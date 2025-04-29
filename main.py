import tkinter, re, sqlite3, os, sys
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.colorchooser import *
from tkinter.filedialog import *

KEYWORDS = ["print", "input", "type", "if", "repeats", "inf"]
BRACKETS = ["{", "}", "(", ")", "[", "]"]
COMMENT_SYMBOL = "#"

completion_menu = None
current_matches = []

themes_list = {}

def get_themes(voider=""):
    """
    Read themes from themes.db and save them to themes_list.
    
    themes_list is a dictionary where the key is the theme name and the value is a
    dictionary with keys "bg" and "fg" which are the colours of the background and
    foreground of the theme respectively.
    """
    global themes_list
    themes = sqlite3.connect(r"themes.db")
    cursor = themes.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS themes (
        name TEXT PRIMARY KEY,
        bg TEXT,
        fg TEXT
    )""")
    themes_data = [
        ("Light", "#FFFFFF", "#000000"),
        ("Dark", "#E1E1E1", "#FFFFFF"),
        ("Solarized Light", "#FDF6E3", "#1e1e1e"),
        ("Solarized Dark", "#002B36", "#ffffff")
    ]
    for theme in themes_data:
        name, bg, fg = theme
        cursor.execute("SELECT 1 FROM themes WHERE name = ?", (name,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO themes (name, bg, fg) VALUES (?, ?, ?)", (name, bg, fg))
        else: continue
    themes.commit()
    cursor.execute("SELECT name, bg, fg FROM themes")
    result = cursor.fetchall()
    themes.close()
    for i in range(len(result)):
        themes_list[result[i][0]] = {"bg": result[i][1], "fg": result[i][2]}
    
get_themes()

current_theme = themes_list["Dark"]

def show_about(voider=""):
    """
    Displays an informational message box with details about Rolton IDE.
    """
    showinfo("About Rolton IDE", "Rolton IDE is a IDE for RoltonLang")

def on_closing():
    """
    Asks the user if he wants to save the file before closing the window and closes the window if the answer is yes or if the file is already saved.
    If the answer is no, the function does nothing.
    """
    current_text = textarea.get("1.0", END)
    if not current_text:
        sys.exit(0)
    elif current_text != buffer_text or current_text != "":
        if not (not buffer_text and not file_adress):
            result = askyesnocancel("Unsaved Changes", "You have unsaved changes. Save before closing?")
            if result is None:
                return
            elif result:
                if not saving_file():
                    return
        else:
            pass
    sys.exit(0)

def new_file(voider=""):
    """
    Deletes all text in the text area and resets the file_adress variable to an empty string.
    The title of the window is changed to "Rolton IDE - new file".
    """
    global file_adress, buffer_text
    buffer_text = textarea.get("1.0", END)
    textarea.delete("1.0", END)
    file_adress = ""
    wnd.title(f"Rolton IDE - new file")

def saving_file(voider=""):
    """
    Saves the current file. If file_obj is empty, shows an info box with the message "File not saved" and returns False.
    If file_obj is not empty, saves the file and shows an info box with the message "File saved successfully" and returns True.
    """
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
    """
    Opens a new file in the text area.

    This function asks the user to select a file using the file dialog,
    reads the contents of the file and inserts it into the text area.
    If the user cancels the file dialog, shows an info box with the message
    "File not opened".
    """
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
    """
    Reverts the text area to the previous state stored in buffer_text.

    This function clears the current content of the text area and replaces
    it with the text stored in buffer_text, effectively undoing any changes
    made since the last save or buffer update.
    """
    global buffer_text
    textarea.delete("1.0", END)
    textarea.insert("1.0", buffer_text)
    buffer_text = textarea.get("1.0", END)

def redo_text(voider=""):
    """
    Reverts the text area to the next state stored in buffer_text.

    This function clears the current content of the text area and replaces
    it with the text stored in buffer_text, effectively redoing any changes
    that were undone since the last save or buffer update.
    """
    global buffer_text
    current_text = textarea.get("1.0", END)
    textarea.delete("1.0", END)
    textarea.insert("1.0", buffer_text)
    buffer_text = current_text

def run_file(voider=""):
    """
    Shows a warning dialog with the message "For run file, please, use the terminal".
    """
    showwarning("Run file", "For run file, please, use the terminal")

def insert_quotes(event, quote_type='"'):
    """
    Inserts a pair of quotes at the current cursor position in the text widget.

    This function inserts a specified type of quote twice at the current cursor
    position in the widget associated with the given event. The cursor is then
    moved between the inserted pair of quotes.
    """
    widget = event.widget
    current_pos = widget.index(INSERT)
    widget.insert(current_pos, f"{quote_type}{quote_type}")
    new_pos = f"{current_pos}+1c"
    widget.mark_set(INSERT, new_pos)
    return "break"

def insert_braces(event, brace_type="{}"):
    """
    Inserts a pair of braces at the current cursor position in the text widget.

    This function inserts the specified type of braces at the current cursor
    position in the widget associated with the given event. The cursor is then
    moved between the inserted pair of braces.
    """
    widget = event.widget
    current_pos = widget.index(INSERT)
    widget.insert(current_pos, brace_type)
    new_pos = f"{current_pos}+1c"
    widget.mark_set(INSERT, new_pos)
    return "break"

def autocomplete(event):
    """
    A function that completes the current word in the text widget by showing a
    pop up menu with matching words from the KEYWORDS list.

    This function is called when the user presses the tab key while typing in the
    text widget.

    If there are no matches, the function returns None. Otherwise, it inserts the
    selected item from the menu into the text widget and returns "break" to stop
    the event from propagating further.

    If the user has not typed any word yet, the function simply returns None.
    """
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
    """
    Inserts the selected completion into the text widget, replacing the current
    word and any text after it.

    This function is called when the user selects a completion from the pop up
    menu. It destroys the menu, determines the current word, and inserts the
    selected completion after the current word. The cursor is then placed at the
    end of the inserted text.
    """
    global completion_menu
    if completion_menu:
        completion_menu.destroy()
        completion_menu = None
    current_word = get_current_word()
    replacement = text[len(current_word):]
    textarea.insert(INSERT, replacement)

def get_current_word():
    """
    Returns the word that the user is currently typing in the text widget.

    This function uses the current cursor position to determine which line the
    user is currently typing in and which column the user is currently at. It
    then splits the line into two parts: the part before the user and the part
    after the user. It uses a regular expression to find the last word in the
    part before the user, and returns that word.

    If there is no word before the user, or if the user is at the start of the
    line, the function returns an empty string.
    """
    cursor_pos = textarea.index(INSERT)
    line_number, column_number = map(int, cursor_pos.split('.'))
    line = textarea.get(f"{line_number}.0", f"{line_number}.end")
    before_cursor = line[:column_number]
    match = re.search(r'[\w_]+$|$', before_cursor)
    return match.group(0) if match else ""

def on_key_press(event):
    """
    Handles key presses in the text widget, providing various auto-completion and
    auto-formatting features.

    If the user presses a quote mark, inserts a matching closing quote mark.
    If the user presses an opening brace (e.g. '{', '('), inserts a matching
    closing brace.
    If the user presses the escape key, destroys any pop up menu that is currently
    displayed.
    If the user presses the tab key, shows a pop up menu of matching words from
    the KEYWORDS list.
    If the user presses the up or down arrow keys while a pop up menu is displayed,
    selects the previous or next item in the menu, respectively.

    Returns "break" to stop the event from propagating further, if the key press
    was handled by this function.
    """
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

def zoom_in(voider=""):
    """
    Increases the font size of the text widget by one.

    This function takes an optional argument, which is ignored.
    """
    global font_size
    font_size += 1
    textarea.config(font=(font_name, font_size))

def zoom_out(voider=""):
    """
    Decreases the font size of the text widget by one.

    This function takes an optional argument, which is ignored.
    """
    global font_size
    font_size -= 1
    textarea.config(font=(font_name, font_size))

def apply_theme(theme_name):
    """
    Applies a theme to the text widget.

    Notes
    -----
    If the theme name is not found in themes_list, the text widget's current
    theme is not changed.
    """
    global current_theme
    if theme_name in themes_list:
        current_theme = themes_list[theme_name]
        textarea.config(
            background=current_theme["bg"],
            foreground=current_theme["fg"]
        )

def add_theme():
    """
    Opens a window to create a new theme.

    The user can input the name of the theme and choose the background and foreground colors.

    The theme is added to the menu after creation.
    """
    def get_color_and_name():
        """
        Opens a window to create a new theme.
    
        The user can input the name of the theme and choose the background and foreground colors.
    
        The theme is added to the menu after creation.
    
        Returns
        -------
        tuple
            A tuple containing the name of the theme and the background and foreground colors as strings.
        """
        
        result = None
        color1 = "#FFFFFF"
        color2 = "#000000"

        def choose_color1():
            """
            Opens a color chooser dialog to select a background color.
            
            This function uses the askcolor dialog to allow the user to select a background
            color. If a color is selected, it updates the color1 variable and changes the 
            background of button1 to the chosen color.
            """
            nonlocal color1
            code = askcolor(parent=root, title="Select background color")
            root.focus_set()
            if code[1]:
                color1 = code[1]
                button1.config(bg=color1)

        def choose_color2():
            """
            Opens a color chooser dialog to select a foreground color.
            
            This function uses the askcolor dialog to allow the user to select a foreground
            color. If a color is selected, it updates the color2 variable and changes the 
            background of button2 to the chosen color.
            """
            nonlocal color2
            code = askcolor(parent=root, title="Select foreground color")
            root.focus_set()
            if code[1]:
                color2 = code[1]
                button2.config(bg=color2)


        def on_ok():
            """
            Handles the OK button click event.
            
            This function retrieves the theme name from the entry widget and checks if it is non-empty.
            If the name is valid, it stores the theme name along with the selected background and
            foreground colors in the result variable and closes the window. If the name is empty, it
            displays a warning message to prompt the user to enter a theme name.
            """

            nonlocal result
            name = entry.get().strip()
            if not name:
                showwarning("Theme creating process error!", "Enter the theme name!")
                return
            result = (name, color1, color2)
            root.destroy()

        root = Tk()
        root.title("Theme creating menu")
        root.geometry("300x200")

        Label(root, text="Background:").grid(row=0, column=0, padx=10, pady=5)
        button1 = tkinter.Button(
            root,
            bg=color1,
            width=10,
            command=choose_color1
        )
        button1.grid(row=0, column=1, padx=10, pady=5)

        Label(root, text="Foreground:").grid(row=1, column=0, padx=10, pady=5)
        button2 = tkinter.Button(
            root,
            bg=color2,
            width=10,
            command=choose_color2
        )
        button2.grid(row=1, column=1, padx=10, pady=5)

        Label(root, text="Name:").grid(row=2, column=0, padx=10, pady=5)
        entry = Entry(root, width=30)
        entry.grid(row=2, column=1, padx=10, pady=5)

        ok_button = tkinter.Button(
            root,
            text="OK",
            command=on_ok,
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        ok_button.grid(row=3, column=0, columnspan=2, pady=15)

        root.resizable(False, False)
        root.mainloop()
        root.focus_set()
        return result

    result_func = get_color_and_name()

    getted_text, bg_color, fg_color = result_func if result_func != None else ("User-theme", "#000000", "#FFFFFF")

    themes = sqlite3.connect(r"themes.db")
    themes_list[theme_name] = {"bg": bg_color, "fg": fg_color}
    cursor = themes.cursor()
    cursor.execute("INSERT INTO themes (name, bg, fg) VALUES (?, ?, ?)", (getted_text, bg_color, fg_color))
    themes.commit()
    themes.close()
    menu_theme.add_command(
        label=theme_name,
        command=lambda t=getted_text: apply_theme(t)
    )

def delete_data(voider=""):
    """
    Deletes all user themes from the database and restarts the program.

    This function is called when the user selects "Delete data" from the "Theme" menu.
    It asks the user if they are sure they want to delete all user themes, and if they
    confirm, it deletes all user themes from the database and restarts the program.
    """
    askquestion = tkinter.messagebox.askquestion(
        "Delete data",
        "You really want to delete all user themes?",
        icon="warning"
    )

    if askquestion == "yes":
        themes = sqlite3.connect(r"themes.db")
        cursor = themes.cursor()
        cursor.execute("DELETE FROM themes")
        cursor.execute("CREATE TABLE IF NOT EXISTS themes (name TEXT, bg TEXT, fg TEXT)")
        cursor.execute("INSERT INTO themes (name, bg, fg) VALUES (?, ?, ?)", ("Light", "#FFFFFF", "#000000"))
        cursor.execute("INSERT INTO themes (name, bg, fg) VALUES (?, ?, ?)", ("Dark", "#1E1E1E", "#FFFFFF"))
        cursor.execute("INSERT INTO themes (name, bg, fg) VALUES (?, ?, ?)", ("Solarized Light", "#FDF6E3", "#1e1e1e"))
        cursor.execute("INSERT INTO themes (name, bg, fg) VALUES (?, ?, ?)", ("Solarized Dark", "#002B36", "#ffffff"))
        themes.commit()
        themes.close()
        os.system(f"{sys.argv[0]}") # for unix/linux need get path to intepriter!
        sys.exit(0)
    else:
        pass

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
menu_view.add_command(label="Zoom in", command = zoom_in)
menu_view.add_command(label="Zoom out", command = zoom_out)

menu_help = Menu(wnd, tearoff=0)
menu_help.add_command(label="About", command=show_about)

menu_run = Menu(wnd, tearoff=0)
menu_run.add_command(label="Run", command=run_file)

menu_theme = Menu(wnd, tearoff=0)
menu_theme.add_command(label="Add theme", command=add_theme)
menu_theme.add_separator()

menu_settings = Menu(wnd, tearoff=0)
menu_settings.add_command(label="Delete data", command=delete_data)

for theme_name in themes_list:
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
menu_bar.add_cascade(label="Settings", menu=menu_settings)

font_size = 12
font_name = "Courier New"

textarea = Text(wnd, 
    wrap=WORD, 
    font=(font_name, font_size), 
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
wnd.bind("<Control-equal>", zoom_in)
wnd.bind("<Control-minus>", zoom_out)
textarea.bind("<Key>", on_key_press)

wnd.protocol("WM_DELETE_WINDOW", on_closing)

wnd.mainloop()
