// LumiControl: elenca gli elementi utilizzabili di una finestra (UI Automation).
// Uso: LumiControl.exe list <hwnd> [max] | focused | ocr <hwnd> | play <hwnd>
// Stampa una riga JSON: {"ok":true,"items":[{"name","type","x","y","w","h","enabled","id"}]}
// Solo lettura: non clicca e non scrive nulla (lo fa Lumi, dopo le conferme).
using System;
using System.Collections.Generic;
using System.Windows.Automation;
using System.Web.Script.Serialization;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;

static class Program
{
    static readonly ControlType[] Useful = {
        ControlType.Button, ControlType.Edit, ControlType.Hyperlink, ControlType.MenuItem,
        ControlType.ListItem, ControlType.TabItem, ControlType.CheckBox, ControlType.RadioButton,
        ControlType.ComboBox, ControlType.Document, ControlType.SplitButton, ControlType.TreeItem,
        ControlType.DataItem, ControlType.Spinner, ControlType.Slider, ControlType.MenuBar,
    };

    // Nome, tipo e rettangolo di un elemento (null se senza dimensioni).
    static Dictionary<string, object> Describe(AutomationElement el)
    {
        var c = el.Current;
        var r = c.BoundingRectangle;
        if (r.IsEmpty || r.Width < 2 || r.Height < 2) return null;
        string name = c.Name ?? "";
        if (name.Length == 0) name = c.HelpText ?? "";
        return new Dictionary<string, object> {
            {"name", name.Length > 200 ? name.Substring(0, 200) : name},
            {"type", c.ControlType.ProgrammaticName.Replace("ControlType.", "")},
            {"x", (int)r.X}, {"y", (int)r.Y}, {"w", (int)r.Width}, {"h", (int)r.Height},
            {"enabled", c.IsEnabled},
            {"id", c.AutomationId ?? ""},
        };
    }

    [StructLayout(LayoutKind.Sequential)]
    struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    static Bitmap Capture(IntPtr hwnd, out RECT rect)
    {
        if (!GetWindowRect(hwnd, out rect)) throw new InvalidOperationException("finestra non trovata");
        int w = Math.Max(1, rect.Right - rect.Left), h = Math.Max(1, rect.Bottom - rect.Top);
        var bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb);
        using (var g = Graphics.FromImage(bmp))
            g.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(w, h));
        return bmp;
    }

    // Scritte visibili nella finestra con l'OCR integrato di Windows 10 (offline).
    // Le parole di una riga vengono divise in gruppi quando c'è molto spazio tra loro
    // (es. le voci di un menu in alto), così ogni gruppo ha il suo numero.
    static List<Dictionary<string, object>> Ocr(IntPtr hwnd)
    {
        RECT rect;
        var items = new List<Dictionary<string, object>>();
        using (var bmp = Capture(hwnd, out rect))
        using (var ms = new MemoryStream())
        {
            bmp.Save(ms, ImageFormat.Png);
            var stream = new Windows.Storage.Streams.InMemoryRandomAccessStream();
            using (var writer = new Windows.Storage.Streams.DataWriter(stream.GetOutputStreamAt(0)))
            {
                writer.WriteBytes(ms.ToArray());
                writer.StoreAsync().AsTask().Wait();
            }
            var decoder = Windows.Graphics.Imaging.BitmapDecoder.CreateAsync(stream).AsTask().Result;
            var soft = decoder.GetSoftwareBitmapAsync(Windows.Graphics.Imaging.BitmapPixelFormat.Bgra8,
                Windows.Graphics.Imaging.BitmapAlphaMode.Premultiplied).AsTask().Result;
            var engine = Windows.Media.Ocr.OcrEngine.TryCreateFromLanguage(new Windows.Globalization.Language("it"))
                         ?? Windows.Media.Ocr.OcrEngine.TryCreateFromUserProfileLanguages();
            if (engine == null) throw new InvalidOperationException("OCR di Windows non disponibile (lingua mancante)");
            var result = engine.RecognizeAsync(soft).AsTask().Result;
            foreach (var line in result.Lines)
            {
                var words = line.Words.ToList();
                int start = 0;
                for (int i = 1; i <= words.Count; i++)
                {
                    bool split = i == words.Count;
                    if (!split)
                    {
                        var a = words[i - 1].BoundingRect; var b = words[i].BoundingRect;
                        split = b.X - (a.X + a.Width) > Math.Max(14, a.Height * 1.6);
                    }
                    if (!split) continue;
                    var group = words.Skip(start).Take(i - start).ToList();
                    double x0 = group.Min(w => w.BoundingRect.X), y0 = group.Min(w => w.BoundingRect.Y);
                    double x1 = group.Max(w => w.BoundingRect.X + w.BoundingRect.Width);
                    double y1 = group.Max(w => w.BoundingRect.Y + w.BoundingRect.Height);
                    items.Add(new Dictionary<string, object> {
                        {"name", string.Join(" ", group.Select(w => w.Text))}, {"type", "Text"},
                        {"x", rect.Left + (int)x0}, {"y", rect.Top + (int)y0},
                        {"w", (int)(x1 - x0)}, {"h", (int)(y1 - y0)}, {"enabled", true}, {"id", "ocr"} });
                    start = i;
                    if (items.Count >= 300) return items;
                }
            }
        }
        return items;
    }

    // Pulsanti «play» disegnati: cerchio chiaro (quasi bianco) con un triangolo scuro
    // al centro. Analisi dei pixel, nessun modello.
    static List<Dictionary<string, object>> PlayButtons(IntPtr hwnd)
    {
        RECT rect;
        var items = new List<Dictionary<string, object>>();
        using (var bmp = Capture(hwnd, out rect))
        {
            int step = 2, W = bmp.Width / step, H = bmp.Height / step;
            var light = new bool[W, H];
            var data = bmp.LockBits(new Rectangle(0, 0, bmp.Width, bmp.Height), ImageLockMode.ReadOnly,
                                    PixelFormat.Format32bppArgb);
            var buffer = new byte[data.Stride * bmp.Height];
            Marshal.Copy(data.Scan0, buffer, 0, buffer.Length);
            bmp.UnlockBits(data);
            Func<int, int, int> lum = (px, py) => {
                int o = py * data.Stride + px * 4;
                return (buffer[o] + buffer[o + 1] + buffer[o + 2]) / 3;
            };
            for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) light[x, y] = lum(x * step, y * step) > 215;
            var seen = new bool[W, H];
            var queue = new Queue<int>();
            for (int sy = 0; sy < H; sy++) for (int sx = 0; sx < W; sx++)
            {
                if (!light[sx, sy] || seen[sx, sy]) continue;
                int minx = sx, maxx = sx, miny = sy, maxy = sy, count = 0;
                queue.Enqueue(sy * W + sx); seen[sx, sy] = true;
                while (queue.Count > 0)
                {
                    int v = queue.Dequeue(), x = v % W, y = v / W; count++;
                    if (x < minx) minx = x; if (x > maxx) maxx = x; if (y < miny) miny = y; if (y > maxy) maxy = y;
                    if (x > 0 && light[x - 1, y] && !seen[x - 1, y]) { seen[x - 1, y] = true; queue.Enqueue(v - 1); }
                    if (x < W - 1 && light[x + 1, y] && !seen[x + 1, y]) { seen[x + 1, y] = true; queue.Enqueue(v + 1); }
                    if (y > 0 && light[x, y - 1] && !seen[x, y - 1]) { seen[x, y - 1] = true; queue.Enqueue(v - W); }
                    if (y < H - 1 && light[x, y + 1] && !seen[x, y + 1]) { seen[x, y + 1] = true; queue.Enqueue(v + W); }
                }
                int bw = maxx - minx + 1, bh = maxy - miny + 1;
                if (bw < 10 || bh < 10 || bw > 45 || bh > 45) continue;          // 20–90 px
                double aspect = (double)bw / bh, fill = (double)count / (bw * bh);
                if (aspect < 0.8 || aspect > 1.25 || fill < 0.4 || fill > 0.82) continue;
                int cx = (minx + maxx) / 2, cy = (miny + maxy) / 2;
                if (light[cx, cy]) continue;                                    // centro scuro: triangolo
                items.Add(new Dictionary<string, object> {
                    {"name", "play"}, {"type", "PlayShape"},
                    {"x", rect.Left + minx * step}, {"y", rect.Top + miny * step},
                    {"w", bw * step}, {"h", bh * step}, {"enabled", true}, {"id", "shape"} });
                if (items.Count >= 20) return items;
            }
        }
        return items;
    }

    static int Main(string[] args)
    {
        var json = new JavaScriptSerializer();
        try
        {
            if (args.Length >= 2 && (args[0] == "ocr" || args[0] == "play"))
            {
                var handle = new IntPtr(long.Parse(args[1]));
                var read = args[0] == "ocr" ? Ocr(handle) : PlayButtons(handle);
                Console.Out.WriteLine(json.Serialize(new Dictionary<string, object> {
                    {"ok", true}, {"items", read} }));
                return 0;
            }
            if (args.Length >= 1 && args[0] == "focused")
            {
                var f = AutomationElement.FocusedElement;
                object item = null;
                if (f != null) item = Describe(f);
                Console.Out.WriteLine(json.Serialize(new Dictionary<string, object> {
                    {"ok", true}, {"item", item} }));
                return 0;
            }
            if (args.Length < 2 || args[0] != "list")
                throw new ArgumentException("uso: list <hwnd> [max] | focused");
            var hwnd = new IntPtr(long.Parse(args[1]));
            int max = args.Length > 2 ? Math.Min(int.Parse(args[2]), 1000) : 400;
            var root = AutomationElement.FromHandle(hwnd);
            var types = new List<Condition>();
            foreach (var t in Useful)
                types.Add(new PropertyCondition(AutomationElement.ControlTypeProperty, t));
            var condition = new AndCondition(
                new OrCondition(types.ToArray()),
                new PropertyCondition(AutomationElement.IsOffscreenProperty, false));
            var found = root.FindAll(TreeScope.Descendants, condition);
            var items = new List<Dictionary<string, object>>();
            foreach (AutomationElement el in found)
            {
                if (items.Count >= max) break;
                try
                {
                    var d = Describe(el);
                    if (d != null) items.Add(d);
                }
                catch (ElementNotAvailableException) { }
            }
            Console.Out.WriteLine(json.Serialize(new Dictionary<string, object> {
                {"ok", true}, {"items", items} }));
            return 0;
        }
        catch (Exception ex)
        {
            Console.Out.WriteLine(json.Serialize(new Dictionary<string, object> {
                {"ok", false}, {"error", ex.GetType().Name + ": " + ex.Message} }));
            return 1;
        }
    }
}
