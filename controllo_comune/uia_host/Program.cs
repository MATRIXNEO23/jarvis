// LumiControl: elenca gli elementi utilizzabili di una finestra (UI Automation).
// Uso: LumiControl.exe list <hwnd> [max]  |  LumiControl.exe focused
// Stampa una riga JSON: {"ok":true,"items":[{"name","type","x","y","w","h","enabled","id"}]}
// Solo lettura: non clicca e non scrive nulla (lo fa Lumi, dopo le conferme).
using System;
using System.Collections.Generic;
using System.Windows.Automation;
using System.Web.Script.Serialization;

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

    static int Main(string[] args)
    {
        var json = new JavaScriptSerializer();
        try
        {
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
