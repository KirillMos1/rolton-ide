import tkinter, re
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *

KEYWORDS = ["print", "input", "type", "if", "repeats", "inf"]
BRACKETS = ["{", "}", "(", ")", "[", "]"]
COMMENT_SYMBOL = "#"

completion_menu = None
current_matches = []

THEMES = {
    "Light": {"bg": "#FFFFFF", "fg": "#000000"},
    "Dark": {"bg": "#1E1E1E", "fg": "#FFFFFF"},
    "Solarized Light": {"bg": "#FDF6E3", "fg": "#1e1e1e"},
    "Solarized Dark": {"bg": "#002B36", "fg": "#ffffff"},
}

current_theme = THEMES["Dark"]

def show_about(voider=""):
    showinfo("About Rolton IDE", "Rolton IDE is a IDE for RoltonLang")

def on_closing():
    current_text = textarea.get("1.0", END)
    if current_text != buffer_text:
        result = askyesnocancel("Unsaved Changes", "You have unsaved changes. Save before closing?")
        if result is None:
            return
        elif result:
            if not saving_file():
                return
    wnd.destroy()

def new_file(voider=""):
    global file_adress, buffer_text
    buffer_text = textarea.get("1.0", END)
    textarea.delete("1.0", END)
    file_adress = ""
    wnd.title(f"Rolton IDE - new file")

def saving_file(voider=""):
    global file_adress, buffer_text
    file_obj = asksaveasfilename(
        defaultextension=".rolton",
        filetypes=[("RoltonLang Files", "*.rolton")],
        initialfile="main.rolton",
        title="Saving RoltonLang file..."
    )
    if file_obj:
        with open(file_obj, "w") as f:
            f.write(textarea.get("1.0", END))
        buffer_text = textarea.get("1.0", END)
        file_adress = file_obj
        showinfo("Rolton IDE", "File saved successfully")
        return True
    else:
        showinfo("Rolton IDE", "File not saved")
        return False

def open_file(voider=""):
    global file_adress, buffer_text
    file_obj = askopenfilename(
        defaultextension=".rolton",
        filetypes=[("RoltonLang Files", "*.rolton")],
        initialfile="main.rolton",
        title="Opening RoltonLang file..."
    )
    buffer_text = textarea.get("1.0", END)
    if file_obj:
        with open(file_obj, "r") as f:
            textarea.delete("1.0", END)
            textarea.insert("1.0", f.read())
        wnd.title(f"Rolton IDE - {file_obj}")
    else:
        showinfo("Rolton IDE", "File not opened")

def undo_text(voider=""):
    global buffer_text
    textarea.delete("1.0", END)
    textarea.insert("1.0", buffer_text)
    buffer_text = textarea.get("1.0", END)

def redo_text(voider=""):
    global buffer_text
    current_text = textarea.get("1.0", END)
    textarea.delete("1.0", END)
    textarea.insert("1.0", buffer_text)
    buffer_text = current_text

def run_file(voider=""):
    showwarning("Run file", "For run file, please, use the terminal")

def insert_quotes(event, quote_type='"'):
    widget = event.widget
    current_pos = widget.index(INSERT)
    widget.insert(current_pos, f"{quote_type}{quote_type}")
    new_pos = f"{current_pos}+1c"
    widget.mark_set(INSERT, new_pos)
    return "break"

def insert_braces(event, brace_type="{}"):
    widget = event.widget
    current_pos = widget.index(INSERT)
    widget.insert(current_pos, brace_type)
    new_pos = f"{current_pos}+1c"
    widget.mark_set(INSERT, new_pos)
    return "break"

def autocomplete(event):
    global completion_menu, current_matches
    current_word = get_current_word()
    if current_word:
        matches = [word for word in KEYWORDS if word.startswith(current_word)]
        if matches:
            if completion_menu:
                completion_menu.destroy()
            completion_menu = Menu(wnd, tearoff=0, bg="white", fg="black")
            for item in matches:
                completion_menu.add_command(
                    label=item,
                    command=lambda text=item: insert_completion(text)
                )
            x, y, _, _ = textarea.bbox("insert")
            if y is not None:
                y += textarea.winfo_rooty() + 20
                completion_menu.post(event.widget.winfo_rootx() + x, y)
            current_matches = matches
            return "break"
        else:
            return None
    else:
        return None

def insert_completion(text):
    global completion_menu
    if completion_menu:
        completion_menu.destroy()
        completion_menu = None
    current_word = get_current_word()
    replacement = text[len(current_word):]
    textarea.insert(INSERT, replacement)

def get_current_word():
    cursor_pos = textarea.index(INSERT)
    line_number, column_number = map(int, cursor_pos.split('.'))
    line = textarea.get(f"{line_number}.0", f"{line_number}.end")
    before_cursor = line[:column_number]
    match = re.search(r'[\w_]+$|$', before_cursor)
    return match.group(0) if match else ""

def on_key_press(event):
    global completion_menu
    char = event.char
    if char == '"':
        return insert_quotes(event)
    elif char == "'":
        return insert_quotes(event, quote_type="'")
    elif char == "{":
        return insert_braces(event)
    elif char == "(":
        return insert_braces(event, brace_type="()")
    elif char == "[":
        return insert_braces(event, brace_type="[]")
    elif char == "\x1b":
        if completion_menu:
            completion_menu.destroy()
            completion_menu = None
        return "break"
    elif char == "\t":
        return autocomplete(event)
    elif event.keysym == "Down" and completion_menu:
        completion_menu.tk.call(completion_menu, "activate", "next")
        return "break"
    elif event.keysym == "Up" and completion_menu:
        completion_menu.tk.call(completion_menu, "activate", "prev")
        return "break"

def apply_theme(theme_name):
    global current_theme
    if theme_name in THEMES:
        current_theme = THEMES[theme_name]
        textarea.config(
            background=current_theme["bg"],
            foreground=current_theme["fg"]
        )

buffer_text = ""
file_adress = ""

wnd = tkinter.Tk()
wnd.title("Rolton IDE - new file")
wnd.geometry("1200x600")
wnd.resizable(False, False)

menu_file = Menu(wnd, tearoff=0)
menu_file.add_command(label="New file", command=new_file)
menu_file.add_command(label="Open file", command=open_file)
menu_file.add_command(label="Save file", command=saving_file)
menu_file.add_separator()
menu_file.add_command(label="Exit", command=on_closing)

menu_edit = Menu(wnd, tearoff=0)
menu_edit.add_command(label="Undo", command=undo_text)
menu_edit.add_command(label="Redo", command=redo_text)

menu_view = Menu(wnd, tearoff=0)
menu_view.add_command(label="Zoom in")
menu_view.add_command(label="Zoom out")

menu_help = Menu(wnd, tearoff=0)
menu_help.add_command(label="About", command=show_about)

menu_run = Menu(wnd, tearoff=0)
menu_run.add_command(label="Run", command=run_file)

menu_theme = Menu(wnd, tearoff=0)
for theme_name in THEMES:
    menu_theme.add_command(
        label=theme_name,
        command=lambda t=theme_name: apply_theme(t)
    )

menu_bar = Menu(wnd, 
    background="#060573", 
    foreground="white",   
    activebackground="#060573",
    activeforeground="white"   
)
menu_bar.add_cascade(label="File", menu=menu_file)
menu_bar.add_cascade(label="Edit", menu=menu_edit)
menu_bar.add_cascade(label="View", menu=menu_view)  
menu_bar.add_cascade(label="Help", menu=menu_help)
menu_bar.add_cascade(label="Run", menu=menu_run)
menu_bar.add_cascade(label="Theme", menu=menu_theme)

textarea = Text(wnd, 
    wrap=WORD, 
    font=("Courier New", 12), 
    width=600, 
    height=25, 
    background=current_theme["bg"], 
    foreground=current_theme["fg"]
)
textarea.pack(fill=BOTH, expand=True)

scrollbar = Scrollbar(wnd, orient=VERTICAL, command=textarea.yview)
scrollbar.pack(side=RIGHT, fill=Y)

scrollbar2 = Scrollbar(wnd, orient=HORIZONTAL, command=textarea.xview)
scrollbar2.pack(side=BOTTOM, fill=X)

textarea.config(yscrollcommand=scrollbar.set)
textarea.config(xscrollcommand=scrollbar2.set)

scrollbar.config(command=textarea.yview)
scrollbar2.config(command=textarea.xview)

textarea.focus_set()

wnd.columnconfigure(0, weight=1)
wnd.rowconfigure(0, weight=1)

wnd.config(menu=menu_bar)

wnd.bind("<Control-n>", new_file)
wnd.bind("<Control-o>", open_file)
wnd.bind("<Control-s>", saving_file)
wnd.bind("<Control-z>", undo_text)
wnd.bind("<Control-y>", redo_text)
wnd.bind("<Control-r>", run_file)
textarea.bind("<Key>", on_key_press)

wnd.protocol("WM_DELETE_WINDOW", on_closing)

wnd.mainloop()
