import tkinter.messagebox
from customtkinter import *
import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3

#Connecting sqlite database
connection = sqlite3.connect("databases/branches.db")
#Turning foreign key constraints on
connection.execute("PRAGMA foreign_keys = ON")
#Initializing cursor
db = connection.cursor()

root = CTk()
root.geometry("1000x900")
root.title("Branch Notes")
root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=2)
root.rowconfigure(1, weight=1)

#Frames
logoframe = CTkFrame(root)
textframe = CTkFrame(root)
exploreframe = CTkFrame(root)

#Placing Frames
textframe.grid(row=1,
                column=1,
                sticky="nswe",
                rowspan=3,
                padx=20,
                pady=20)
logoframe.grid(row=0,
                column=0,
                sticky="nswe",
                columnspan=2,
                rowspan=1,
                padx=20,
                pady=20)
exploreframe.grid(row=1,
                    column=0,
                    sticky="nswe",
                    rowspan=3,
                    padx=20,
                    pady=20)

#Logo
logo = CTkImage(light_image=Image.open("images/BNnobg.png"),
                dark_image=Image.open("images/BNnobg.png"),
                size=(800,200))
logo_label = CTkLabel(logoframe,
                      text="",
                      image=logo,
                      compound=LEFT)
logo_label.pack(expand=True,
                fill=BOTH)

#Treeview

branchestyle = ttk.Style()
branchestyle.theme_use("default")
branchestyle.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=30,
                        font=("Terminal", 12),
                        borderwidth=0)


branches = ttk.Treeview(exploreframe,
                        show="tree",
                        selectmode=tkinter.BROWSE,
                        )

#Buttons
branch_buttons = CTkFrame(exploreframe,
                          height=40)
branch_buttons.pack(side=TOP,
                    fill="x")
img_new = CTkImage(light_image=Image.open("images/new.png"),
                   dark_image=Image.open("images/new.png"),
                   size=(25,20))
img_save = CTkImage(light_image=Image.open("images/save.png"),
                   dark_image=Image.open("images/save.png"),
                   size=(25,20))
img_delete = CTkImage(light_image=Image.open("images/del.png"),
                   dark_image=Image.open("images/del.png"),
                   size=(25,20))

def new():
    if bb_menu.get() == "Root Branch":
        iid = branches.insert("", tkinter.END, text="Root Branch", values="root")
        db.execute("INSERT INTO branches (iid, name, value) VALUES (?, ?, ?)", (iid, "Root Branch", "root"))
        connection.commit()

    elif bb_menu.get() == "Sub-Branch":
            if branches.focus():
                item = branches.selection()[0]

                if item and branches.item(item).get("values") == ['root'] or branches.item(item).get("values") == ['sub']:
                    iid = branches.insert(item, tkinter.END, text="Sub Branch", values="sub")
                    db.execute("INSERT INTO branches (iid, name, parent_id, value) VALUES (?, ?, ?, ?)", (iid, "Sub-Branch", item, "sub"))
                    connection.commit()
                else:
                    tkinter.messagebox.showinfo("Error", "You need to select a parent branch to create a sub-branch")
            else:
                tkinter.messagebox.showinfo("Error", "You need to select a parent branch to create a sub-branch")

    elif bb_menu.get() == "Note":
            if branches.focus():
                item = branches.selection()[0]

                if item and branches.item(item).get("values") == ['root'] or branches.item(item).get("values") == ['sub']:
                    iid = branches.insert(item, tkinter.END, text="Note", values="note")
                    db.execute("INSERT INTO notes (iid, name, branch_id, value) VALUES (?, ?, ?, ?)", (iid, "Note", item, "note"))
                    connection.commit()
                else:
                    tkinter.messagebox.showinfo("Error", "You need to select a branch to create a note")
            else:
                tkinter.messagebox.showinfo("Error", "You need to select a branch to create a note")
    
def load():
    db.execute("SELECT * FROM branches")
    branchs = db.fetchall()
    db.execute("SELECT * FROM notes")
    notes = db.fetchall()

    if branchs:
        for branch in branchs:
            iid = branch[0]
            name = branch[1]
            parent = branch[2]
            value = branch[3]

            if parent is None:
                parent = ""
                
            branches.insert(parent, tkinter.END, iid, text=name, values=value)

            if notes:
                for note in notes:
                    iid = note[0]
                    name = note[1]
                    context = note[2]
                    branch_id = note[3]
                    value = note[4]

                    if branches.exists(branch_id):
                        branches.insert(branch_id, tkinter.END, iid, text=name, values=value)

def delete():
    item = branches.selection()[0]
    branches.delete(item)
    db.execute("DELETE FROM branches WHERE iid = ?", (item,))
    connection.commit()

def rename(event):
    #Getting selected treeview item
    item = branches.selection()[0]

    if item:
        #Getting current text of treeview item
        old_text = branches.item(item).get("text")

        #Getting dimension of treeview item (cell)
        box = branches.bbox(item)

        #Creating entry widget to enter new text
        edit_entry = tkinter.Entry(branches,
                               bg="#2b2b2b",
                               fg="white",
                               width=box[2])
        
        #Inserting current item's text inside of entry widget
        edit_entry.insert(0, old_text)

        #Selecting all characters inside entry widget
        edit_entry.select_range(0, tkinter.END)

        #Setting focus to entry wdiget
        edit_entry.focus()

        #Function to update treeview item text and to delete entry widget afterwards
        def enter_pressed():
            new_text = edit_entry.get().strip()
            branches.item(item, text=new_text)

            #Checking if item is a branch or a note, then updating name in database
            if branches.item(item).get("values") == ['root'] or branches.item(item).get("values") == ['sub']:
                db.execute("UPDATE branches SET name = ? WHERE iid = ?", (new_text, item,))
                connection.commit()
            else:
                db.execute("UPDATE notes SET name = ? WHERE iid = ?", (new_text, item,))
                connection.commit()

            edit_entry.destroy()
    
        #Binding events (enter key, focusing out of widget) to entry widget
        edit_entry.bind("<Return>", lambda event: enter_pressed())
        edit_entry.bind("<FocusOut>", lambda event: edit_entry.destroy())

        #Placing entry widget on treeview item's coordinates
        edit_entry.place(x=box[0], y=box[1], width=box[2], height=box[3])
    
branches.bind("<Double-1>", rename)

bb_new = CTkButton(branch_buttons, bg_color="#2b2b2b", fg_color="#2b2b2b", text="", width=50, image=img_new, command=new)
bb_load = CTkButton(branch_buttons, bg_color="#2b2b2b", fg_color="#2b2b2b", text="", width=50, image=img_save, command=load)
bb_delete = CTkButton(branch_buttons, bg_color="#2b2b2b", fg_color="#2b2b2b", text="", width=50, image=img_delete, command=delete)

#Menu
bb_menu = CTkOptionMenu(branch_buttons,
                        bg_color="#2b2b2b",
                        fg_color="#2b2b2b",
                        button_color="#383838",
                        font=("Terminal", 12),
                        dropdown_font=("Terminal", 12),
                        corner_radius=0,
                        values=["Root Branch", "Sub-Branch", "Note"])

#Textbox
textbox = CTkTextbox(textframe)
def show_textbox(event):
    global selected_note
    item = branches.selection()[0]
    selected_note = item
    if branches.item(item).get("values") == ['note'] and branches.identify_element(event.x, event.y) == "text":
        textbox.delete("1.0", "end")
        db.execute("SELECT content FROM notes WHERE iid = ?", (item,))
        content = db.fetchone()
        if content:
            text_content = content[0]
            text_content = text_content.replace("{", "").replace("}", "")
            textbox.insert("1.0", text_content)
        else:
            textbox.insert("1.0", "")
        if not textbox.winfo_ismapped():
            textbox.pack(expand=True,
                        fill=BOTH)
        
branches.bind("<ButtonRelease-1>", show_textbox)

#Save textbox content
def save_text():
    db.execute("UPDATE notes SET content = NULL WHERE iid = ?", (selected_note,))
    new_text = textbox.get("1.0", "end")
    db.execute("UPDATE notes SET content = ? WHERE iid = ?", (new_text, selected_note,))
    connection.commit()

def typing(event):
    if hasattr(typing, "after_id"):
        root.after_cancel(typing.after_id)
    typing.after_id = root.after(500, save_text)

textbox.bind("<Key>", typing)


bb_new.grid(row=0,
            column=1)
bb_load.grid(row=0,
             column=2)
bb_delete.grid(row=0,
               column=3)
bb_menu.grid(row=0,
            column=0)

branches.pack(expand=True,
              fill=BOTH)

root.mainloop()