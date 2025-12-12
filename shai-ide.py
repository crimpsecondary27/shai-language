import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import re
import os
import webbrowser
import tempfile
import json
import subprocess
import sys

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
        
    def create_first_tab(self):
        tab_name = "غير مسمى.shai" if self.language == "ar" else "Untitled.shai"
        self.create_tab(tab_name)
        
    def create_tab(self, title, content="", filepath=None):
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
        
        return editor
    
    def setup_syntax_tags(self, editor):
        if self.current_theme == "dark":
            editor.tag_configure("directive", foreground="#569cd6", font=("Consolas", 12, "bold"))
            editor.tag_configure("arabic_directive", foreground="#d7ba7d", font=("Consolas", 12, "bold"))
            editor.tag_configure("attribute", foreground="#9cdcfe", font=("Consolas", 12))
            editor.tag_configure("comment", foreground="#6a9955", font=("Consolas", 12, "italic"))
            editor.tag_configure("string", foreground="#ce9178", font=("Consolas", 12))
            editor.tag_configure("header", foreground="#d16969", font=("Consolas", 12, "bold"))
            editor.tag_configure("title_cmd", foreground="#4ec9b0", font=("Consolas", 12, "bold"))
            editor.tag_configure("style_cmd", foreground="#c586c0", font=("Consolas", 12, "bold"))
            editor.tag_configure("body_cmd", foreground="#dcdcaa", font=("Consolas", 12, "bold"))
            editor.tag_configure("button_cmd", foreground="#ffd700", font=("Consolas", 12, "bold"))
            editor.tag_configure("list_cmd", foreground="#b5cea8", font=("Consolas", 12))
            editor.tag_configure("paragraph", foreground="#9cdcfe", font=("Consolas", 12))
        else:
            editor.tag_configure("directive", foreground="#0000ff", font=("Consolas", 12, "bold"))
            editor.tag_configure("arabic_directive", foreground="#8b4513", font=("Consolas", 12, "bold"))
            editor.tag_configure("attribute", foreground="#2e8b57", font=("Consolas", 12))
            editor.tag_configure("comment", foreground="#008000", font=("Consolas", 12, "italic"))
            editor.tag_configure("string", foreground="#a31515", font=("Consolas", 12))
            editor.tag_configure("header", foreground="#ff4500", font=("Consolas", 12, "bold"))
            editor.tag_configure("title_cmd", foreground="#2e8b57", font=("Consolas", 12, "bold"))
            editor.tag_configure("style_cmd", foreground="#8a2be2", font=("Consolas", 12, "bold"))
            editor.tag_configure("body_cmd", foreground="#d2691e", font=("Consolas", 12, "bold"))
            editor.tag_configure("button_cmd", foreground="#ff8c00", font=("Consolas", 12, "bold"))
            editor.tag_configure("list_cmd", foreground="#556b2f", font=("Consolas", 12))
            editor.tag_configure("paragraph", foreground="#2e8b57", font=("Consolas", 12))
    
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
        except:
            pass
            
    def save_settings(self):
        try:
            with open("shai_settings.json", "w", encoding="utf-8") as f:
                json.dump({
                    "theme": self.current_theme,
                    "recent_files": self.recent_files[-10:],
                    "language": self.language
                }, f, ensure_ascii=False)
        except:
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
        except:
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
        
        ttk.Button(toolbar, text="📁", width=3, 
                  command=self.open_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄", width=3, 
                  command=self.refresh_explorer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="➕", width=3, 
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
                    node = self.file_tree.insert("", "end", text=f"📁 {item}", 
                                               values=[full_path], open=False)
                else:
                    icon = "📄" if item.endswith(".shai") else "📋"
                    self.file_tree.insert("", "end", text=f"{icon} {item}", 
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
                            node = self.file_tree.insert(item, "end", text=f"📁 {item_name}", 
                                                       values=[full_path])
                        else:
                            icon = "📄" if item_name.endswith(".shai") else "📋"
                            self.file_tree.insert(item, "end", text=f"{icon} {item_name}", 
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
            
            tab, editor = self.create_tab(tab_name, content, filepath)
            
            if filepath not in self.recent_files:
                self.recent_files.insert(0, filepath)
                self.save_settings()
                
            self.status.config(text=self.t(f"Loaded: {filepath}", f"تم التحميل: {filepath}"))
            
        except Exception as e:
            messagebox.showerror(
                self.t("Error", "خطأ"),
                self.t(f"Failed to load file:\n{str(e)}", f"فشل تحميل الملف:\n{str(e)}")
            )
            
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
        self.highlight_current_tab()
    
    def highlight_editor(self, editor):
        if not editor:
            return
            
        text = editor.get("1.0", "end-1c")
        
        for tag in ["directive", "arabic_directive", "attribute", "comment", 
                    "string", "header", "title_cmd", "style_cmd", "body_cmd", 
                    "button_cmd", "list_cmd", "paragraph"]:
            editor.tag_remove(tag, "1.0", "end")
        
        self.apply_comprehensive_highlighting(editor, text)
    
    def apply_comprehensive_highlighting(self, editor, text):
        lines = text.split('\n')
        line_num = 1
        
        for line in lines:
            self.highlight_line(editor, line, line_num)
            line_num += 1
    
    def highlight_line(self, editor, line, line_num):
        pos = f"{line_num}.0"
        
        english_headers = ["@h1", "@h2", "@h3", "@h4", "@h5", "@h6"]
        arabic_headers = ["@ر1", "@ر2", "@ر3", "@ر4", "@ر5", "@ر6"]
        
        english_title_commands = ["@title"]
        arabic_title_commands = ["@نص"]
        
        english_style_commands = ["@style"]
        arabic_style_commands = ["@مسار"]
        
        english_body_commands = ["@body"]
        arabic_body_commands = ["@جسم"]
        
        english_button_commands = ["@button"]
        arabic_button_commands = ["@زر"]
        
        english_list_commands = ["@ul", "@li"]
        arabic_list_commands = ["@قائمة", "@عنصر"]
        
        english_paragraph_commands = ["@p"]
        arabic_paragraph_commands = ["@فقرة"]
        
        if line.strip().startswith('#'):
            start_pos = f"{line_num}.{line.find('#')}"
            end_pos = f"{line_num}.end"
            editor.tag_add("comment", start_pos, end_pos)
        
        for cmd in english_headers:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("header", start_pos, end_pos)
        
        for cmd in arabic_headers:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("header", start_pos, end_pos)
        
        for cmd in english_title_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("title_cmd", start_pos, end_pos)
        
        for cmd in arabic_title_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("title_cmd", start_pos, end_pos)
        
        for cmd in english_style_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("style_cmd", start_pos, end_pos)
        
        for cmd in arabic_style_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("style_cmd", start_pos, end_pos)
        
        for cmd in english_body_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("body_cmd", start_pos, end_pos)
        
        for cmd in arabic_body_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("body_cmd", start_pos, end_pos)
        
        for cmd in english_button_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("button_cmd", start_pos, end_pos)
        
        for cmd in arabic_button_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("button_cmd", start_pos, end_pos)
        
        for cmd in english_list_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("list_cmd", start_pos, end_pos)
        
        for cmd in arabic_list_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("list_cmd", start_pos, end_pos)
        
        for cmd in english_paragraph_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("paragraph", start_pos, end_pos)
        
        for cmd in arabic_paragraph_commands:
            if cmd in line:
                start_pos = f"{line_num}.{line.find(cmd)}"
                end_pos = f"{start_pos}+{len(cmd)}c"
                editor.tag_add("paragraph", start_pos, end_pos)
        
        if '@onclick=' in line:
            start_idx = line.find('@onclick=')
            start_pos = f"{line_num}.{start_idx}"
            end_pos = f"{line_num}.end"
            editor.tag_add("attribute", start_pos, end_pos)
        
        if '"' in line:
            start_idx = line.find('"')
            if start_idx != -1:
                end_idx = line.find('"', start_idx + 1)
                if end_idx != -1:
                    start_pos = f"{line_num}.{start_idx}"
                    end_pos = f"{line_num}.{end_idx + 1}"
                    editor.tag_add("string", start_pos, end_pos)
    
    def run_code(self, event=None):
        editor = self.get_current_editor()
        if not editor:
            messagebox.showwarning(
                self.t("No File", "لا يوجد ملف"),
                self.t("Open a file first.", "افتح ملفًا أولاً.")
            )
            return
            
        code = editor.get("1.0", "end-1c").strip()
        
        if not code:
            messagebox.showwarning(
                self.t("Empty File", "ملف فارغ"),
                self.t("The editor is empty.", "المحرر فارغ.")
            )
            return
        
        current_tab = self.get_current_tab()
        current_file = self.tab_files.get(current_tab)
        
        if current_file is None or not os.path.exists(current_file):
            if not messagebox.askyesno(
                self.t("Save File", "حفظ الملف"),
                self.t("Save file before running?", "هل تريد حفظ الملف قبل التشغيل؟")
            ):
                return
            self.save_as_file()
            
            if not self.tab_files.get(current_tab):
                return
        
        self.output.delete("1.0", "end")
        self.output.insert("1.0", self.t("Compiling...\n", "جاري الترجمة...\n"))
        self.status.config(text=self.t("Compiling...", "جاري الترجمة..."))
        
        temp_dir = tempfile.mkdtemp()
        temp_shai = os.path.join(temp_dir, "temp.shai")
        temp_html = os.path.join(temp_dir, "output.html")
        
        with open(temp_shai, "w", encoding="utf-8") as f:
            f.write(code)
        
        try:
            compiler_path = "shay-compiler.js"
            if not os.path.exists(compiler_path):
                compiler_path = os.path.join(os.path.dirname(__file__), "shay-compiler.js")
            
            self.output.insert("end", self.t(f"Using compiler: {compiler_path}\n", 
                                            f"جاري استخدام المترجم: {compiler_path}\n"))
            
            result = subprocess.run(["node", compiler_path, temp_shai, temp_html], 
                                   capture_output=True, text=True, shell=True)
            
            self.output.delete("1.0", "end")
            
            if result.stdout:
                self.output.insert("1.0", result.stdout)
            
            if result.returncode == 0:
                if os.path.exists(temp_html):
                    webbrowser.open(f"file:///{temp_html.replace(os.sep, '/')}")
                    success_msg = self.t("\n✓ Compiled successfully! Opening in browser...\n", 
                                       "\n✓ تم الترجمة بنجاح! جاري الفتح في المتصفح...\n")
                    self.output.insert("end", success_msg)
                    self.status.config(text=self.t("Running in browser...", "جاري التشغيل في المتصفح..."))
                else:
                    error_msg = self.t("\n✗ Output file not created\n", 
                                     "\n✗ لم يتم إنشاء ملف الإخراج\n")
                    self.output.insert("end", error_msg)
            else:
                error_msg = self.t("\n✗ Compilation failed:\n", 
                                 "\n✗ فشلت الترجمة:\n")
                self.output.insert("end", error_msg)
                if result.stderr:
                    self.output.insert("end", result.stderr)
                    
        except FileNotFoundError:
            error_msg = self.t("\n✗ Node.js not found! Install Node.js to compile.\n",
                             "\n✗ Node.js غير موجود! قم بتثبيت Node.js للترجمة.\n")
            self.output.insert("end", error_msg)
        except Exception as e:
            error_msg = self.t(f"\n✗ Error: {str(e)}\n", f"\n✗ خطأ: {str(e)}\n")
            self.output.insert("end", error_msg)
        
        self.output.see("end")
        self.bottom_notebook.select(self.output_frame)
        
    def compile_only(self):
        self.run_code()
    
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
            except:
                pass
                
    def redo(self, event=None):
        editor = self.get_current_editor()
        if editor:
            try:
                editor.edit_redo()
            except:
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
                "Shai IDE v1.0\nA development environment for Shai language\n\nShai is a simple markup language for web development.",
                "بيئة شاي الإصدار 1.0\nبيئة تطوير للغة شاي\n\nشاي هي لغة ترميز بسيطة لتطوير الويب."
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
