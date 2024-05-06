"""Branch Notes.

Application for branched study notes.
Create branches, sub-branches, and organize your notes with your preferred hierarchy.
Features include renaming notes and branches, as well as automatic loading from the database.
More features yet to come.
"""

import tkinter.messagebox
import customtkinter as ctk
import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3

# Connecting sqlite database
connection = sqlite3.connect("databases/branches.db")
# Turning foreign key constraints on
connection.execute("PRAGMA foreign_keys = ON")
# Initializing cursor
db = connection.cursor()

def main_app():
    # Function to check if limit of sub-branches has been exceeded (7)
    def check_max_branches():
        item = branches.selection()[0]
        count = 0

        # Go to root branch of any selected branch
        while branches.parent(item) != "":
            item = branches.parent(item)

        # Recursive function to traverse whole tree and count number of branches
        def count_children(item):

            nonlocal count

            count += 1

            # Get children of current item
            children = branches.get_children(item)

            # Recursively traverse sub-branches
            for child in children:

                # Decrementing count to not include notes
                if branches.item(child).get("values") == ['note']:
                    count -= 1

                count_children(child)
            
            # Excluding initial item from the count
            return count - 1
        
        count = count_children(item)
        
        # Check if amount of branches exceeds limit (7)
        if count >= 7:
            tkinter.messagebox.showinfo("Error", "Maximum amount of sub-branches per root-branch: 7")
            return True 

    # Function to create new item in treeview
    def new():

        # Check if maximum amount of 200 items has been exceeded
        if len(branches.get_children()) > 200:
            tkinter.messagebox.showinfo("Error", "Maximum amount of elements exceeded: 200")

        # Check what item is selected in the menu
        if bb_menu.get() == "Root Branch":

            # Create item and execute database query
            iid = branches.insert("", tkinter.END, text="Root Branch", values="root")
            db.execute("INSERT INTO branches (iid, name, value) VALUES (?, ?, ?)", (iid, "Root Branch", "root"))
            connection.commit()

        elif bb_menu.get() == "Sub-Branch":
                
                # Check if a branch is selected to be parent of the new sub-branch
                if branches.focus():
                    item = branches.selection()[0]

                    # Check if selected item is a branch
                    if item and branches.item(item).get("values") == ['root'] or branches.item(item).get("values") == ['sub']:

                        # Check if branch limit isn't exceeded
                        if not check_max_branches():

                            # Create item and execute database query
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

    # Function to load data from database
    def load():

        # Fetch data from database
        db.execute("SELECT * FROM branches")
        branchs = db.fetchall()
        db.execute("SELECT * FROM notes")
        notes = db.fetchall()

        # Check if any branches exist
        # Branch and note creation are not separated as to mantain exact item order in treeview
        if branchs:

            # Create branch by extracting data from database
            for branch in branchs:
                iid = branch[0]
                name = branch[1]
                parent = branch[2]
                value = branch[3]

                # Check if branch is a root branch (no parent)
                if parent is None:
                    parent = ""
                    
                branches.insert(parent, tkinter.END, iid, text=name, values=value)

                # Check if any notes exist
                if notes:

                    # Create note by extracting data from database
                    for note in notes:
                        iid = note[0]
                        name = note[1]
                        branch_id = note[3]
                        value = note[4]

                        # Before creating note, check if parent branch exists
                        if branches.exists(branch_id):
                            if not branches.exists(iid):
                                branches.insert(branch_id, tkinter.END, iid, text=name, values=value)

    # Function to delete items in treeview
    def delete():
        item = branches.selection()[0]

        # Check if a note is currently selected and displayed
        if "selected_note" in globals() and branches.exists(selected_note):

            # Check if note's parent branch exists
            if branches.parent(selected_note):
                parent_branch = branches.parent(selected_note)
        
        # Check if selected item is a branch or a note, delete from database accordingly and hide textbox if deleted item is a note
        if branches.item(item).get("values") == ['root'] or branches.item(item).get("values") == ['sub']:
            db.execute("DELETE FROM branches WHERE iid = ?", (item,))
        else:
            db.execute("DELETE FROM notes WHERE iid = ?", (item,))
            textbox.pack_forget()

        branches.delete(item)
        connection.commit()

        # If note's parent branch is deleted, hide textbox
        if not branches.exists(parent_branch):
            textbox.pack_forget()

    # Function to rename items in treeview
    def rename(event):
        # Getting selected treeview item
        item = branches.selection()[0]

        if item:
            # Getting current text of treeview item
            old_text = branches.item(item).get("text")

            # Getting dimension of treeview item (cell)
            box = branches.bbox(item)

            # Creating entry widget to enter new text
            edit_entry = tkinter.Entry(branches,
                                    bg="#2b2b2b",
                                    fg="white",
                                    font=("Terminal", 13),
                                    width=box[2])

            # Inserting current item's text inside of entry widget
            edit_entry.insert(0, old_text)

            # Selecting all characters inside entry widget
            edit_entry.select_range(0, tkinter.END)

            # Setting focus to entry wdiget
            edit_entry.focus()

            # Function to update treeview item text and to delete entry widget afterwards
            def enter_pressed():
                new_text = edit_entry.get().strip()
                if len(new_text) < 25:
                    branches.item(item, text=new_text)

                    # Checking if item is a branch or a note, then updating name in database
                    if branches.item(item).get("values") == ['root'] or branches.item(item).get("values") == ['sub']:
                        db.execute("UPDATE branches SET name = ? WHERE iid = ?", (new_text, item,))
                        connection.commit()
                    else:
                        db.execute("UPDATE notes SET name = ? WHERE iid = ?", (new_text, item,))
                        connection.commit()

                    edit_entry.destroy()
                else:
                    tkinter.messagebox.showinfo("Error", "Maximum amount of characters exceeded: 25")

        
            # Binding events (enter key, focusing out of widget) to entry widget
            edit_entry.bind("<Return>", lambda event: enter_pressed())
            edit_entry.bind("<FocusOut>", lambda event: edit_entry.destroy())

            # Placing entry widget on treeview item's coordinates
            edit_entry.place(x=box[0], y=box[1], width=box[2], height=box[3])

    # Function to display textbot with content of selected note
    def show_textbox(event):
        # Making selected_note global to correctly close textbox upon deletion of parent branch
        global selected_note

        item = branches.selection()[0]

        # Check if selected item is a note and if user clicked directly on the note's name
        if branches.item(item).get("values") == ['note'] and branches.identify_element(event.x, event.y) == "text":
            selected_note = item

            # Deleting current content from textbox
            textbox.delete("1.0", "end")

            # Fetching note content from database
            db.execute("SELECT content FROM notes WHERE iid = ?", (item,))
            content = db.fetchone()

            # If content is present, insert into textbox
            if content[0]:
                text_content = content[0]
                text_content = text_content.replace("{", "").replace("}", "")
                textbox.insert("1.0", text_content)
            else:
                textbox.insert("1.0", "")

            # Display textbox if isn't currently displayed
            if not textbox.winfo_ismapped():
                textbox.pack(expand=True,
                            fill=ctk.BOTH)

    # Function to store textbox content in database
    def typing(event):

        # Function that executes database queries
        def save_text():
            db.execute("UPDATE notes SET content = NULL WHERE iid = ?", (selected_note,))
            new_text = textbox.get("1.0", "end")
            db.execute("UPDATE notes SET content = ? WHERE iid = ?", (new_text, selected_note,))
            connection.commit()

        # Schedule saving of textbox content upon keypress (500ms)
        # (Adapted from ChatGPT) If content save scheduled and another key is pressed (meaning typing function is called), restart save timer
        if hasattr(typing, "after_id"):             
            root.after_cancel(typing.after_id)
        typing.after_id = root.after(500, save_text)


    # Configuring application geometry
    root = ctk.CTk()
    root.geometry("1000x800")
    root.title("Branch Notes")
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=2)
    root.rowconfigure(1, weight=1)

    # App icon
    icon = ImageTk.PhotoImage(file="images/icon.png")
    root.iconphoto(True, icon)


    # Frames
    logoframe = ctk.CTkFrame(root)
    textframe = ctk.CTkFrame(root)
    exploreframe = ctk.CTkFrame(root)

    # Placing Frames
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

    # Logo image and label
    logo = ctk.CTkImage(light_image=Image.open("images/BNlogo.png"),
                    dark_image=Image.open("images/BNlogo.png"),
                    size=(400, 110))
    logo_label = ctk.CTkLabel(logoframe,
                          text="",
                          image=logo,
                          compound=ctk.LEFT)

    # Placing Logo
    logo_label.pack(expand=True,
                    fill=ctk.BOTH)

    # Frame for buttons
    branch_buttons = ctk.CTkFrame(exploreframe,
                              height=40,
                              fg_color="#2b2b2b")

    # Images for buttons
    img_new = ctk.CTkImage(light_image=Image.open("images/plus.png"),
                       dark_image=Image.open("images/plus.png"),
                       size=(25, 20))

    img_delete = ctk.CTkImage(light_image=Image.open("images/x.png"),
                          dark_image=Image.open("images/x.png"),
                          size=(25, 20))

    # Buttons
    bb_new = ctk.CTkButton(branch_buttons, bg_color="#2b2b2b",
                                       fg_color="#2b2b2b",
                                       hover_color="#424242",
                                       text="",
                                       width=50,
                                       image=img_new,
                                       corner_radius=0,
                                       command=new)

    bb_delete = ctk.CTkButton(branch_buttons, bg_color="#2b2b2b", 
                                          fg_color="#2b2b2b", 
                                          hover_color="#424242",
                                          text="", width=50, 
                                          image=img_delete, 
                                          corner_radius=0,
                                          command=delete)

    # Placing Buttons Frame
    branch_buttons.pack(side=ctk.TOP,
                        fill="x")

    # Placing buttons
    bb_new.grid(row=0,
                column=1)
    bb_delete.grid(row=0,
                   column=3)


    # Treeview
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
                            selectmode=tkinter.BROWSE
                            )


    # Placing Treeview
    branches.pack(expand=True,
                  fill=ctk.BOTH)


    # Menu
    bb_menu = ctk.CTkOptionMenu(branch_buttons,
                            bg_color="#2b2b2b",
                            fg_color="#2b2b2b",
                            button_color="#383838",
                            button_hover_color="#424242",
                            font=("Terminal", 12),
                            dropdown_font=("Terminal", 12),
                            corner_radius=0,
                            values=["Root Branch", "Sub-Branch", "Note"])

    # Placing Menu
    bb_menu.grid(row=0,
                 column=0)


    # Textbox
    textbox = ctk.CTkTextbox(textframe,
                         wrap=ctk.WORD,
                         corner_radius=0,
                         font=("Terminal", 17)) 


    # Event Bindings
    branches.bind("<Triple-1>", rename)

    branches.bind("<ButtonRelease-1>", show_textbox)

    textbox.bind("<Key>", typing)


    # Loading data from database
    load()

    # Main application loop
    root.mainloop()

