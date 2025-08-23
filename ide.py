import io
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from src.lexer import Lexer
from src.parser import Parser, ParserError
from src.interpreter import Interpreter, RuntimeErrorEx

# ---- VS Code Dark+ colors ----
COL_BG        = "#1e1e1e"
COL_EDITOR    = "#1e1e1e"
COL_GUTTER    = "#252526"
COL_BORDER    = "#333333"
COL_TEXT      = "#d4d4d4"
COL_SELECTION = "#264f78"
COL_CURSOR    = "#ffffff"
COL_GUTTER_TEXT = "#858585"
COL_STATUS_BG   = "#007acc"
COL_STATUS_FG   = "#ffffff"

# Syntax
COL_KEYWORD   = "#c586c0"
COL_NUMBER    = "#4fc1ff"
COL_STRING    = "#ce9178"
COL_COMMENT   = "#6a9955"
COL_OPERATOR  = "#dcdcaa"
COL_PAREN     = "#9cdcfe"

KEYWORDS = ["fff", "if", "else", "while", "print", "true", "false"]

class DamavandIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Damavand IDE — Dark+")
        self.filename = None

        root.configure(bg=COL_BG)

        # Menu
        menubar = tk.Menu(root, tearoff=0, bg=COL_BG, fg=COL_TEXT,
                          activebackground=COL_GUTTER, activeforeground=COL_TEXT)

        filemenu = tk.Menu(menubar, tearoff=0, bg=COL_BG, fg=COL_TEXT,
                           activebackground=COL_GUTTER, activeforeground=COL_TEXT)
        filemenu.add_command(label="New  Ctrl+N", command=self.new_file)
        filemenu.add_command(label="Open Ctrl+O", command=self.open_file, accelerator="Ctrl+O")
        filemenu.add_command(label="Save Ctrl+S", command=self.save_file, accelerator="Ctrl+S")
        filemenu.add_command(label="Save As…", command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.safe_exit)
        menubar.add_cascade(label="File", menu=filemenu)

        runmenu = tk.Menu(menubar, tearoff=0, bg=COL_BG, fg=COL_TEXT,
                          activebackground=COL_GUTTER, activeforeground=COL_TEXT)
        runmenu.add_command(label="▶ Run   F5", command=self.run_code, accelerator="F5")
        menubar.add_cascade(label="Run", menu=runmenu)

        root.config(menu=menubar)

        # Top area: gutter + editor + scrollbar
        top_frame = tk.Frame(root, bg=COL_BG, bd=0, highlightthickness=0)
        top_frame.pack(fill=tk.BOTH, expand=True)

        editor_container = tk.Frame(top_frame, bg=COL_BG)
        editor_container.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(editor_container, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.gutter = tk.Text(editor_container, width=6, padx=6, takefocus=0,
                              bg=COL_GUTTER, fg=COL_GUTTER_TEXT, bd=0, highlightthickness=0,
                              state="disabled")
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)

        self.editor = tk.Text(editor_container, wrap="none", font=("Consolas", 12),
                              bg=COL_EDITOR, fg=COL_TEXT, insertbackground=COL_CURSOR,
                              selectbackground=COL_SELECTION, undo=True, bd=0,
                              highlightthickness=0, yscrollcommand=self._on_editor_scroll)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self._on_scrollbar)

        sep = tk.Frame(root, height=1, bg=COL_BORDER, bd=0, highlightthickness=0)
        sep.pack(fill=tk.X)

        console_container = tk.Frame(root, bg=COL_BG)
        console_container.pack(fill=tk.BOTH, side=tk.BOTTOM)

        self.console = tk.Text(console_container, wrap="word", height=10, font=("Consolas", 12),
                               bg=COL_EDITOR, fg=COL_TEXT, insertbackground=COL_CURSOR,
                               selectbackground=COL_SELECTION, bd=0, highlightthickness=0)
        self.console.pack(fill=tk.BOTH, expand=False)

        status = tk.Frame(root, bg=COL_BORDER, height=1)
        status.pack(fill=tk.X)
        self.statusbar = tk.Label(root, text="Ready", anchor="w", bg=COL_STATUS_BG,
                                  fg=COL_STATUS_FG, padx=8)
        self.statusbar.pack(fill=tk.X)

        self._init_tags()

        # Bindings
        self.editor.bind("<KeyRelease>", self._on_change)
        self.editor.bind("<ButtonRelease-1>", self._update_status)
        self.editor.bind("<Motion>", self._update_status)
        self.editor.bind("<<Modified>>", self._on_modified)
        root.bind_all("<Control-o>", lambda e: self.open_file())
        root.bind_all("<Control-s>", lambda e: self.save_file())
        root.bind_all("<Control-n>", lambda e: self.new_file())
        root.bind_all("<F5>",       lambda e: self.run_code())

        self._update_gutter()
        self.highlight()
        self._update_status()

    # --- tags ---
    def _init_tags(self):
        self.editor.tag_configure("kw", foreground=COL_KEYWORD)
        self.editor.tag_configure("num", foreground=COL_NUMBER)
        self.editor.tag_configure("str", foreground=COL_STRING)
        self.editor.tag_configure("com", foreground=COL_COMMENT, font=("Consolas", 12, "italic"))
        self.editor.tag_configure("op", foreground=COL_OPERATOR)
        self.editor.tag_configure("par", foreground=COL_PAREN)
        # ensure comments sit on top
        self.editor.tag_raise("com")


    # --- scroll sync ---
    def _on_editor_scroll(self, *args):
        self.scrollbar.set(*args)
        self.gutter.yview_moveto(args[0])

    def _on_scrollbar(self, *args):
        self.editor.yview(*args)
        self.gutter.yview(*args)

    # --- gutter ---
    def _update_gutter(self):
        self.gutter.config(state="normal")
        self.gutter.delete("1.0", "end")
        last_line = int(self.editor.index("end-1c").split(".")[0])
        self.gutter.insert("1.0", "\n".join(str(i) for i in range(1, last_line + 1)))
        self.gutter.config(state="disabled")

    def _on_modified(self, _=None):
        self.editor.tk.call(self.editor._w, 'edit', 'modified', 0)
        self._update_gutter()
        self._update_status()

    def _on_change(self, _=None):
        self.highlight()
        self._update_gutter()
        self._update_status()

    # --- status ---
    def _update_status(self, _=None):
        idx = self.editor.index("insert")
        line, col = idx.split(".")
        name = self.filename if self.filename else "Untitled"
        self.statusbar.config(text=f"{name}   Ln {line}, Col {int(col)+1}")

    # ---------- robust highlighter (comments override everything) ----------
    def clear_tags(self):
        for tag in ["kw", "num", "str", "com", "op", "par"]:
            self.editor.tag_remove(tag, "1.0", "end")

    def highlight(self):
        content = self.editor.get("1.0", "end-1c")
        self.clear_tags()

        # 1) Compute string spans (both ' and ", honoring escapes)
        string_spans = self._find_string_spans(content)

        # 2) Compute comment spans (# ... end-of-line), but ONLY outside strings
        comment_spans = self._find_comment_spans(content, string_spans)

        # Paint comments first and keep them above others
        for s, e in comment_spans:
            self._tag_abs_range("com", s, e)

        # 3) Paint strings
        for s, e in string_spans:
            self._tag_abs_range("str", s, e)

        # 4) Other categories, excluding string+comment spans
        protected = self._merge_spans(string_spans + comment_spans)

        import re
        # keywords
        kw_pattern = r"\b(" + "|".join(map(re.escape, KEYWORDS)) + r")\b"
        for m in re.finditer(kw_pattern, content):
            self._tag_abs_range_excluding("kw", m.start(), m.end(), protected)

        # numbers (ints & floats)
        for m in re.finditer(r"\b\d+(\.\d+)?\b", content):
            self._tag_abs_range_excluding("num", m.start(), m.end(), protected)

        # operators (including '=' and '!' forms)
        for m in re.finditer(r"==|!=|<=|>=|[=+\-*/%<>!]", content):
            self._tag_abs_range_excluding("op", m.start(), m.end(), protected)

        # parens/braces/brackets
        for m in re.finditer(r"[\(\)\{\}\[\]]", content):
            self._tag_abs_range_excluding("par", m.start(), m.end(), protected)

        # make sure comments always on top visually
        self.editor.tag_raise("com")

    # ---- span helpers ----
    def _find_string_spans(self, text):
        spans = []
        i, n = 0, len(text)
        in_str = False
        quote = None
        start = 0
        while i < n:
            c = text[i]
            if not in_str:
                if c in ("'", '"'):
                    in_str = True
                    quote = c
                    start = i
                i += 1
            else:
                if c == "\\":
                    i += 2  # skip escaped char
                    continue
                if c == quote:
                    spans.append((start, i + 1))  # include closing quote
                    in_str = False
                    quote = None
                    i += 1
                else:
                    i += 1
        # unclosed string: color until EOL or end
        if in_str:
            spans.append((start, n))
        return spans

    def _find_comment_spans(self, text, string_spans):
        # Build quick mask for "inside-string"
        in_string = [False] * (len(text) + 1)
        for s, e in string_spans:
            for k in range(s, e):
                if 0 <= k < len(in_string):
                    in_string[k] = True

        spans = []
        i, n = 0, len(text)
        while i < n:
            if text[i] == "#" and not in_string[i]:
                # comment runs to end of line
                j = i
                while j < n and text[j] != "\n":
                    j += 1
                spans.append((i, j))
                i = j
            else:
                i += 1
        return spans

    def _merge_spans(self, spans):
        if not spans:
            return []
        spans = sorted(spans)
        merged = [list(spans[0])]
        for s, e in spans[1:]:
            if s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        return [(a, b) for a, b in merged]

    def _overlaps(self, spans, a, b):
        # any overlap with [a,b)
        for s, e in spans:
            if not (b <= s or a >= e):
                return True
        return False

    def _tag_abs_range(self, tag, abs_start, abs_end):
        start = f"1.0+{abs_start}c"
        end   = f"1.0+{abs_end}c"
        self.editor.tag_add(tag, start, end)

    def _tag_abs_range_excluding(self, tag, abs_start, abs_end, excluded_spans):
        # Skip adding if overlaps any protected span
        if self._overlaps(excluded_spans, abs_start, abs_end):
            return
        self._tag_abs_range(tag, abs_start, abs_end)

    # --- file ops ---
    def new_file(self):
        self.filename = None
        self.editor.delete("1.0", "end")
        self.console.delete("1.0", "end")
        self._update_status()

    def open_file(self):
        fn = filedialog.askopenfilename(
            filetypes=[("Damavand files", "*.dam"), ("All files", "*.*")]
        )
        if not fn:
            return
        try:
            with open(fn, "r", encoding="utf-8") as f:
                text = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", text)
            self.filename = fn
            self.console.delete("1.0", "end")
            self.console.insert("end", f"Opened: {self.filename}\n")
            self.highlight()
            self._update_gutter()
            self._update_status()
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def save_file(self):
        if not self.filename:
            return self.save_as()
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))
            self.console.insert("end", f"Saved: {self.filename}\n")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def save_as(self):
        fn = filedialog.asksaveasfilename(
            defaultextension=".dam",
            filetypes=[("Damavand files", "*.dam"), ("All files", "*.*")],
        )
        if not fn:
            return
        self.filename = fn
        self.save_file()

    def safe_exit(self):
        self.root.quit()

    # --- run ---
    def run_code(self):
        code = self.editor.get("1.0", "end-1c")
        self.console.delete("1.0", "end")

        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = io.StringIO()

        try:
            tokens = Lexer(code).tokenize()
            ast = Parser(tokens).parse()
            Interpreter().run(ast)
        except (SyntaxError, ParserError, RuntimeErrorEx, Exception) as e:
            print(f"[IDE Error] {e}")
        output = sys.stdout.getvalue()

        sys.stdout, sys.stderr = old_out, old_err

        self.console.insert("end", output)
        self.highlight()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700+100+60")
    app = DamavandIDE(root)
    root.mainloop()
