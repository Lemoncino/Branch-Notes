import tkinter.messagebox
import customtkinter as ctk
import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
import BranchNotes as bn
import random
import time
import bcrypt
import sqlite3

# Connecting sqlite database
connection = sqlite3.connect("databases/branches.db")
# Initializing cursor
db = connection.cursor()

def check():
    db.execute("SELECT * FROM pin")
    existing_pin = db.fetchone()

    if existing_pin:
        login()
    else:
        pin()

def pin():

    def hash_pin():
        pin = pin_entry.get().encode("utf-8")
        salt = bcrypt.gensalt()

        hashed_pin = bcrypt.hashpw(pin, salt)

        db.execute("INSERT INTO pin (pin) VALUES (?)", (hashed_pin,))
        connection.commit()

        tkinter.messagebox.showinfo("Success", "Successfully created PIN.")
        
        time.sleep(1)
        pin_frame.destroy()
        recovery_number()


    def recovery_number():

        def generate_number():
            number = random.randint(1000000, 9999999)
            
            return number
        
        number = generate_number()

        def store_recovery_number(number):

            number = str(number).encode("utf-8")
            salt = bcrypt.gensalt()

            hashed_recovery_number = bcrypt.hashpw(number, salt)
            
            db.execute("UPDATE pin SET recovery_number = ?", (hashed_recovery_number,))
            connection.commit()
        


        # Main frame for recovery number
        recovery_frame = ctk.CTkFrame(create_pin,
                                  fg_color="#424242")
        recovery_frame.grid(column=0,
                            row=0,
                            sticky="news",
                            pady=80,
                            padx=50)
        
        # Frame containing generated number
        number_frame = ctk.CTkFrame(recovery_frame,
                                fg_color="#2e2e2e",
                                width=300,
                                height=100)
        number_frame.place(rely=0.6,
                           relx=0.5,
                           anchor=ctk.CENTER)
        
        # Label for recovery number
        recovery_label = ctk.CTkLabel(recovery_frame,
                                  text="The displayed number is a\nrandomly generated identifier\nassigned to you\nthat is required to authenticate\nwhen resetting your PIN.",
                                  font=("Terminal", 20),
                                  pady=10)
        recovery_label.pack()

        warning_label = ctk.CTkLabel(recovery_frame,
                                 text="STORE THIS NUMBER",
                                 text_color="#ff6161",
                                 font=("Terminal", 25))
        warning_label.pack()

        number_label = ctk.CTkLabel(number_frame,
                                text=number,
                                font=("Terminal", 40))
        number_label.place(rely=0.5,
                           relx=0.5,
                           anchor=ctk.CENTER)
        
        number_confirm_button = ctk.CTkButton(recovery_frame,
                                text="I Understand",
                                font=("Terminal", 17),
                                fg_color="#3b3b3b",
                                command=lambda: [store_recovery_number(number), create_pin.destroy(), login()])
        number_confirm_button.place(rely=0.85,
                                    relx=0.5,
                                    anchor=ctk.CENTER)
        

    # PIN creation form geometry
    create_pin = ctk.CTk()
    create_pin.geometry("500x500")
    create_pin.title("Login")
    create_pin.resizable(False, False)
    create_pin.columnconfigure(0, weight=1)
    create_pin.rowconfigure(0, weight=1)

    # Frame for PIN creation form
    pin_frame = ctk.CTkFrame(create_pin,
                         width=100,
                         height=100,
                         fg_color="#424242")
    pin_frame.grid(column=0,
                   row=0,
                   sticky="news",
                   pady=150,
                   padx=80)
    
    # Label for welcome text
    welcome_label = ctk.CTkLabel(pin_frame,
                             text="Welcome to Branch Notes",
                             font=("Terminal", 17))
    welcome_label.pack()

    # Label for PIN creation
    pin_label = ctk.CTkLabel(pin_frame,
                         text="Create your PIN",
                         font=("Terminal", 15))
    pin_label.place(rely=0.3,
                    relx=0.5,
                    anchor=ctk.CENTER)
    
    # PIN creation entry
    pin_entry = ctk.CTkEntry(pin_frame,
                   show="*",
                   placeholder_text="PIN",
                   font=("Terminal", 15),
                   width=200,
                   height=40)
    pin_entry.place(rely=0.5,
              relx=0.5,
              anchor=ctk.CENTER)
    
    # Submit button

    submit_button = ctk.CTkButton(pin_frame,
                              text="Submit",
                              font=("Terminal", 15),
                              fg_color="#3b3b3b",
                              command=hash_pin)
    submit_button.place(rely=0.7,
                        relx=0.5,
                        anchor=ctk.CENTER)
    
    create_pin.mainloop()



def login():

    def check_pin():
        inserted_pin = pin.get().encode("utf-8")

        db.execute("SELECT * FROM pin")
        real_pin = db.fetchone()

        result = bcrypt.checkpw(inserted_pin, real_pin[0])

        if result:
            login.destroy()
            bn.main_app()
        else:
            tkinter.messagebox.showinfo("Error", "PIN is incorrect.")

    def reset():
        return
    
    def forgot():
        return

    login = ctk.CTk()
    login.geometry("500x500")
    login.title("Login")
    login.resizable(False, False)
    login.columnconfigure(0, weight=1)
    login.rowconfigure(0, weight=1)

    login_frame = ctk.CTkFrame(login,
                               fg_color="#424242")
    login_frame.grid(column=0,
                     row=0,
                     sticky="news",
                     pady=120,
                     padx=80)

    login_label = ctk.CTkLabel(login_frame,
                               text="Branch Notes Login",
                               font=("Terminal", 17))

    login_label.pack()

    pin = ctk.CTkEntry(login_frame,
                       placeholder_text="PIN",
                       font=("Terminal", 15),
                       width=200,
                       height=40)
    
    pin.place(rely=0.3,
              relx=0.5,
              anchor=ctk.CENTER)
    
    login_button = ctk.CTkButton(login_frame,
                                 text="Log In",
                                 font=("Terminal", 17),
                                 fg_color="#3b3b3b",
                                 command=check_pin)
    login_button.place(rely=0.5,
                       relx=0.5,
                       anchor=ctk.CENTER)
    
    forgot_button = ctk.CTkButton(login_frame,
                                  text="Forgot PIN",
                                  font=("Terminal", 15),
                                  fg_color="#3b3b3b",
                                  command=forgot)
    forgot_button.place(rely=0.9,
                        relx=0.05,
                        anchor=ctk.SW)
    
    reset_button = ctk.CTkButton(login_frame,
                                 text="Reset PIN",
                                 font=("Terminal", 15),
                                 fg_color="#3b3b3b",
                                 command=reset)
    reset_button.place(rely=0.9,
                       relx=0.95,
                       anchor=ctk.SE)

    login.mainloop()