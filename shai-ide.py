import tkinter as tk
from tkinter import ttk, scrolledtext
import re

class ShaiIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Shai-lang IDE - VS Code Style")
        
        # VS Code-like dark theme
        self.root.configure(bg="#1e1e1e")
        
        # Configure window
        self.root.geometry("1000x700")
        
        # Create menu
        self.create_menu()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add editor tab
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="shai_script.shai")
        
        # Create widgets
        self.create_widgets()
        
        # Autocomplete variables
        self.autocomplete_words = ["func", "if", "else", "while", "for", "return"]
        self.setup_autocomplete()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.config(menu=menubar)
        
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
        
        # Bottom panel
        self.bottom_panel = ttk.Frame(self.root, height=200)
        self.bottom_panel.pack(fill=tk.X)
        
        # Output display
        self.output = scrolledtext.ScrolledText(
            self.bottom_panel,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            state="normal"
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#007acc",
            fg="white"
        )
        self.status.pack(fill=tk.X)
        
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
        
    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        
        # Clear output
        self.output.delete("1.0", tk.END)
        
        # TODO: Execute shai-lang code here
        # For now just display the code
        self.output.insert(tk.END, "Executing shai-lang code...\n\n", "output")
        self.output.insert(tk.END, code, "output")
        
        self.status.config(text="Execution completed")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShaiIDE(root)
    root.mainloop()
