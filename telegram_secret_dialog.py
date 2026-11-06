"""Masked, paste-friendly Windows/Tk input for Telegram setup secrets.

Windows console getpass() reads low-level key events. In some cmd hosts
Ctrl+V is ignored, and successful pastes may appear to do nothing because
nothing is echoed. This modal uses a native Tk Entry, where the paste button
reads the clipboard only after the person explicitly clicks it. Secrets
are never printed, logged, included in command-line args, or saved here.
"""
from __future__ import annotations

import tkinter as tk


def secret_length_ok(value: object, minimum: int, maximum: int) -> bool:
    """A simple UI guard, not a secret strength or authentication check."""
    return (isinstance(value, str) and type(minimum) is int
            and type(maximum) is int and 1 <= minimum <= maximum <= 512
            and minimum <= len(value) <= maximum)


def prompt_masked_secret(title: str, description: str, *,
                         min_length: int = 1,
                         max_length: int = 256) -> str | None:
    """Blocking native Windows dialog: Ctrl+V and a visible Incolla button.

    Return None only for Cancel/Escape/window-close. No fallback to getpass:
    that would silently reintroduce the original clipboard problem.
    """
    if (not isinstance(title, str) or not isinstance(description, str)
            or not title or len(title) > 100
            or not description or len(description) > 320
            or type(min_length) is not int or type(max_length) is not int
            or not 1 <= min_length <= max_length <= 512):
        raise ValueError("Parametri finestra segreta non validi.")

    win = tk.Tk()
    from window_chrome import install_window_chrome
    install_window_chrome(win)
    answer: list[str | None] = [None]
    try:
        win.title(title)
        win.geometry("520x230")
        win.minsize(420, 210)
        win.configure(bg="#071421")
        win.resizable(True, False)
        # Bring the prompt above the console on startup. Do not permanently
        # force always-on-top, so the user can return to the browser to copy.
        win.lift()
        try:
            win.attributes("-topmost", True)
            win.after(350, lambda: win.attributes("-topmost", False))
        except tk.TclError:
            pass

        tk.Label(
            win, text=description, anchor="w", justify="left",
            font=("Segoe UI", 10), bg="#071421", fg="#d4f4ff",
            wraplength=470
        ).pack(fill="x", padx=17, pady=(17, 10))

        field = tk.Entry(
            win, show="*", font=("Consolas", 13), width=48,
            bg="#102a3d", fg="white", insertbackground="white",
            relief="solid", bd=1
        )
        field.pack(fill="x", padx=17, ipady=7)

        status = tk.StringVar(
            value="Puoi usare Ctrl+V oppure premere Incolla.")
        tk.Label(
            win, textvariable=status, bg="#071421", fg="#90bfd5",
            anchor="w", font=("Segoe UI", 9)
        ).pack(fill="x", padx=17, pady=(7, 6))

        row = tk.Frame(win, bg="#071421")
        row.pack(fill="x", padx=17)

        def paste() -> None:
            # Clipboard is accessed only on an intentional user click.
            try:
                pasted = win.clipboard_get()
            except tk.TclError:
                status.set("Appunti vuoti o non contenenti testo.")
                return
            if not isinstance(pasted, str) or not pasted:
                status.set("Nessun testo trovato negli appunti.")
                return
            if len(pasted) > max_length:
                status.set("Testo troppo lungo: controlla cosa hai copiato.")
                return
            field.insert(tk.INSERT, pasted)
            status.set("Testo incollato. Ora premi Conferma.")
            field.focus_set()

        def confirm(_event=None) -> None:
            value = field.get()
            if not secret_length_ok(value, min_length, max_length):
                status.set(
                    f"Il campo deve contenere da {min_length} "
                    f"a {max_length} caratteri.")
                return
            answer[0] = value
            win.destroy()

        def cancel(_event=None) -> None:
            answer[0] = None
            win.destroy()

        tk.Button(
            row, text="Incolla", command=paste, cursor="hand2",
            bg="#12415b", fg="white", activebackground="#196989",
            activeforeground="white", width=12, bd=0
        ).pack(side="left", padx=(0, 7), ipady=5)
        tk.Button(
            row, text="Cancella", command=lambda: field.delete(0, "end"),
            cursor="hand2", bg="#142737", fg="white",
            activebackground="#264354", activeforeground="white",
            width=9, bd=0
        ).pack(side="left", ipady=5)
        tk.Button(
            row, text="Conferma", command=confirm, cursor="hand2",
            bg="#075b7b", fg="white", activebackground="#1081a9",
            activeforeground="white", width=12, bd=0
        ).pack(side="right", ipady=5)

        win.bind("<Return>", confirm)
        win.bind("<Escape>", cancel)
        win.protocol("WM_DELETE_WINDOW", cancel)
        win.after(100, field.focus_force)
        win.mainloop()
        return answer[0]
    finally:
        # Destroy only when still alive (the callbacks already destroy it).
        try:
            if win.winfo_exists():
                win.destroy()
        except tk.TclError:
            pass
