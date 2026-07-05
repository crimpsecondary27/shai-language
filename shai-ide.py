import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import webbrowser
import tempfile
import json

TAG_NAMES = [
    "directive", "arabic_directive", "attribute", "comment",
    "string", "header", "title_cmd", "style_cmd", "body_cmd",
    "button_cmd", "list_cmd", "paragraph", "tag_cmd"
]

ARABIC_COMMANDS = {
    "@نص": "title",
    "@مسار": "style",
    "@جسم": "body",
    "@ر1": "h1",
    "@ر2": "h2",
    "@ر3": "h3",
    "@ر4": "h4",
    "@ر5": "h5",
    "@ر6": "h6",
    "@عنوان1": "h1",
    "@فقرة": "p",
    "@قائمة": "ul",
    "@قائمة-غير-مرقمة": "ul",
    "@عنصر": "li",
    "@عنصر-قائمة": "li",
    "@زر": "button",
    "@جدول": "table",
    "@رأس-جدول": "thead",
    "@صف-جدول": "tr",
    "@رأس-خلية": "th",
    "@جسم-جدول": "tbody",
    "@خلية-جدول": "td",
    "@نموذج": "form",
    "@تسمية": "label",
    "@إدخال": "input",
    "@فيديو": "video",
    "@مصدر": "source",
    "@قسم": "div",
    "@نطاق": "span",
    "@رابط": "a",
    "@صورة": "img",
    "@سطر-جديد": "br",
    "@خط-فاصل": "hr",
    "@غامق": "strong",
    "@مائل": "em",
    "@صغير": "small",
    "@مسبق": "pre",
    "@كود": "code",
    "@اقتباس": "blockquote",
    "@تنقل": "nav",
    "@ترويسة": "header",
    "@تذييل": "footer",
    "@فصل": "section",
    "@مقال": "article",
    "@جانب": "aside",
    "@رئيسي": "main",
    "@شكل": "figure",
    "@تسمية-شكل": "figcaption",
    "@منطقة-نص": "textarea",
    "@قائمة-منسدلة": "select",
    "@خيار": "option",
}

ENGLISH_COMMANDS = {
    "@title": "title",
    "@style": "style",
    "@body": "body",
    "@h1": "h1",
    "@h2": "h2",
    "@h3": "h3",
    "@h4": "h4",
    "@h5": "h5",
    "@h6": "h6",
    "@p": "p",
    "@ul": "ul",
    "@li": "li",
    "@button": "button",
    "@table": "table",
    "@thead": "thead",
    "@tr": "tr",
    "@th": "th",
    "@tbody": "tbody",
    "@td": "td",
    "@form": "form",
    "@label": "label",
    "@input": "input",
    "@video": "video",
    "@source": "source",
    "@div": "div",
    "@span": "span",
    "@a": "a",
    "@img": "img",
    "@br": "br",
    "@hr": "hr",
    "@strong": "strong",
    "@em": "em",
    "@small": "small",
    "@pre": "pre",
    "@code": "code",
    "@blockquote": "blockquote",
    "@nav": "nav",
    "@header": "header",
    "@footer": "footer",
    "@section": "section",
    "@article": "article",
    "@aside": "aside",
    "@main": "main",
    "@figure": "figure",
    "@figcaption": "figcaption",
    "@textarea": "textarea",
    "@select": "select",
    "@option": "option",
}

ALL_COMMANDS = {**ARABIC_COMMANDS, **ENGLISH_COMMANDS}
HEADER_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
VOID_TAGS = {"br", "hr", "img"}
GENERIC_TAGS = {
    "div", "span", "a", "strong", "em", "small", "pre", "code",
    "blockquote", "nav", "header", "footer", "section", "article",
    "aside", "main", "figure", "figcaption", "textarea", "select", "option"
}
BODY_MARKERS = {"@body", "@جسم"}

HIGHLIGHT_GROUPS = (
    ("header", ("@h1", "@h2", "@h3", "@h4", "@h5", "@h6",
                "@ر1", "@ر2", "@ر3", "@ر4", "@ر5", "@ر6")),
    ("title_cmd", ("@title", "@نص")),
    ("style_cmd", ("@style", "@مسار")),
    ("body_cmd", ("@body", "@جسم")),
    ("button_cmd", ("@button", "@زر")),
    ("list_cmd", ("@ul", "@li", "@قائمة", "@عنصر")),
    ("paragraph", ("@p", "@فقرة")),
    ("tag_cmd", (
        "@div", "@span", "@a", "@img", "@br", "@hr", "@strong", "@em",
        "@small", "@pre", "@code", "@blockquote", "@nav", "@header",
        "@footer", "@section", "@article", "@aside", "@main", "@figure",
        "@figcaption", "@textarea", "@select", "@option",
        "@قسم", "@نطاق", "@رابط", "@صورة", "@سطر-جديد", "@خط-فاصل",
        "@غامق", "@مائل", "@صغير", "@مسبق", "@كود", "@اقتباس", "@تنقل",
        "@ترويسة", "@تذييل", "@فصل", "@مقال", "@جانب", "@رئيسي",
        "@شكل", "@تسمية-شكل", "@منطقة-نص", "@قائمة-منسدلة", "@خيار"
    )),
)

LARGE_FILE_CHAR_THRESHOLD = 400000
LARGE_FILE_LINE_THRESHOLD = 15000

STYLE_BLOCK = """  <style>
    body {
      font-family: Arial, sans-serif;
      background: white;
      color: black;
      padding: 30px;
      max-width: 900px;
      margin: 0 auto;
    }
    h1, h2, h3, h4, h5, h6 { color: black; }
    p { line-height: 1.6; margin: 12px 0; color: black; }
    a { color: blue; }
    ul { padding-left: 30px; }
    li { margin: 6px 0; }
    table { border-collapse: collapse; margin: 15px 0; }
    th, td { border: 1px solid black; padding: 8px; }
    th { background: white; font-weight: bold; }
    form { margin: 15px 0; }
    label { display: block; margin: 8px 0 4px; }
    input, textarea, select {
      border: 1px solid black;
      padding: 6px;
      margin-bottom: 10px;
      background: white;
      color: black;
    }
    button {
      background: white;
      color: black;
      border: 1px solid black;
      padding: 8px 16px;
      cursor: pointer;
    }
    button:hover { background: black; color: white; }
    pre, code { background: white; border: 1px solid black; padding: 8px; }
    blockquote { border-left: 3px solid black; padding-left: 12px; color: black; }
    hr { border: none; border-top: 1px solid black; }
  </style>"""


CANVAS_SUPPORTED_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "br", "hr", "button"
}


def compile_shai_canvas(shai_code):
    ops = []
    title = "Shai Page"
    y = 40
    x = 40

    def add_text(text, size, bold):
        nonlocal y
        weight = "bold" if bold else "normal"
        ops.append({
            "type": "text",
            "x": x,
            "y": y,
            "text": text,
            "font": f"{weight} {size}px Arial"
        })
        y += int(size * 1.5)

    for raw_line in shai_code.split("\n"):
        line = raw_line.strip()

        if not line or line.startswith("#") or line in BODY_MARKERS:
            continue

        command, content, attrs = extract_command(line)

        if command in ("@title", "@نص"):
            title = content
            continue

        if command in ("@style", "@مسار"):
            continue

        tag = ALL_COMMANDS.get(command)

        if tag is None:
            add_text(line, 16, False)
            continue

        if tag == "h1":
            add_text(content, 32, True)
        elif tag == "h2":
            add_text(content, 26, True)
        elif tag == "h3":
            add_text(content, 22, True)
        elif tag == "h4":
            add_text(content, 18, True)
        elif tag == "h5":
            add_text(content, 16, True)
        elif tag == "h6":
            add_text(content, 14, True)
        elif tag == "p":
            add_text(content, 16, False)
        elif tag == "li":
            ops.append({"type": "text", "x": x + 20, "y": y, "text": f"- {content}", "font": "16px Arial"})
            y += 24
        elif tag == "br":
            y += 16
        elif tag == "hr":
            ops.append({"type": "line", "x1": x, "y1": y, "x2": x + 800, "y2": y})
            y += 20
        elif tag == "button":
            btn_text = content
            onclick = ""
            if "@onclick=" in content:
                text_part, _, rest = content.partition("@onclick=")
                btn_text = text_part.strip()
                onclick = rest.strip().strip('"')
            width = max(80, len(btn_text) * 9 + 30)
            ops.append({
                "type": "button", "x": x, "y": y, "w": width, "h": 36,
                "text": btn_text, "onclick": onclick
            })
            y += 46
        elif tag not in CANVAS_SUPPORTED_TAGS:
            if content:
                add_text(content, 16, False)

    total_height = y + 40
    ops_json = json.dumps(ops)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {{ margin: 0; background: white; }}
    canvas {{ display: block; }}
  </style>
</head>
<body>
  <canvas id="shai-canvas" width="900" height="{total_height}"></canvas>
  <script>
    const ops = {ops_json};
    const canvas = document.getElementById('shai-canvas');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'black';
    for (const op of ops) {{
      if (op.type === 'text') {{
        ctx.font = op.font;
        ctx.fillStyle = 'black';
        ctx.fillText(op.text, op.x, op.y);
      }} else if (op.type === 'line') {{
        ctx.strokeStyle = 'black';
        ctx.beginPath();
        ctx.moveTo(op.x1, op.y1);
        ctx.lineTo(op.x2, op.y2);
        ctx.stroke();
      }} else if (op.type === 'button') {{
        ctx.strokeStyle = 'black';
        ctx.strokeRect(op.x, op.y, op.w, op.h);
        ctx.font = '14px Arial';
        ctx.fillStyle = 'black';
        ctx.fillText(op.text, op.x + 12, op.y + op.h / 2 + 5);
      }}
    }}
    canvas.addEventListener('mousemove', function(e) {{
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      let overButton = false;
      for (const op of ops) {{
        if (op.type === 'button' && mx >= op.x && mx <= op.x + op.w && my >= op.y && my <= op.y + op.h) {{
          overButton = true;
        }}
      }}
      canvas.style.cursor = overButton ? 'pointer' : 'default';
    }});
    canvas.addEventListener('click', function(e) {{
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      for (const op of ops) {{
        if (op.type === 'button' && mx >= op.x && mx <= op.x + op.w && my >= op.y && my <= op.y + op.h) {{
          if (op.onclick) {{
            try {{ new Function(op.onclick)(); }} catch (err) {{ console.error(err); }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>"""


def extract_command(line):
    if not line.startswith("@"):
        return "", line, ""

    space_index = line.find(" ")
    bracket_index = line.find("[")

    if bracket_index != -1 and (space_index == -1 or bracket_index <= space_index):
        command = line[:bracket_index].rstrip()
        end_bracket = line.find("]", bracket_index)
        if end_bracket != -1:
            attrs = line[bracket_index + 1:end_bracket]
            content = line[end_bracket + 1:].strip()
            return command, content, attrs
        return command, "", ""

    if space_index != -1:
        command = line[:space_index]
        rest = line[space_index + 1:].strip()
        if rest.startswith("["):
            end_bracket = rest.find("]")
            if end_bracket != -1:
                attrs = rest[1:end_bracket]
                content = rest[end_bracket + 1:].strip()
                return command, content, attrs
        return command, rest, ""

    return line, "", ""


def compile_shai(shai_code):
    out = ["<!DOCTYPE html>", "<html>", "<head>"]
    in_body = False
    in_list = False
    in_table = False
    in_table_head = False
    in_table_body = False
    in_form = False
    in_video = False

    for raw_line in shai_code.split("\n"):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line in BODY_MARKERS:
            out.append("</head>")
            out.append("<body>")
            in_body = True
            continue

        command, content, attrs = extract_command(line)

        if command in ("@title", "@نص"):
            out.append(f"  <title>{content}</title>")
            continue

        if command in ("@style", "@مسار"):
            out.append(f'  <link rel="stylesheet" href="{content}">')
            continue

        if not in_body:
            continue

        tag = ALL_COMMANDS.get(command)

        if tag is None:
            out.append(f"  <p>{line}</p>")
            continue

        if tag in HEADER_TAGS:
            if in_list:
                out.append("  </ul>")
                in_list = False
            if in_table:
                if in_table_head:
                    out.append("    </thead>")
                    in_table_head = False
                if in_table_body:
                    out.append("    </tbody>")
                    in_table_body = False
                out.append("  </table>")
                in_table = False
            out.append(f"  <{tag}>{content}</{tag}>")
        elif tag == "p":
            out.append(f"  <p>{content}</p>")
        elif tag == "ul":
            if in_list:
                out.append("  </ul>")
            out.append("  <ul>")
            in_list = True
        elif tag == "li":
            if not in_list:
                out.append("  <ul>")
                in_list = True
            out.append(f"    <li>{content}</li>")
        elif tag == "table":
            if in_list:
                out.append("  </ul>")
                in_list = False
            out.append('  <table border="1">')
            in_table = True
        elif tag == "thead":
            out.append("    <thead>")
            in_table_head = True
        elif tag == "tbody":
            if in_table_head:
                out.append("    </thead>")
                in_table_head = False
            out.append("    <tbody>")
            in_table_body = True
        elif tag == "tr":
            if in_table_head or in_table_body:
                out.append("      <tr>")
        elif tag == "th":
            out.append(f"        <th>{content}</th>")
        elif tag == "td":
            out.append(f"        <td>{content}</td>")
        elif tag == "form":
            out.append("  <form>")
            in_form = True
        elif tag == "label":
            out.append(f"    <label {attrs}>{content}</label>")
        elif tag == "input":
            out.append(f"    <input {attrs}>")
        elif tag == "button":
            if "@onclick=" in content:
                text_part, _, rest = content.partition("@onclick=")
                onclick = rest.strip().strip('"')
                out.append(f'  <button onclick="{onclick}">{text_part.strip()}</button>')
            else:
                out.append(f"  <button {attrs}>{content}</button>")
        elif tag == "video":
            out.append(f"  <video {attrs}>")
            in_video = True
        elif tag == "source":
            out.append(f"    <source {attrs}>")
        elif tag == "br":
            out.append("  <br>")
        elif tag == "hr":
            out.append("  <hr>")
        elif tag == "img":
            out.append(f"  <img {attrs}>")
        elif tag in GENERIC_TAGS:
            if attrs:
                out.append(f"  <{tag} {attrs}>{content}</{tag}>")
            else:
                out.append(f"  <{tag}>{content}</{tag}>")

    if in_list:
        out.append("  </ul>")
    if in_table_head:
        out.append("    </thead>")
    if in_table_body:
        out.append("    </tbody>")
    if in_table:
        out.append("  </table>")
    if in_form:
        out.append("  </form>")
    if in_video:
        out.append("  </video>")

    if not in_body:
        out.append("</head>")
        out.append("<body>")
        out.append("  <h1>Missing @body section</h1>")

    out.append(STYLE_BLOCK)
    out.append("</body>")
    out.append("</html>")

    return "\n".join(out)


class ShaiIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("بيئة تطوير شاي - Shai IDE")
        self.root.geometry("1200x800")

        self.current_theme = "dark"
        self.current_file = None
        self.recent_files = []
        self.language = "ar"
        self.tab_files = {}
        self.editors = {}
        self._highlight_job = None

        self.load_settings()
        self.setup_theme()

        self.create_menu()

        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(self.main_pane, width=200)
        self.main_pane.add(self.sidebar)

        self.create_explorer()

        self.editor_area = ttk.Frame(self.main_pane)
        self.main_pane.add(self.editor_area)

        self.notebook = ttk.Notebook(self.editor_area)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_first_tab()

        self.autocomplete_words = [
            "@title", "@style", "@body",
            "@h1", "@h2", "@h3", "@h4", "@h5", "@h6",
            "@p", "@ul", "@li", "@button",
            "@نص", "@مسار", "@جسم",
            "@ر1", "@ر2", "@ر3", "@ر4", "@ر5", "@ر6",
            "@فقرة", "@قائمة", "@عنصر", "@زر"
        ]

        self.create_bottom_panel()
        self.apply_theme_colors()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.root.bind_all("<Control-s>", self.save_file)
        self.root.bind_all("<Control-Shift-s>", self.save_as_file)
        self.root.bind_all("<F5>", self.run_code)
        self.root.bind_all("<F6>", self.run_code_canvas)

    def create_first_tab(self):
        tab_name = "غير مسمى.shai" if self.language == "ar" else "Untitled.shai"
        self.create_tab(tab_name)

    def create_tab(self, title, content="", filepath=None, skip_highlight=False):
        tab = ttk.Frame(self.notebook)
        editor = self.create_editor_widgets(tab)

        if content:
            editor.insert("1.0", content)

        self.notebook.add(tab, text=title)
        self.notebook.select(tab)

        self.tab_files[tab] = filepath
        self.editors[tab] = editor

        if filepath:
            self.current_file = filepath

        if content and not skip_highlight:
            self.highlight_editor(editor)

        return tab, editor

    def create_editor_widgets(self, parent_frame):
        editor = scrolledtext.ScrolledText(
            parent_frame,
            wrap=tk.NONE,
            width=100,
            height=30,
            font=("Consolas", 12),
            bg=self.editor_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.accent_color,
            undo=True,
            relief=tk.FLAT
        )
        editor.pack(fill=tk.BOTH, expand=True)

        self.setup_syntax_tags(editor)

        editor.bind("<KeyRelease>", self.on_key_release)
        editor.bind("<<Paste>>", self.on_paste)

        return editor

    def setup_syntax_tags(self, editor):
        editor.tag_configure("directive", foreground="blue", font=("Consolas", 12, "bold"))
        editor.tag_configure("arabic_directive", foreground="brown", font=("Consolas", 12, "bold"))
        editor.tag_configure("attribute", foreground="teal", font=("Consolas", 12))
        editor.tag_configure("comment", foreground="green", font=("Consolas", 12, "italic"))
        editor.tag_configure("string", foreground="chocolate", font=("Consolas", 12))
        editor.tag_configure("header", foreground="red", font=("Consolas", 12, "bold"))
        editor.tag_configure("title_cmd", foreground="darkgreen", font=("Consolas", 12, "bold"))
        editor.tag_configure("style_cmd", foreground="purple", font=("Consolas", 12, "bold"))
        editor.tag_configure("body_cmd", foreground="orange", font=("Consolas", 12, "bold"))
        editor.tag_configure("button_cmd", foreground="goldenrod", font=("Consolas", 12, "bold"))
        editor.tag_configure("list_cmd", foreground="olive", font=("Consolas", 12))
        editor.tag_configure("paragraph", foreground="navy", font=("Consolas", 12))
        editor.tag_configure("tag_cmd", foreground="gray", font=("Consolas", 12, "bold"))

    def t(self, english, arabic):
        return arabic if self.language == "ar" else english

    def load_settings(self):
        try:
            if os.path.exists("shai_settings.json"):
                with open("shai_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("theme", "dark")
                    self.recent_files = settings.get("recent_files", [])
                    self.language = settings.get("language", "ar")
        except Exception:
            pass

    def save_settings(self):
        try:
            with open("shai_settings.json", "w", encoding="utf-8") as f:
                json.dump({
                    "theme": self.current_theme,
                    "recent_files": self.recent_files[-10:],
                    "language": self.language
                }, f, ensure_ascii=False)
        except Exception:
            pass

    def on_closing(self):
        self.save_settings()
        self.root.destroy()

    def on_tab_changed(self, event=None):
        current_tab = self.get_current_tab()
        if current_tab:
            self.current_file = self.tab_files.get(current_tab)
            self.highlight_current_tab()

    def get_current_tab(self):
        try:
            current_index = self.notebook.index("current")
            if current_index >= 0:
                return self.notebook.nametowidget(self.notebook.tabs()[current_index])
        except Exception:
            pass
        return None

    def get_current_editor(self):
        current_tab = self.get_current_tab()
        if current_tab:
            return self.editors.get(current_tab)
        return None

    def setup_theme(self):
        if self.current_theme == "dark":
            self.bg_color = "#1e1e1e"
            self.fg_color = "#d4d4d4"
            self.sidebar_bg = "#252526"
            self.editor_bg = "#1e1e1e"
            self.accent_color = "#007acc"
            self.button_bg = "#0e639c"
            self.tree_bg = "#252526"
            self.statusbar_bg = "#007acc"
            self.statusbar_fg = "#ffffff"
            self.menu_bg = "#252526"
            self.menu_fg = "#cccccc"
        else:
            self.bg_color = "#ffffff"
            self.fg_color = "#323232"
            self.sidebar_bg = "#f3f3f3"
            self.editor_bg = "#ffffff"
            self.accent_color = "#005a9e"
            self.button_bg = "#0066b8"
            self.tree_bg = "#f3f3f3"
            self.statusbar_bg = "#e4e6f1"
            self.statusbar_fg = "#000000"
            self.menu_bg = "#ffffff"
            self.menu_fg = "#000000"

    def apply_theme_colors(self):
        self.root.configure(bg=self.bg_color)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TButton",
                       background=self.button_bg,
                       foreground="white",
                       borderwidth=1)
        style.map("TButton",
                 background=[('active', self.accent_color)])

        style.configure("Treeview",
                       background=self.tree_bg,
                       foreground=self.fg_color,
                       fieldbackground=self.tree_bg)
        style.map("Treeview",
                 background=[('selected', self.accent_color)],
                 foreground=[('selected', 'white')])

        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab",
                       background=self.sidebar_bg,
                       foreground=self.fg_color,
                       padding=[10, 5])
        style.map("TNotebook.Tab",
                 background=[('selected', self.bg_color)],
                 foreground=[('selected', self.fg_color)])

        for tab, editor in self.editors.items():
            editor.configure(bg=self.editor_bg, fg=self.fg_color,
                           insertbackground=self.fg_color,
                           selectbackground=self.accent_color)

        if hasattr(self, 'output'):
            self.output.configure(bg=self.editor_bg, fg=self.fg_color)

        if hasattr(self, 'repl_output'):
            self.repl_output.configure(bg=self.editor_bg, fg=self.fg_color)

        if hasattr(self, 'terminal'):
            self.terminal.configure(bg=self.editor_bg, fg=self.fg_color)

        if hasattr(self, 'repl_input'):
            self.repl_input.configure(bg=self.editor_bg, fg=self.fg_color,
                                     insertbackground=self.fg_color)

        if hasattr(self, 'status'):
            self.status.configure(bg=self.statusbar_bg, fg=self.statusbar_fg)

        if hasattr(self, 'sidebar'):
            self.sidebar.configure(style="TFrame")

        self.highlight_all_tabs()

    def highlight_all_tabs(self):
        for tab, editor in self.editors.items():
            self.highlight_editor(editor)

    def highlight_current_tab(self):
        editor = self.get_current_editor()
        if editor:
            self.highlight_editor(editor)

    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.menu_bg, fg=self.menu_fg,
                         activebackground=self.accent_color,
                         activeforeground="white")

        file_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.menu_bg, fg=self.menu_fg,
                           activebackground=self.accent_color,
                           activeforeground="white")
        file_menu.add_command(label=self.t("New", "جديد"),
                             command=self.new_file,
                             accelerator="Ctrl+N")
        file_menu.add_command(label=self.t("Open...", "فتح..."),
                             command=self.open_file,
                             accelerator="Ctrl+O")
        file_menu.add_command(label=self.t("Open Folder", "فتح مجلد"),
                             command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label=self.t("Save", "حفظ"),
                             command=self.save_file,
                             accelerator="Ctrl+S")
        file_menu.add_command(label=self.t("Save As...", "حفظ باسم..."),
                             command=self.save_as_file,
                             accelerator="Ctrl+Shift+S")
        file_menu.add_separator()

        recent_menu = tk.Menu(file_menu, tearoff=0,
                             bg=self.menu_bg, fg=self.menu_fg,
                             activebackground=self.accent_color,
                             activeforeground="white")
        self.update_recent_menu(recent_menu)
        file_menu.add_cascade(label=self.t("Open Recent", "فتح حديث"),
                             menu=recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label=self.t("Exit", "خروج"),
                             command=self.on_closing)
        menubar.add_cascade(label=self.t("File", "ملف"), menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.menu_bg, fg=self.menu_fg,
                           activebackground=self.accent_color,
                           activeforeground="white")
        edit_menu.add_command(label=self.t("Undo", "تراجع"),
                             command=self.undo,
                             accelerator="Ctrl+Z")
        edit_menu.add_command(label=self.t("Redo", "إعادة"),
                             command=self.redo,
                             accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label=self.t("Cut", "قص"),
                             command=self.cut,
                             accelerator="Ctrl+X")
        edit_menu.add_command(label=self.t("Copy", "نسخ"),
                             command=self.copy,
                             accelerator="Ctrl+C")
        edit_menu.add_command(label=self.t("Paste", "لصق"),
                             command=self.paste,
                             accelerator="Ctrl+V")
        menubar.add_cascade(label=self.t("Edit", "تحرير"), menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.menu_bg, fg=self.menu_fg,
                           activebackground=self.accent_color,
                           activeforeground="white")
        view_menu.add_command(label=self.t("Toggle Sidebar", "إظهار/إخفاء الشريط الجانبي"),
                             command=self.toggle_sidebar)
        view_menu.add_separator()

        theme_menu = tk.Menu(view_menu, tearoff=0,
                            bg=self.menu_bg, fg=self.menu_fg,
                            activebackground=self.accent_color,
                            activeforeground="white")
        theme_menu.add_command(label="Dark Mode",
                              command=lambda: self.switch_theme("dark"),
                              state="disabled" if self.current_theme == "dark" else "normal")
        theme_menu.add_command(label="Light Mode",
                              command=lambda: self.switch_theme("light"),
                              state="disabled" if self.current_theme == "light" else "normal")
        view_menu.add_cascade(label=self.t("Theme", "المظهر"), menu=theme_menu)

        lang_menu = tk.Menu(view_menu, tearoff=0,
                           bg=self.menu_bg, fg=self.menu_fg,
                           activebackground=self.accent_color,
                           activeforeground="white")
        lang_menu.add_command(label="العربية",
                             command=lambda: self.switch_language("ar"))
        lang_menu.add_command(label="English",
                             command=lambda: self.switch_language("en"))
        view_menu.add_cascade(label=self.t("Language", "اللغة"), menu=lang_menu)

        menubar.add_cascade(label=self.t("View", "عرض"), menu=view_menu)

        run_menu = tk.Menu(menubar, tearoff=0,
                          bg=self.menu_bg, fg=self.menu_fg,
                          activebackground=self.accent_color,
                          activeforeground="white")
        run_menu.add_command(label=self.t("Run Shai File", "تشغيل ملف شاي"),
                            command=self.run_code,
                            accelerator="F5")
        run_menu.add_command(label=self.t("Run (Canvas Turbo)", "تشغيل (كانفس تيربو)"),
                            command=self.run_code_canvas,
                            accelerator="F6")
        run_menu.add_command(label=self.t("Compile Only", "ترجمة فقط"),
                            command=self.compile_only)
        run_menu.add_command(label=self.t("Open in Browser", "فتح في المتصفح"),
                            command=self.open_in_browser)
        menubar.add_cascade(label=self.t("Run", "تشغيل"), menu=run_menu)

        help_menu = tk.Menu(menubar, tearoff=0,
                           bg=self.menu_bg, fg=self.menu_fg,
                           activebackground=self.accent_color,
                           activeforeground="white")
        help_menu.add_command(label=self.t("About", "حول"),
                             command=self.show_about)
        help_menu.add_command(label=self.t("Shai Syntax", "بناء جملة شاي"),
                             command=self.show_syntax_help)
        menubar.add_cascade(label=self.t("Help", "مساعدة"), menu=help_menu)

        self.root.config(menu=menubar)

    def update_recent_menu(self, menu):
        menu.delete(0, tk.END)
        for file in self.recent_files:
            if os.path.exists(file):
                menu.add_command(label=os.path.basename(file),
                               command=lambda f=file: self.open_recent_file(f))

    def switch_theme(self, theme):
        self.current_theme = theme
        self.setup_theme()
        self.apply_theme_colors()
        self.save_settings()

    def switch_language(self, lang):
        self.language = lang
        self.save_settings()
        messagebox.showinfo(
            self.t("Language Changed", "تم تغيير اللغة"),
            self.t("Language changed. Some changes may require restart.",
                  "تم تغيير اللغة. بعض التغييرات قد تتطلب إعادة التشغيل.")
        )

    def create_explorer(self):
        explorer_header = ttk.Label(self.sidebar,
                                   text=self.t("EXPLORER", "المستكشف"),
                                   font=("Segoe UI", 9, "bold"))
        explorer_header.pack(fill=tk.X, padx=10, pady=(10, 5))

        toolbar = ttk.Frame(self.sidebar)
        toolbar.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(toolbar, text=self.t("Folder", "مجلد"), width=8,
                  command=self.open_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=self.t("Refresh", "تحديث"), width=8,
                  command=self.refresh_explorer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=self.t("New", "جديد"), width=8,
                  command=self.new_shai_file).pack(side=tk.LEFT, padx=2)

        self.file_tree = ttk.Treeview(self.sidebar, show="tree", selectmode="browse")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.file_tree.bind("<Double-1>", self.on_tree_double_click)

        self.refresh_explorer()

    def refresh_explorer(self, folder="."):
        self.file_tree.delete(*self.file_tree.get_children())
        try:
            for item in sorted(os.listdir(folder)):
                if item.startswith('.'):
                    continue
                full_path = os.path.join(folder, item)
                if os.path.isdir(full_path):
                    self.file_tree.insert("", "end", text=f"[DIR] {item}",
                                        values=[full_path], open=False)
                else:
                    label = "[SHAI]" if item.endswith(".shai") else "[FILE]"
                    self.file_tree.insert("", "end", text=f"{label} {item}",
                                        values=[full_path])
        except PermissionError:
            pass

    def open_recent_file(self, filepath):
        if os.path.exists(filepath):
            self.load_file(filepath)
        else:
            messagebox.showerror(
                self.t("Error", "خطأ"),
                self.t(f"File not found:\n{filepath}", f"الملف غير موجود:\n{filepath}")
            )
            if filepath in self.recent_files:
                self.recent_files.remove(filepath)
                self.save_settings()

    def open_folder(self):
        folder = filedialog.askdirectory(
            title=self.t("Select Folder", "اختر مجلد")
        )
        if folder:
            os.chdir(folder)
            self.refresh_explorer(folder)

    def create_bottom_panel(self):
        self.bottom_notebook = ttk.Notebook(self.root)
        self.bottom_notebook.pack(fill=tk.BOTH, expand=False, padx=5, pady=(0, 5))

        self.output_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.output_frame, text=self.t("Output", "النتائج"))

        self.output = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 11),
            bg=self.editor_bg,
            fg=self.fg_color,
            state="normal",
            relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        self.repl_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.repl_frame, text=self.t("Terminal", "طرفية"))

        self.repl_output = scrolledtext.ScrolledText(
            self.repl_frame,
            wrap=tk.WORD,
            height=4,
            font=("Consolas", 11),
            bg=self.editor_bg,
            fg=self.fg_color,
            state="normal",
            relief=tk.FLAT
        )
        self.repl_output.pack(fill=tk.BOTH, expand=True)

        self.repl_input = tk.Entry(
            self.repl_frame,
            font=("Consolas", 11),
            bg=self.editor_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.repl_input.pack(fill=tk.X, padx=5, pady=5)
        self.repl_input.bind("<Return>", self.eval_repl)

        self.terminal_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.terminal_frame, text=self.t("Console", "محطة"))

        self.terminal = scrolledtext.ScrolledText(
            self.terminal_frame,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 11),
            bg=self.editor_bg,
            fg=self.fg_color,
            state="normal",
            relief=tk.FLAT
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        self.status = tk.Label(
            self.root,
            text=self.t("Ready", "جاهز"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=self.statusbar_bg,
            fg=self.statusbar_fg,
            font=("Segoe UI", 9)
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def new_file(self, event=None):
        tab_name = self.t("غير مسمى.shai", "Untitled.shai")
        self.create_tab(tab_name)
        self.status.config(text=self.t("New file created", "تم إنشاء ملف جديد"))

    def on_tree_double_click(self, event):
        selection = self.file_tree.selection()
        if not selection:
            return

        item = selection[0]
        path = self.file_tree.item(item, "values")[0]

        if os.path.isdir(path):
            if self.file_tree.item(item, "open"):
                self.file_tree.item(item, open=False)
                for child in self.file_tree.get_children(item):
                    self.file_tree.delete(child)
            else:
                self.file_tree.item(item, open=True)
                for child in self.file_tree.get_children(item):
                    self.file_tree.delete(child)

                try:
                    for item_name in sorted(os.listdir(path)):
                        if item_name.startswith('.'):
                            continue
                        full_path = os.path.join(path, item_name)
                        if os.path.isdir(full_path):
                            self.file_tree.insert(item, "end", text=f"[DIR] {item_name}",
                                                values=[full_path])
                        else:
                            label = "[SHAI]" if item_name.endswith(".shai") else "[FILE]"
                            self.file_tree.insert(item, "end", text=f"{label} {item_name}",
                                                values=[full_path])
                except PermissionError:
                    pass
        elif path.endswith(".shai"):
            self.load_file(path)

    def open_file(self, event=None):
        filepath = filedialog.askopenfilename(
            title=self.t("Open Shai File", "فتح ملف شاي"),
            filetypes=[("Shai files", "*.shai"), ("All files", "*.*")]
        )
        if filepath:
            self.load_file(filepath)

    def load_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tab_name = os.path.basename(filepath)

            for tab, fpath in self.tab_files.items():
                if fpath == filepath:
                    self.notebook.select(tab)
                    return

            is_large = (
                len(content) > LARGE_FILE_CHAR_THRESHOLD
                or content.count("\n") > LARGE_FILE_LINE_THRESHOLD
            )

            self.create_tab(tab_name, content, filepath, skip_highlight=is_large)

            if filepath not in self.recent_files:
                self.recent_files.insert(0, filepath)
                self.save_settings()

            if is_large:
                self.status.config(text=self.t(
                    f"Loaded (large file, full highlighting skipped): {filepath}",
                    f"تم التحميل (ملف كبير، تم تخطي التلوين الكامل): {filepath}"
                ))
            else:
                self.status.config(text=self.t(f"Loaded: {filepath}", f"تم التحميل: {filepath}"))

        except Exception as e:
            messagebox.showerror(
                self.t("Error", "خطأ"),
                self.t(f"Failed to load file:\n{str(e)}", f"فشل تحميل الملف:\n{str(e)}")
            )

    def validate_write_path(self, filepath):
        if not filepath:
            return False, self.t("No file path given.", "لم يتم تحديد مسار الملف.")

        try:
            directory = os.path.dirname(os.path.abspath(filepath)) or "."
        except Exception:
            return False, self.t("Invalid file path.", "مسار ملف غير صالح.")

        if not os.path.isdir(directory):
            return False, self.t(
                f"Directory does not exist:\n{directory}",
                f"المجلد غير موجود:\n{directory}"
            )

        if not os.access(directory, os.W_OK):
            return False, self.t(
                f"Directory is not writable:\n{directory}",
                f"لا يمكن الكتابة في هذا المجلد:\n{directory}"
            )

        return True, ""

    def new_shai_file(self):
        default_name = self.t("غير مسمى.shai", "Untitled.shai")

        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            title=self.t("Create New Shai File", "إنشاء ملف شاي جديد"),
            defaultextension=".shai",
            filetypes=[("Shai files", "*.shai"), ("All files", "*.*")],
            initialfile=default_name
        )

        if filepath:
            valid, reason = self.validate_write_path(filepath)
            if not valid:
                messagebox.showerror(self.t("Error", "خطأ"), reason)
                return

            template = self.t("""# برنامجي الأول بشاي
@نص صفحتي بشاي
@مسار style.css

@جسم
  @ر1 مرحباً بالعالم!
  @فقرة هذه فقرة مكتوبة بلغة شاي.
  @زر انقر هنا @onclick="alert('مرحباً من شاي!')"
""",
"""# My first Shai program
@title My Shai Page
@style style.css

@body
  @h1 Welcome to Shai!
  @p This is a paragraph in Shai language.
  @button Click me @onclick="alert('Hello from Shai!')"
""")

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(template)

                self.refresh_explorer()
                self.load_file(filepath)

            except Exception as e:
                messagebox.showerror(
                    self.t("Error", "خطأ"),
                    self.t(f"Failed to create file:\n{str(e)}", f"فشل إنشاء الملف:\n{str(e)}")
                )

    def save_file(self, event=None):
        editor = self.get_current_editor()
        if not editor:
            return

        current_tab = self.get_current_tab()
        if not current_tab:
            return

        content = editor.get("1.0", "end-1c")

        current_file = self.tab_files.get(current_tab)

        if current_file is None or not os.path.exists(current_file):
            self.save_as_file()
        else:
            valid, reason = self.validate_write_path(current_file)
            if not valid:
                messagebox.showerror(self.t("Error", "خطأ"), reason)
                return

            try:
                with open(current_file, "w", encoding="utf-8") as f:
                    f.write(content)

                self.status.config(text=self.t(f"Saved: {current_file}", f"تم الحفظ: {current_file}"))

                if current_file not in self.recent_files:
                    self.recent_files.insert(0, current_file)
                    self.save_settings()

            except Exception as e:
                messagebox.showerror(
                    self.t("Error", "خطأ"),
                    self.t(f"Failed to save file:\n{str(e)}", f"فشل حفظ الملف:\n{str(e)}")
                )

    def save_as_file(self, event=None):
        editor = self.get_current_editor()
        if not editor:
            return

        current_tab = self.get_current_tab()
        if not current_tab:
            return

        content = editor.get("1.0", "end-1c")

        current_file = self.tab_files.get(current_tab)
        if current_file and os.path.exists(current_file):
            initial_file = os.path.basename(current_file)
        else:
            initial_file = self.t("غير مسمى.shai", "Untitled.shai")

        self.root.focus_force()

        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            title=self.t("Save File As", "حفظ الملف باسم"),
            defaultextension=".shai",
            filetypes=[("Shai files", "*.shai"), ("All files", "*.*")],
            initialfile=initial_file
        )

        if not filepath:
            return

        valid, reason = self.validate_write_path(filepath)
        if not valid:
            messagebox.showerror(self.t("Error", "خطأ"), reason)
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            self.tab_files[current_tab] = filepath
            self.current_file = filepath
            self.notebook.tab(current_tab, text=os.path.basename(filepath))

            self.status.config(text=self.t(f"Saved as: {filepath}", f"تم الحفظ باسم: {filepath}"))

            if filepath not in self.recent_files:
                self.recent_files.insert(0, filepath)
                self.save_settings()

            self.refresh_explorer()

        except Exception as e:
            messagebox.showerror(
                self.t("Error", "خطأ"),
                self.t(f"Failed to save file:\n{str(e)}", f"فشل حفظ الملف:\n{str(e)}")
            )

    def on_key_release(self, event=None):
        if self._highlight_job:
            self.root.after_cancel(self._highlight_job)
        self._highlight_job = self.root.after(15, self.highlight_current_line)

    def on_paste(self, event=None):
        self.root.after(10, self.highlight_current_tab)

    def highlight_current_line(self):
        self._highlight_job = None
        editor = self.get_current_editor()
        if not editor:
            return

        try:
            line_num = int(editor.index("insert").split(".")[0])
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"

            for tag in TAG_NAMES:
                editor.tag_remove(tag, line_start, line_end)

            line_text = editor.get(line_start, line_end)
        except tk.TclError:
            return
        except Exception:
            return

        self.highlight_line(editor, line_text, line_num)

    def highlight_editor(self, editor):
        if not editor:
            return

        try:
            text = editor.get("1.0", "end-1c")
            for tag in TAG_NAMES:
                editor.tag_remove(tag, "1.0", "end")
        except tk.TclError:
            return
        except Exception:
            return

        line_num = 1
        for line in text.split('\n'):
            self.highlight_line(editor, line, line_num)
            line_num += 1

    def highlight_line(self, editor, line, line_num):
        try:
            if line.strip().startswith('#'):
                start_pos = f"{line_num}.{line.find('#')}"
                editor.tag_add("comment", start_pos, f"{line_num}.end")

            for tag_name, keywords in HIGHLIGHT_GROUPS:
                for cmd in keywords:
                    idx = line.find(cmd)
                    if idx != -1:
                        start_pos = f"{line_num}.{idx}"
                        editor.tag_add(tag_name, start_pos, f"{start_pos}+{len(cmd)}c")

            if '@onclick=' in line:
                start_idx = line.find('@onclick=')
                editor.tag_add("attribute", f"{line_num}.{start_idx}", f"{line_num}.end")

            if '"' in line:
                start_idx = line.find('"')
                if start_idx != -1:
                    end_idx = line.find('"', start_idx + 1)
                    if end_idx != -1:
                        editor.tag_add("string", f"{line_num}.{start_idx}", f"{line_num}.{end_idx + 1}")
        except tk.TclError:
            pass
        except Exception:
            pass

    def run_code(self, event=None):
        editor = self.get_current_editor()
        if not editor:
            messagebox.showwarning(
                self.t("No File", "لا يوجد ملف"),
                self.t("Open a file first.", "افتح ملفاً أولاً.")
            )
            return

        code = editor.get("1.0", "end-1c").strip()

        if not code:
            messagebox.showwarning(
                self.t("Empty File", "ملف فارغ"),
                self.t("The editor is empty.", "المحرر فارغ.")
            )
            return

        self.output.delete("1.0", "end")
        self.status.config(text=self.t("Compiling...", "جاري الترجمة..."))

        try:
            html = compile_shai(code)
        except Exception as e:
            self.output.insert("1.0", self.t(f"Compilation failed:\n{str(e)}\n",
                                             f"فشلت الترجمة:\n{str(e)}\n"))
            self.status.config(text=self.t("Compilation failed", "فشلت الترجمة"))
            self.bottom_notebook.select(self.output_frame)
            return

        temp_dir = tempfile.mkdtemp()
        temp_html = os.path.join(temp_dir, "output.html")

        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(f"file:///{temp_html.replace(os.sep, '/')}")

        self.output.insert("1.0", self.t("Compiled successfully. Opening in browser.\n",
                                        "تمت الترجمة بنجاح. جاري الفتح في المتصفح.\n"))
        self.status.config(text=self.t("Running in browser", "قيد التشغيل في المتصفح"))
        self.bottom_notebook.select(self.output_frame)

    def run_code_canvas(self, event=None):
        editor = self.get_current_editor()
        if not editor:
            messagebox.showwarning(
                self.t("No File", "لا يوجد ملف"),
                self.t("Open a file first.", "افتح ملفاً أولاً.")
            )
            return

        code = editor.get("1.0", "end-1c").strip()

        if not code:
            messagebox.showwarning(
                self.t("Empty File", "ملف فارغ"),
                self.t("The editor is empty.", "المحرر فارغ.")
            )
            return

        self.output.delete("1.0", "end")
        self.status.config(text=self.t("Compiling (Canvas Turbo)...", "جاري الترجمة (كانفس تيربو)..."))

        try:
            html = compile_shai_canvas(code)
        except Exception as e:
            self.output.insert("1.0", self.t(f"Canvas compilation failed:\n{str(e)}\n",
                                             f"فشلت ترجمة الكانفس:\n{str(e)}\n"))
            self.status.config(text=self.t("Compilation failed", "فشلت الترجمة"))
            self.bottom_notebook.select(self.output_frame)
            return

        temp_dir = tempfile.mkdtemp()
        temp_html = os.path.join(temp_dir, "output_canvas.html")

        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html)

        webbrowser.open(f"file:///{temp_html.replace(os.sep, '/')}")

        self.output.insert("1.0", self.t(
            "Compiled with Canvas Turbo (single canvas element, no DOM tree, no CSS layout). "
            "Supports headings, paragraphs, list items, buttons, br and hr. Opening in browser.\n",
            "تمت الترجمة بوضع كانفس تيربو (عنصر كانفس واحد، بدون شجرة DOM أو تنسيق CSS). "
            "يدعم العناوين والفقرات وعناصر القوائم والأزرار وbr وhr. جاري الفتح في المتصفح.\n"
        ))
        self.status.config(text=self.t("Running (Canvas Turbo)", "قيد التشغيل (كانفس تيربو)"))
        self.bottom_notebook.select(self.output_frame)

    def compile_only(self):
        editor = self.get_current_editor()
        if not editor:
            return

        code = editor.get("1.0", "end-1c").strip()
        if not code:
            return

        current_tab = self.get_current_tab()
        current_file = self.tab_files.get(current_tab)

        try:
            html = compile_shai(code)
        except Exception as e:
            self.output.delete("1.0", "end")
            self.output.insert("1.0", self.t(f"Compilation failed:\n{str(e)}\n",
                                             f"فشلت الترجمة:\n{str(e)}\n"))
            self.bottom_notebook.select(self.output_frame)
            return

        if current_file:
            output_path = os.path.splitext(current_file)[0] + ".html"
        else:
            output_path = os.path.join(tempfile.mkdtemp(), "output.html")

        valid, reason = self.validate_write_path(output_path)
        if not valid:
            self.output.delete("1.0", "end")
            self.output.insert("1.0", reason + "\n")
            self.bottom_notebook.select(self.output_frame)
            return

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            self.output.delete("1.0", "end")
            self.output.insert("1.0", self.t(f"Failed to write output:\n{str(e)}\n",
                                             f"فشلت كتابة الملف:\n{str(e)}\n"))
            self.bottom_notebook.select(self.output_frame)
            return

        self.output.delete("1.0", "end")
        self.output.insert("1.0", self.t(f"Compiled to: {output_path}\n",
                                        f"تمت الترجمة إلى: {output_path}\n"))
        self.status.config(text=self.t("Compiled", "تمت الترجمة"))
        self.bottom_notebook.select(self.output_frame)

    def eval_repl(self, event):
        code = self.repl_input.get()
        self.repl_input.delete(0, tk.END)

        self.repl_output.insert("end", f">>> {code}\n")

        try:
            result = f"Result: {code}"
            self.repl_output.insert("end", f"{result}\n")
        except Exception as e:
            self.repl_output.insert("end", f"Error: {str(e)}\n")

        self.repl_output.see("end")

    def open_in_browser(self):
        current_tab = self.get_current_tab()
        current_file = self.tab_files.get(current_tab)

        if current_file and os.path.exists(current_file):
            webbrowser.open(f"file:///{current_file.replace(os.sep, '/')}")
        else:
            messagebox.showwarning(
                self.t("File Not Saved", "الملف غير محفوظ"),
                self.t("Save the file first.", "احفظ الملف أولاً.")
            )

    def undo(self, event=None):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_undo()
            except Exception:
                pass

    def redo(self, event=None):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_redo()
            except Exception:
                pass

    def cut(self, event=None):
        editor = self.get_current_editor()
        if editor:
            editor.event_generate("<<Cut>>")

    def copy(self, event=None):
        editor = self.get_current_editor()
        if editor:
            editor.event_generate("<<Copy>>")

    def paste(self, event=None):
        editor = self.get_current_editor()
        if editor:
            editor.event_generate("<<Paste>>")

    def toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, before=self.editor_area)

    def show_about(self):
        messagebox.showinfo(
            self.t("About Shai IDE", "حول بيئة شاي"),
            self.t(
                "Shai IDE v2.0\nA development environment for Shai language\n\nShai is a simple markup language for web development.",
                "بيئة شاي الإصدار 2.0\nبيئة تطوير للغة شاي\n\nشاي هي لغة ترميز بسيطة لتطوير الويب."
            )
        )

    def show_syntax_help(self):
        help_text = self.t("""Shai Language Syntax:

ENGLISH COMMANDS:
@title [text]       - Page title
@style [path]       - CSS stylesheet path
@body               - Start body content
@h1 [text]          - Heading level 1
@h2 [text]          - Heading level 2
@h3 [text]          - Heading level 3
@h4 [text]          - Heading level 4
@h5 [text]          - Heading level 5
@h6 [text]          - Heading level 6
@p [text]           - Paragraph
@ul                 - Start unordered list
@li [text]          - List item
@button [text] @onclick="[code]" - Button with click handler
@table              - Start table
@thead / @tbody     - Table head / body
@tr / @th / @td     - Table row / header cell / data cell
@form               - Start form
@label [text]       - Form label
@input [attrs]      - Input field
@video [attrs]      - Video element
@source [attrs]     - Video source

ARABIC COMMANDS:
@نص [نص]            - عنوان الصفحة
@مسار [مسار]        - ربط ملف أنماط CSS
@جسم               - يبدأ قسم محتوى الصفحة
@ر1 [نص]           - عنوان مستوى 1
@ر2 [نص]           - عنوان مستوى 2
@ر3 [نص]           - عنوان مستوى 3
@ر4 [نص]           - عنوان مستوى 4
@ر5 [نص]           - عنوان مستوى 5
@ر6 [نص]           - عنوان مستوى 6
@فقرة [نص]         - فقرة نصية
@قائمة             - قائمة غير مرتبة
@عنصر [نص]         - عنصر قائمة
@زر [نص] @onclick="[كود]" - زر مع معالج النقر
@جدول              - جدول
@رأس-جدول / @جسم-جدول - رأس الجدول / جسم الجدول
@صف-جدول / @رأس-خلية / @خلية-جدول - صف / خلية رأس / خلية بيانات
@نموذج             - نموذج
@تسمية [نص]        - تسمية حقل
@إدخال [خصائص]     - حقل إدخال
@فيديو [خصائص]     - عنصر فيديو
@مصدر [خصائص]      - مصدر فيديو

EXAMPLE:
# Headings Example
@title صفحة العناوين
@style style.css

@جسم
  @ر1 العنوان الرئيسي
  @فقرة هذه فقرة تحت العنوان الرئيسي
  @ر2 عنوان فرعي
  @ر3 عنوان أصغر
  @زر انقر هنا @onclick="alert('مرحباً')"
""",
"""بناء جملة لغة شاي:

الأوامر الإنجليزية:
@title [نص]        - عنوان الصفحة
@style [مسار]      - مسار ملف الأنماط
@body              - بدء محتوى الصفحة
@h1 [نص]           - عنوان مستوى 1
@h2 [نص]           - عنوان مستوى 2
@h3 [نص]           - عنوان مستوى 3
@h4 [نص]           - عنوان مستوى 4
@h5 [نص]           - عنوان مستوى 5
@h6 [نص]           - عنوان مستوى 6
@p [نص]            - فقرة
@ul                - بدء قائمة غير مرتبة
@li [نص]           - عنصر قائمة
@button [نص] @onclick="[كود]" - زر مع معالج النقر
@table             - جدول
@thead / @tbody    - رأس / جسم الجدول
@tr / @th / @td    - صف / خلية رأس / خلية بيانات
@form              - نموذج
@label [نص]        - تسمية حقل
@input [خصائص]     - حقل إدخال
@video [خصائص]     - عنصر فيديو
@source [خصائص]    - مصدر فيديو

الأوامر العربية:
@نص [نص]           - Page title
@مسار [مسار]       - CSS file path
@جسم              - Start body section
@ر1 [نص]          - Heading level 1
@ر2 [نص]          - Heading level 2
@ر3 [نص]          - Heading level 3
@ر4 [نص]          - Heading level 4
@ر5 [نص]          - Heading level 5
@ر6 [نص]          - Heading level 6
@فقرة [نص]        - Paragraph
@قائمة            - Unordered list
@عنصر [نص]        - List item
@زر [نص] @onclick="[code]" - Button with onclick handler

مثال:
# This is a comment
@title My First Page
@style style.css

@body
  @h1 Hello World
  @p This is a paragraph in Shai
  @h2 Sub Heading
  @button Click here @onclick="alert('Hello')"
""")

        help_window = tk.Toplevel(self.root)
        help_window.title(self.t("Shai Syntax Help", "مساعدة بناء جملة شاي"))
        help_window.geometry("600x400")
        help_window.configure(bg=self.bg_color)

        text_widget = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg=self.editor_bg,
            fg=self.fg_color,
            relief=tk.FLAT
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShaiIDE(root)
    root.mainloop()
