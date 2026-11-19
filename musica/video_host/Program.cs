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
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)] static extern uint GetLongPathName(string shortPath, System.Text.StringBuilder longPath, uint size);
    [StructLayout(LayoutKind.Sequential)] struct RECT { public int Left, Top, Right, Bottom; }

    // WebView2 folder mappings want the real long path (no 8.3 «RUNNER~1»).
    static string LongPath(string path)
    {
        var sb = new System.Text.StringBuilder(1024);
        return GetLongPathName(path, sb, (uint)sb.Capacity) > 0 ? sb.ToString() : path;
    }

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
                // Senza questo Chromium blocca l'avvio automatico con audio
                // (play() rifiutato: nessun gesto dell'utente nella pagina).
                var options = new CoreWebView2EnvironmentOptions("--autoplay-policy=no-user-gesture-required");
                var env = await CoreWebView2Environment.CreateAsync(null, dataDir, options);
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
            core.WebMessageReceived += (o, m) =>
            {
                var text = m.TryGetWebMessageAsString();
                if (text != null && text.Contains("\"page\"")) PageReady = true;
                Emit(text);
            };
            // File locali serviti da Lumi con richieste a intervalli (Range):
            // la mappatura cartella di WebView2 non riproduceva i file (MediaError 4).
            core.AddWebResourceRequestedFilter("https://lumi.media/*", CoreWebView2WebResourceContext.All);
            core.WebResourceRequested += (o, r) => ServeMedia(core, r);
            core.NavigationCompleted += (o, n) => Emit("{\"ev\":\"ready\"}");
            core.Navigate("https://lumi.player/player.html");
        };
        var timer = new System.Windows.Forms.Timer { Interval = 300 };
        timer.Tick += (s, e) => { if (!IsWindow(parent)) Application.Exit(); else Fit(form, parent); };
        timer.Start();
        // I comandi arrivano anche mentre WebView2 si sta ancora avviando: si
        // tengono in coda e si eseguono solo quando la pagina del lettore è pronta
        // (prima andavano persi: il primo video dopo l'avvio non partiva).
        var pending = new System.Collections.Concurrent.ConcurrentQueue<string>();
        var quit = false;
        var reader = new Thread(() =>
        {
            string line;
            while ((line = Console.In.ReadLine()) != null)
            {
                if (line.Contains("\"quit\"")) { quit = true; break; }
                pending.Enqueue(line);
            }
            quit = true;
        }) { IsBackground = true };
        var pump = new System.Windows.Forms.Timer { Interval = 80 };
        pump.Tick += (s, e) =>
        {
            if (quit) { pump.Stop(); Application.Exit(); return; }
            var core = web.CoreWebView2;
            if (core == null || !PageReady) return;
            var json = new JavaScriptSerializer();
            while (pending.TryDequeue(out var line))
            {
                string cmd = null; string path = null;
                try
                {
                    var d = json.Deserialize<System.Collections.Generic.Dictionary<string, object>>(line);
                    cmd = d.ContainsKey("cmd") ? d["cmd"] as string : null;
                    path = d.ContainsKey("path") ? d["path"] as string : null;
                }
                catch { continue; }
                if (cmd == "file")
                {
                    if (path == null || !File.Exists(path))
                    {
                        Emit("{\"ev\":\"error\",\"code\":\"missing\"}");
                        continue;
                    }
                    var full = LongPath(Path.GetFullPath(path));
                    CurrentMedia = full;
                    var url = "https://lumi.media/" + Uri.EscapeDataString(Path.GetFileName(full));
                    Emit("{\"ev\":\"debug\",\"url\":" + json.Serialize(url) + "}");
                    core.PostWebMessageAsString(json.Serialize(new { cmd = "file", url = url }));
                }
                else core.PostWebMessageAsString(line);
            }
        };
        pump.Start();
        reader.Start();
        Application.Run(form);
        return 0;
    }

    static string CurrentMedia;
    static volatile bool PageReady;

    static string Mime(string path)
    {
        switch (Path.GetExtension(path).ToLowerInvariant())
        {
            case ".mp4": case ".m4v": return "video/mp4";
            case ".webm": return "video/webm";
            case ".mov": return "video/quicktime";
            case ".mp3": return "audio/mpeg";
            case ".wav": return "audio/wav";
            case ".m4a": return "audio/mp4";
            default: return "application/octet-stream";
        }
    }

    static void ServeMedia(CoreWebView2 core, CoreWebView2WebResourceRequestedEventArgs r)
    {
        var path = CurrentMedia;
        var name = Uri.UnescapeDataString(new Uri(r.Request.Uri).AbsolutePath.TrimStart('/'));
        if (path == null || !File.Exists(path) || !string.Equals(Path.GetFileName(path), name, StringComparison.OrdinalIgnoreCase))
        {
            r.Response = core.Environment.CreateWebResourceResponse(null, 404, "Not Found", "");
            return;
        }
        long length = new FileInfo(path).Length, start = 0, end = length - 1;
        int status = 200;
        string range = null;
        try { range = r.Request.Headers.GetHeader("Range"); } catch { }
        if (!string.IsNullOrEmpty(range) && range.StartsWith("bytes="))
        {
            var parts = range.Substring(6).Split('-');
            if (long.TryParse(parts[0], out var s0)) start = Math.Max(0, Math.Min(s0, length - 1));
            if (parts.Length > 1 && long.TryParse(parts[1], out var e0)) end = Math.Min(e0, length - 1);
            status = 206;
        }
        var count = Math.Max(0, end - start + 1);
        var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        stream.Seek(start, SeekOrigin.Begin);
        var slice = new SliceStream(stream, count);
        var headers = "Content-Type: " + Mime(path) + "\r\nAccept-Ranges: bytes\r\nContent-Length: " + count
            + (status == 206 ? "\r\nContent-Range: bytes " + start + "-" + end + "/" + length : "")
            + "\r\nAccess-Control-Allow-Origin: *";
        r.Response = core.Environment.CreateWebResourceResponse(slice, status, status == 206 ? "Partial Content" : "OK", headers);
    }

    // Legge al massimo «count» byte dalla posizione corrente.
    sealed class SliceStream : Stream
    {
        readonly Stream inner; long left;
        public SliceStream(Stream inner, long count) { this.inner = inner; left = count; }
        public override bool CanRead => true;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => left;
        public override long Position { get => 0; set => throw new NotSupportedException(); }
        public override void Flush() { }
        public override int Read(byte[] buffer, int offset, int count)
        {
            if (left <= 0) return 0;
            int n = inner.Read(buffer, offset, (int)Math.Min(count, left));
            left -= n;
            return n;
        }
        public override long Seek(long o, SeekOrigin k) => throw new NotSupportedException();
        public override void SetLength(long v) => throw new NotSupportedException();
        public override void Write(byte[] b, int o, int c) => throw new NotSupportedException();
        protected override void Dispose(bool disposing) { if (disposing) inner.Dispose(); base.Dispose(disposing); }
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
