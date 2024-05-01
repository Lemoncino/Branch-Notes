from customtkinter import *
from tkinter import *
from PIL import Image, ImageTk

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

bb_new = CTkButton(branch_buttons, bg_color="#2b2b2b", fg_color="#2b2b2b", text="", width=50, image=img_new)
bb_save = CTkButton(branch_buttons, bg_color="#2b2b2b", fg_color="#2b2b2b", text="", width=50, image=img_save)
bb_delete = CTkButton(branch_buttons, bg_color="#2b2b2b", fg_color="#2b2b2b", text="", width=50, image=img_delete)

bb_new.grid(row=0,
            column=0)
bb_save.grid(row=0,
             column=1)
bb_delete.grid(row=0,
               column=2)

root.mainloop()