import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import re
import os

class ShaiIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("بيئة تطوير شاي")
        
        # VS Code-like dark theme
        self.root.configure(bg="#1e1e1e")
        
        # Configure window
        self.root.geometry("1200x800")
        
        # Create menu
        self.create_menu()
        
        # Main paned window
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (Explorer)
        self.sidebar = ttk.Frame(self.main_pane, width=200)
        self.main_pane.add(self.sidebar)
        
        # Create file explorer
        self.create_explorer()
        
        # Editor area
        self.editor_area = ttk.Frame(self.main_pane)
        self.main_pane.add(self.editor_area)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.editor_area)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add editor tab
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="shai_script.shai")
        
        # Create widgets
        self.create_widgets()
        
        # Autocomplete variables
        self.autocomplete_words = ["func", "if", "else", "while", "for", "return"]
        self.setup_autocomplete()
        
        # Create bottom panel (terminal + REPL)
        self.create_bottom_panel()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="جديد", command=self.new_file)
        file_menu.add_command(label="فتح", command=self.open_file)
        file_menu.add_command(label="فتح مجلد", command=self.open_folder)
        file_menu.add_command(label="حفظ", command=self.save_file)
        file_menu.add_command(label="إنشاء ملف شاي", command=self.create_shai_file)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        menubar.add_cascade(label="ملف", menu=file_menu)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="نفذ", command=self.run_code)
        run_menu.add_command(label="تصحيح")
        menubar.add_cascade(label="تشغيل", menu=run_menu)
        
        self.root.config(menu=menubar)
        
    def create_explorer(self):
        # Explorer header
        explorer_header = ttk.Label(self.sidebar, text="المستكشف", style="Header.TLabel")
        explorer_header.pack(fill=tk.X, padx=5, pady=5)
        
        # File tree
        self.file_tree = ttk.Treeview(self.sidebar)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure treeview columns
        self.file_tree["columns"] = ("path")
        self.file_tree.column("#0", width=300, minwidth=200)
        self.file_tree.column("path", width=0, stretch=tk.NO)
        
        # Bind double click to open files/folders
        self.file_tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Add current directory files
        self.refresh_explorer()
        
    def refresh_explorer(self, folder="."):
        self.file_tree.delete(*self.file_tree.get_children())
        try:
            for item in os.listdir(folder):
                full_path = os.path.join(folder, item)
                if os.path.isdir(full_path):
                    node = self.file_tree.insert("", "end", text=f"📁 {item}", values=[full_path])
                    # Add dummy child to make folder expandable
                    self.file_tree.insert(node, "end", text="Loading...")
                else:
                    self.file_tree.insert("", "end", text=f"📄 {item}", values=[full_path])
        except PermissionError:
            self.file_tree.insert("", "end", text="⚠️ Access Denied")

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            os.chdir(folder)
            self.refresh_explorer(folder)
        
    def create_widgets(self):
        # Code editor
        self.editor = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            undo=True
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Syntax highlighting tags
        self.editor.tag_configure("keyword", foreground="#569cd6")
        self.editor.tag_configure("string", foreground="#ce9178")
        self.editor.tag_configure("comment", foreground="#6a9955")
        
        # Bind key events
        self.editor.bind("<KeyRelease>", self.on_key_release)
        
        # Status bar
        self.status = tk.Label(
            self.editor_area,
            text="جاهز",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#007acc",
            fg="white"
        )
        self.status.pack(fill=tk.X)
        
    def create_bottom_panel(self):
        # Bottom panel notebook
        self.bottom_notebook = ttk.Notebook(self.root)
        self.bottom_notebook.pack(fill=tk.BOTH, expand=False)
        
        # Output tab
        self.output_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.output_frame, text="النتائج")
        
        self.output = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            state="normal"
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # REPL tab (Python IDLE style)
        self.repl_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.repl_frame, text="طرفية")
        
        self.repl_output = scrolledtext.ScrolledText(
            self.repl_frame,
            wrap=tk.WORD,
            height=4,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            state="normal"
        )
        self.repl_output.pack(fill=tk.BOTH, expand=True)
        
        self.repl_input = tk.Entry(
            self.repl_frame,
            font=("Consolas", 11),
            bg="#252526",
            fg="#d4d4d4",
            insertbackground="white"
        )
        self.repl_input.pack(fill=tk.X, pady=5)
        self.repl_input.bind("<Return>", self.eval_repl)
        
        # Terminal tab
        self.terminal_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.terminal_frame, text="محطة")
        
        self.terminal = scrolledtext.ScrolledText(
            self.terminal_frame,
            wrap=tk.WORD,
            height=8,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            state="normal"
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
    def setup_autocomplete(self):
        self.editor.bind("<Tab>", self.handle_autocomplete)
        
    def handle_autocomplete(self, event):
        # Get current word
        word = self.get_current_word()
        
        if word:
            matches = [w for w in self.autocomplete_words if w.startswith(word)]
            if matches:
                self.editor.insert(tk.INSERT, matches[0][len(word):])
                return "break"
        return None
        
    def new_file(self):
        new_tab = ttk.Frame(self.notebook)
        editor = scrolledtext.ScrolledText(
            new_tab,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        editor.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(new_tab, text="Untitled.shai")
        self.notebook.select(new_tab)
        
    def on_tree_double_click(self, event):
        item = self.file_tree.selection()[0]
        path = self.file_tree.item(item, "values")[0]
        
        if os.path.isdir(path):
            # Expand/collapse folder
            if self.file_tree.item(item, "open"):
                self.file_tree.item(item, open=False)
                # Clear children
                for child in self.file_tree.get_children(item):
                    self.file_tree.delete(child)
            else:
                # Load folder contents
                self.file_tree.item(item, open=True)
                for child in self.file_tree.get_children(item):
                    self.file_tree.delete(child)
                
                try:
                    for item_name in os.listdir(path):
                        full_path = os.path.join(path, item_name)
                        if os.path.isdir(full_path):
                            node = self.file_tree.insert(item, "end", text=f"📁 {item_name}", values=[full_path])
                            # Add dummy child to make folder expandable
                            self.file_tree.insert(node, "end", text="Loading...")
                        else:
                            self.file_tree.insert(item, "end", text=f"📄 {item_name}", values=[full_path])
                except PermissionError:
                    self.file_tree.insert(item, "end", text="⚠️ Access Denied")
        else:
            # Open file in editor
            with open(path, "r") as f:
                content = f.read()
            
            new_tab = ttk.Frame(self.notebook)
            editor = scrolledtext.ScrolledText(
                new_tab,
                wrap=tk.WORD,
                font=("Consolas", 12),
                bg="#1e1e1e",
                fg="#d4d4d4"
            )
            editor.pack(fill=tk.BOTH, expand=True)
            editor.insert("1.0", content)
            
            self.notebook.add(new_tab, text=os.path.basename(path))
            self.notebook.select(new_tab)

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Shai files", "*.shai")])
        if filepath:
            with open(filepath, "r") as f:
                content = f.read()
            
            new_tab = ttk.Frame(self.notebook)
            editor = scrolledtext.ScrolledText(
                new_tab,
                wrap=tk.WORD,
                font=("Consolas", 12),
                bg="#1e1e1e",
                fg="#d4d4d4"
            )
            editor.pack(fill=tk.BOTH, expand=True)
            editor.insert("1.0", content)
            
            self.notebook.add(new_tab, text=os.path.basename(filepath))
            self.notebook.select(new_tab)
            
    def create_shai_file(self):
        """Create a new Shai file with web redirect template"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".shai",
            filetypes=[("Shai files", "*.shai")]
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("""
@نص صفحتي الأولى بشاي
@مسار main.css

@body
  @ر1 مرحبًا بالعالم!
  @فقرة هذه فقرة مكتوبة بلغة شاي الترميزية.
  @قائمة
    @عنصر عنصر 1
    @عنصر عنصر 2
  @زر انقر هنا @onclick="alert('مرحبًا!')"
""")
            
            # Open the new file in editor
            new_tab = ttk.Frame(self.notebook)
            editor = scrolledtext.ScrolledText(
                new_tab,
                wrap=tk.WORD,
                font=("Consolas", 12),
                bg="#1e1e1e",
                fg="#d4d4d4"
            )
            editor.pack(fill=tk.BOTH, expand=True)
            editor.insert("1.0", open(filepath, encoding='utf-8').read())
            
            self.notebook.add(new_tab, text=os.path.basename(filepath))
            self.notebook.select(new_tab)
            
            # Refresh explorer
            self.refresh_explorer()
            
    def save_file(self):
        current_tab = self.notebook.select()
        if current_tab:
            editor = self.notebook.nametowidget(current_tab).winfo_children()[0]
            content = editor.get("1.0", tk.END)
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".shai",
                filetypes=[("Shai files", "*.shai")]
            )
            if filepath:
                with open(filepath, "w") as f:
                    f.write(content)
                self.notebook.tab(current_tab, text=os.path.basename(filepath))
        
    def get_current_word(self):
        pos = self.editor.index(tk.INSERT)
        line = pos.split('.')[0]
        col = pos.split('.')[1]
        
        # Get line text
        line_text = self.editor.get(f"{line}.0", f"{line}.end")
        
        # Find current word
        words = re.findall(r'\w+', line_text)
        if not words:
            return None
            
        # Find word at cursor position
        col_num = int(col)
        word_start = 0
        for word in words:
            word_start = line_text.find(word, word_start)
            word_end = word_start + len(word)
            if word_start <= col_num <= word_end:
                return word
            word_start = word_end
        return None
        
    def on_key_release(self, event):
        # Simple syntax highlighting
        self.highlight_syntax()
        
    def highlight_syntax(self):
        text = self.editor.get("1.0", tk.END)
        
        # Remove previous tags
        for tag in ["keyword", "string", "comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
        
        # Highlight keywords
        for word in self.autocomplete_words:
            start = "1.0"
            while True:
                pos = self.editor.search(r'\m{}\M'.format(word), start, stopindex=tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(word)}c"
                self.editor.tag_add("keyword", pos, end)
                start = end
                
        # TODO: Add more syntax highlighting rules
        
    def eval_repl(self, event):
        code = self.repl_input.get()
        self.repl_input.delete(0, tk.END)
        
        self.repl_output.insert(tk.END, f">>> {code}\n", "input")
        
        try:
            # TODO: Execute shai-lang code here
            result = f"Result: {code}"  # Placeholder
            self.repl_output.insert(tk.END, f"{result}\n", "output")
        except Exception as e:
            self.repl_output.insert(tk.END, f"Error: {str(e)}\n", "error")
            
        self.repl_output.see(tk.END)
        
    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        self.output.delete("1.0", tk.END)
        
        import webbrowser
        import tempfile
        import os

        # Create Shai runtime HTML wrapper with debug output
        # Get absolute path to shay-runtime.js (look in both current dir and script dir)
        runtime_path = None
        possible_paths = [
            os.path.abspath("shay-runtime.js"),
            os.path.join(os.path.dirname(__file__), "shay-runtime.js")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                runtime_path = path
                break
        
        # Arabic HTML tag translations
        arabic_tags = {
            'a': 'رابط',
            'abbr': 'اختصار',
            'address': 'عنوان',
            'article': 'مقال',
            'aside': 'جانبي',
            'audio': 'صوت',
            'b': 'عريض',
            'blockquote': 'اقتباس',
            'body': 'جسم',
            'br': 'سطر-جديد',
            'button': 'زر',
            'canvas': 'لوحة',
            'caption': 'شرح',
            'cite': 'استشهاد',
            'code': 'كود',
            'col': 'عمود',
            'colgroup': 'مجموعة-أعمدة',
            'dd': 'وصف-مصطلح',
            'del': 'محذوف',
            'details': 'تفاصيل',
            'dfn': 'تعريف',
            'div': 'قسم',
            'dl': 'قائمة-تعريفات',
            'dt': 'مصطلح',
            'em': 'تأكيد',
            'embed': 'تضمين',
            'fieldset': 'مجموعة-حقول',
            'figcaption': 'شرح-شكل',
            'figure': 'شكل',
            'footer': 'تذييل',
            'form': 'نموذج',
            'h1': 'عنوان1',
            'h2': 'عنوان2',
            'h3': 'عنوان3',
            'h4': 'عنوان4',
            'h5': 'عنوان5',
            'h6': 'عنوان6',
            'head': 'رأس',
            'header': 'رأس-صفحة',
            'hr': 'فاصل',
            'html': 'لغة-توصيف-النص-الفائق',
            'i': 'مائل',
            'iframe': 'إطار-مضمن',
            'img': 'صورة',
            'input': 'إدخال',
            'ins': 'مضاف',
            'kbd': 'لوحة-مفاتيح',
            'label': 'تسمية',
            'legend': 'شرح',
            'li': 'عنصر-قائمة',
            'link': 'رابط',
            'main': 'رئيسي',
            'map': 'خريطة',
            'mark': 'تمييز',
            'menu': 'قائمة',
            'meta': 'بيانات',
            'meter': 'عداد',
            'nav': 'تنقل',
            'noscript': 'بدون-سكربت',
            'object': 'كائن',
            'ol': 'قائمة-مرقمة',
            'optgroup': 'مجموعة-خيارات',
            'option': 'خيار',
            'output': 'خرج',
            'p': 'فقرة',
            'param': 'معيار',
            'picture': 'صورة',
            'pre': 'مسبق-التنسيق',
            'progress': 'تقدم',
            'q': 'اقتباس-قصير',
            'rp': 'دعم-روبي',
            'rt': 'شرح-روبي',
            'ruby': 'روبي',
            's': 'مشطوب',
            'samp': 'عينة',
            'script': 'سكربت',
            'section': 'قسم',
            'select': 'اختيار',
            'small': 'صغير',
            'source': 'مصدر',
            'span': 'امتداد',
            'strong': 'قوي',
            'style': 'تنسيق',
            'sub': 'منخفض',
            'summary': 'ملخص',
            'sup': 'مرتفع',
            'table': 'جدول',
            'tbody': 'جسم-جدول',
            'td': 'خلية-جدول',
            'template': 'قالب',
            'textarea': 'منطقة-نص',
            'tfoot': 'تذييل-جدول',
            'th': 'رأس-خلية',
            'thead': 'رأس-جدول',
            'time': 'وقت',
            'title': 'عنوان',
            'tr': 'صف-جدول',
            'track': 'مسار',
            'u': 'تحته-خط',
            'ul': 'قائمة-غير-مرقمة',
            'var': 'متغير',
            'video': 'فيديو',
            'wbr': 'فاصل-كلمة'
        }

        # Replace HTML tags with Arabic equivalents in the code
        for eng, arb in arabic_tags.items():
            code = code.replace(f'<{eng}', f'<{arb}').replace(f'</{eng}>', f'</{arb}>')
        
        escaped_code = code.replace('`', '\\`').replace('${', '\\${')
        # Verify runtime file exists
        if not runtime_path or not os.path.exists(runtime_path):
            # Copy runtime file to temp dir if not found
            import shutil
            temp_dir = tempfile.mkdtemp()
            runtime_path = os.path.join(temp_dir, "shay-runtime.js")
            shutil.copy2(os.path.join(os.path.dirname(__file__), "shay-runtime.js"), runtime_path)
            self.output.insert(tk.END, f"Copied runtime to temp location: {runtime_path}\n", "output")

        shai_content = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script>
    console.log('Loading shay-runtime.js from: {0}');
  </script>
  <script src="file:///{0}"></script>
  <style>
    /* Default styles */
    body {{
      margin: 0;
      padding: 20px;
      font-family: Arial;
      background: #1e1e1e;
      color: white;
    }}
    shai-element {{
      display: block;
      border: 1px solid #569cd6;
      padding: 10px;
      margin: 10px 0;
    }}
  </style>
</head>
<body>
  <script>
    try {{
      console.log('Initializing Shai Runtime...');
      const runtime = new ShayRuntime();
      
      console.log('Executing Shai code...');
      runtime.execute(`{1}`);
      
      console.log('Code executed successfully!');
      
      console.log('Shai app mounted successfully!');
    }} catch (e) {{
      console.error('Shai Runtime Error:', e);
      document.body.innerHTML = `
        <div style="color: red; padding: 20px;">
          <h2>Shai Runtime Error</h2>
          <pre>${{e.stack}}</pre>
        </div>
      `;
    }}
  </script>
</body>
</html>""".format(
    runtime_path.replace(os.sep, '/'),
    escaped_code
)
        
        # Save as temporary file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            f.write(shai_content.encode('utf-8'))
            temp_path = f.name
            
        # Open in browser
        webbrowser.open(f'file:///{temp_path.replace(os.sep, "/")}')
        
        # Display status
        self.status.config(text="تم تشغيل تطبيق شاي باستخدام المترجم")
        self.output.insert(tk.END, "Running with Shai compiler...\n", "output")
        
        # Focus on terminal
        self.bottom_notebook.select(self.terminal_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShaiIDE(root)
    root.mainloop()
