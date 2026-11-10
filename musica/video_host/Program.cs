// LumiVideo: riquadro video di Lumi (WebView2) incorporato nella finestra di Lumi.
// Uso: LumiVideo.exe <hwnd_genitore> <cartella_dati_webview2>
// Comandi JSON su stdin (una riga ciascuno), eventi JSON su stdout.
using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

static class Program
{
    [DllImport("user32.dll")] static extern IntPtr SetParent(IntPtr child, IntPtr parent);
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] static extern bool IsWindow(IntPtr hWnd);
    [DllImport("user32.dll")] static extern int SetWindowLong(IntPtr hWnd, int index, int value);
    [DllImport("user32.dll")] static extern int GetWindowLong(IntPtr hWnd, int index);
    [StructLayout(LayoutKind.Sequential)] struct RECT { public int Left, Top, Right, Bottom; }

    static readonly object OutLock = new object();
    static void Emit(string json) { lock (OutLock) { Console.Out.WriteLine(json); Console.Out.Flush(); } }

    [STAThread]
    static int Main(string[] args)
    {
        if (args.Length < 2) return 2;
        var parent = new IntPtr(long.Parse(args[0]));
        var dataDir = args[1];
        Application.EnableVisualStyles();
        var form = new Form { FormBorderStyle = FormBorderStyle.None, ShowInTaskbar = false,
                              StartPosition = FormStartPosition.Manual, BackColor = System.Drawing.Color.Black };
        var web = new WebView2 { Dock = DockStyle.Fill };
        form.Controls.Add(web);
        form.Load += async (s, e) =>
        {
            // Figlia della finestra di Lumi: si muove e si chiude con lei.
            const int GWL_STYLE = -16, WS_CHILD = 0x40000000, WS_POPUP = unchecked((int)0x80000000);
            SetWindowLong(form.Handle, GWL_STYLE, (GetWindowLong(form.Handle, GWL_STYLE) | WS_CHILD) & ~WS_POPUP);
            SetParent(form.Handle, parent);
            Fit(form, parent);
            try
            {
                var env = await CoreWebView2Environment.CreateAsync(null, dataDir);
                await web.EnsureCoreWebView2Async(env);
            }
            catch (Exception ex)
            {
                Emit("{\"ev\":\"error\",\"code\":\"webview2\",\"detail\":" + new JavaScriptSerializer().Serialize(ex.GetType().Name) + "}");
                Application.Exit();
                return;
            }
            var core = web.CoreWebView2;
            core.Settings.AreDevToolsEnabled = false;
            core.Settings.AreDefaultContextMenusEnabled = false;
            core.Settings.IsStatusBarEnabled = false;
            var pageDir = Path.Combine(dataDir, "page");
            Directory.CreateDirectory(pageDir);
            using (var res = Assembly.GetExecutingAssembly().GetManifestResourceStream("player.html"))
            using (var fs = File.Create(Path.Combine(pageDir, "player.html"))) res.CopyTo(fs);
            core.SetVirtualHostNameToFolderMapping("lumi.player", pageDir, CoreWebView2HostResourceAccessKind.DenyCors);
            core.WebMessageReceived += (o, m) => Emit(m.TryGetWebMessageAsString());
            core.NavigationCompleted += (o, n) => Emit("{\"ev\":\"ready\"}");
            core.Navigate("https://lumi.player/player.html");
        };
        var timer = new System.Windows.Forms.Timer { Interval = 300 };
        timer.Tick += (s, e) => { if (!IsWindow(parent)) Application.Exit(); else Fit(form, parent); };
        timer.Start();
        var reader = new Thread(() =>
        {
            var json = new JavaScriptSerializer();
            string line;
            while ((line = Console.In.ReadLine()) != null)
            {
                string cmd = null; string path = null;
                try
                {
                    var d = json.Deserialize<System.Collections.Generic.Dictionary<string, object>>(line);
                    cmd = d.ContainsKey("cmd") ? d["cmd"] as string : null;
                    path = d.ContainsKey("path") ? d["path"] as string : null;
                }
                catch { continue; }
                if (cmd == "quit") break;
                var copy = line;
                form.BeginInvoke((Action)(() =>
                {
                    var core = web.CoreWebView2;
                    if (core == null) return;
                    if (cmd == "file" && path != null && File.Exists(path))
                    {
                        // La cartella del file diventa https://lumi.media/ solo per questo brano.
                        core.SetVirtualHostNameToFolderMapping("lumi.media", Path.GetDirectoryName(path), CoreWebView2HostResourceAccessKind.Allow);
                        var url = "https://lumi.media/" + Uri.EscapeDataString(Path.GetFileName(path));
                        core.PostWebMessageAsString(json.Serialize(new { cmd = "file", url = url }));
                    }
                    else core.PostWebMessageAsString(copy);
                }));
            }
            form.BeginInvoke((Action)(() => Application.Exit()));
        }) { IsBackground = true };
        reader.Start();
        Application.Run(form);
        return 0;
    }

    static void Fit(Form form, IntPtr parent)
    {
        if (GetClientRect(parent, out RECT r))
        {
            int w = Math.Max(1, r.Right - r.Left), h = Math.Max(1, r.Bottom - r.Top);
            if (form.Left != 0 || form.Top != 0 || form.Width != w || form.Height != h)
                form.SetBounds(0, 0, w, h);
        }
    }
}
