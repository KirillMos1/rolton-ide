import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter.filedialog import *

def show_about(voider = ""):
    showinfo("About Rolton IDE", "Rolton IDE is a IDE for RoltonLang")

def new_file(voider = ""):
    global file_adress
    global buffer_text
    buffer_text = textarea.get("1.0", END)
    textarea.delete("1.0", END)
    file_adress = ""
    wnd.title(f"Rolton IDE - new file")

def saving_file(voider = ""):
    global file_adress
    global buffer_text
    file_obj = asksaveasfilename(defaultextension = ".rolton", filetypes=[("RoltonLang Files", "*.rolton")], initialfile="main.rolton", title = "Saving RoltonLang file...")
    if file_obj:
        with open(file_obj, "w") as f:
            f.write(textarea.get("1.0", END))
        buffer_text = textarea.get("1.0", END)
        file_adress = file_obj
        wnd.title(f"Rolton IDE - {file_adress}")
        showinfo("Rolton IDE", "File saved successfully")
    else:
        showinfo("Rolton IDE", "File not saved")

def open_file(voider = ""):
    global file_adress
    global buffer_text
    file_obj = askopenfilename(defaultextension = ".rolton", filetypes=[("RoltonLang Files", "*.rolton")], initialfile="main.rolton", title = "Opening RoltonLang file...")
    buffer_text = textarea.get("1.0", END)
    if file_obj:
        with open(file_obj, "r") as f:
            textarea.delete("1.0", END)
            textarea.insert("1.0", f.read())
        wnd.title(f"Rolton IDE - {file_obj}")
    else:
        showinfo("Rolton IDE", "File not opened")

def undo_text(voider = ""):
    global buffer_text
    textarea.delete("1.0", END)
    textarea.insert("1.0", buffer_text)
    buffer_text = textarea.get("1.0", END)

def redo_text(voider = ""):
    global buffer_text
    current_text = textarea.get("1.0", END)
    textarea.delete("1.0", END)
    textarea.insert("1.0", buffer_text)
    buffer_text = current_text

def run_file(voider = ""):
    showwarning("Run file", "For run file, please, use the terminal")

buffer_text = ""
file_adress = ""

wnd = tkinter.Tk()
wnd.title("Rolton IDE - new file")
wnd.geometry("1200x600")
wnd.resizable(False, False)

menu_file = Menu(wnd, tearoff=0)
menu_file.add_command(label="New file")
menu_file.add_command(label="Open file", command=open_file)
menu_file.add_command(label="Save file", command=saving_file)
menu_file.add_separator()
menu_file.add_command(label="Exit", command=wnd.quit)

menu_edit = Menu(wnd, tearoff=0)
menu_edit.add_command(label="Undo", command=undo_text)
menu_edit.add_command(label="Redo", command=redo_text)

menu_view = Menu(wnd, tearoff=0)
menu_view.add_command(label="Zoom in")
menu_view.add_command(label="Zoom out")

menu_help = Menu(wnd, tearoff=0)
menu_help.add_command(label="About", command = show_about)

menu_run = Menu(wnd, tearoff=0)
menu_run.add_command(label="Run", command=run_file)

menu_bar = Menu(wnd, background="#060573", foreground="white", activebackground="#060573", activeforeground="white")
menu_bar.add_cascade(label="File", menu=menu_file)
menu_bar.add_cascade(label="Edit", menu=menu_edit)
menu_bar.add_cascade(label="View", menu=menu_view)  
menu_bar.add_cascade(label="Help", menu=menu_help)
menu_bar.add_cascade(label="Run", menu=menu_run)

textarea = Text(wnd, wrap=WORD, font=("Courier New", 12), width=600, height=25, background="#949494", foreground="white")
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

wnd.protocol("WM_DELETE_WINDOW", wnd.quit)

wnd.mainloop()