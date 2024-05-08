"""Login pages for Branch Notes.

This file contains the PIN creation page, login page, PIN reset page, recovery number page and forgot recovery number page.
"""
import tkinter.messagebox
import customtkinter as ctk
from PIL import Image
import branchnotes as bn
import random
import time
import bcrypt
import sqlite3

# Connecting sqlite database
connection = sqlite3.connect("databases/branches.db")
# Initializing cursor
db = connection.cursor()

# Function to check whether the user already has a PIN
def check():
    db.execute("SELECT * FROM pin")
    existing_pin = db.fetchone()

    # If user has pin, open login page, else open PIN creation page
    if existing_pin:
        login()
    else:
        pin()

# Function for PIN creation page
def pin():

    # Function to hash inserted PIN and store in database
    def hash_pin():
        #Checking if PIN contains only numeric characters and if it exceeds 30 characters
        if pin_entry.get().isdigit():
            if len(pin_entry.get()) <= 30:
                # Converting PIN to sequence of bytes for bcrypt function
                pin = pin_entry.get().encode("utf-8")

                # Generating salt for hashing function
                salt = bcrypt.gensalt()

                # Hashing PIN
                hashed_pin = bcrypt.hashpw(pin, salt)

                # Inserting PIN into database
                db.execute("INSERT INTO pin (pin) VALUES (?)", (hashed_pin,))
                connection.commit()

                tkinter.messagebox.showinfo("Success", "Successfully created PIN.")
                
                # 1 second delay before opening recovery number page
                time.sleep(1)
                pin_frame.destroy()
                recovery_number()
            else:
                tkinter.messagebox.showinfo("Error", "PIN is too long.\nMaximum characters: 30")
        else:
            tkinter.messagebox.showinfo("Error", "PIN must contain only numbers")

    # Function to generate random recovery number
    def recovery_number():

        def generate_number():
            # Using randint function to generate random integer
            number = random.randint(1000000, 9999999)
            
            return number
        
        number = generate_number()

        # Function to hash and store randomly generated number in database
        def store_recovery_number(number):

            # Converting PIN to sequence of bytes for bcrypt function
            number = str(number).encode("utf-8")

            # Generating salt for hashing function
            salt = bcrypt.gensalt()

            # Hashing recovery number
            hashed_recovery_number = bcrypt.hashpw(number, salt)
            
            # Storing recovery number in database
            db.execute("UPDATE pin SET recovery_number = ?", (hashed_recovery_number,))
            connection.commit()
        


        # Main frame for recovery number
        recovery_frame = ctk.CTkFrame(create_pin,
                                      fg_color="#424242",
                                      bg_color="black")
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

        # Label for red warning text
        warning_label = ctk.CTkLabel(recovery_frame,
                                 text="STORE THIS NUMBER",
                                 text_color="#ff6161",
                                 font=("Terminal", 25))
        warning_label.pack()

        # Label to display generated recovery number
        number_label = ctk.CTkLabel(number_frame,
                                text=number,
                                font=("Terminal", 40))
        number_label.place(rely=0.5,
                           relx=0.5,
                           anchor=ctk.CENTER)
        
        # Button to confirm generated number and open login page
        number_confirm_button = ctk.CTkButton(recovery_frame,
                                text="I Understand",
                                font=("Terminal", 17),
                                fg_color="#3b3b3b",
                                command=lambda: [store_recovery_number(number), create_pin.destroy(), check()])
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

    # Icon
    create_pin.iconbitmap("images/icon.ico")

    # Background image and label
    image = Image.open("images/app_wallpaper.jpg")

    bg = ctk.CTkImage(light_image=image,
                      dark_image=image,
                      size=(2000, 2000))

    bg_label = ctk.CTkLabel(create_pin,
                            image=bg)
    bg_label.place(x=0,
                   y=0)


    # Frame for PIN creation form
    pin_frame = ctk.CTkFrame(create_pin,
                             width=100,
                             height=100,
                             fg_color="#424242",
                             bg_color="black")
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
                             placeholder_text="PIN",
                             font=("Terminal", 15),
                             show="*",
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


# Function for login page
def login():

    # Function to check if inserted PIN is correct
    def check_pin():

        # Converting PIN to sequence of bytes for bcrypt function
        inserted_pin = pin.get().encode("utf-8")
        db.execute("SELECT * FROM pin")
        real_pin = db.fetchone()

        # Comparing PINs
        result = bcrypt.checkpw(inserted_pin, real_pin[0])

        # If PIN is correct, open app, else prompt user
        if result:
            login_page.destroy()
            bn.main_app()
        else:
            tkinter.messagebox.showinfo("Error", "PIN is incorrect.")

    # Function for PIN resetting page
    def forgot():

        # Function to reset PIN
        def forgot_pin():
            # Converting PIN to sequence of bytes for bcrypt function
            inserted_recovery_number = recovery_number_entry.get().encode("utf-8")

            db.execute("SELECT recovery_number FROM pin")
            real_recovery_number = db.fetchone()

            # Comparing recovery numbers
            result_recovery = bcrypt.checkpw(inserted_recovery_number, real_recovery_number[0])

            # If recovery number is correct, update database with new PIN
            if result_recovery:
                new_pin = pin_entry.get().encode("utf-8")

                db.execute("SELECT pin FROM pin")
                old_pin = db.fetchone()

                result_pin = bcrypt.checkpw(new_pin, old_pin[0])

                # If new PIN is different from old one, update database, else prompt user
                if not result_pin:
                    salt = bcrypt.gensalt()

                    hashed_new_pin = bcrypt.hashpw(new_pin, salt)

                    db.execute("UPDATE pin SET pin = ?", (hashed_new_pin,))
                    connection.commit()

                    tkinter.messagebox.showinfo("Success", "PIN reset successfully.") 

                    # 1 second delay before opening login page
                    time.sleep(1)
                    login_page.destroy()
                    check()
                else:
                    tkinter.messagebox.showinfo("Error", "New PIN cannot be the old one.")
            else:
                tkinter.messagebox.showinfo("Error", "Recovery number is incorrect.")

        # Function for forgot recovery number page
        def forgot_recovery_number():

            # Function to clear database
            def reset_app():
                db.execute("DELETE FROM pin")
                db.execute("DELETE FROM notes")
                db.execute("DELETE FROM branches")
                connection.commit()

                # 1 second delay before opening PIN creation page
                time.sleep(1)
                login_page.destroy()
                check()

            # Resetting frame to display new one
            forgot_frame.destroy()

            # Main frame for forgot recovery number page
            forgot_recovery = ctk.CTkFrame(login_page,
                                           fg_color="#424242",
                                           bg_color="black")
            forgot_recovery.grid(column=0,
                                 row=0,
                                 sticky="news",
                                 pady=120,
                                 padx=80)
            
            # Label for warning text
            forgot_recovery_label = ctk.CTkLabel(forgot_recovery,
                                                 text="If you forgot\nthe recovery number\nthe application will be\ncompletely reset.\n\nYou will lose\nall your notes\nand your PIN.",
                                                 text_color="#ff6161",
                                                 font=("Terminal", 16))
            forgot_recovery_label.pack(pady=20)

            # Button to clear database
            reset_app_button = ctk.CTkButton(forgot_recovery,
                                             text="I Understand",
                                             font=("Terminal", 17),
                                             fg_color="#3b3b3b",
                                             command=reset_app)            
            reset_app_button.place(rely=0.85,
                                        relx=0.5,
                                        anchor=ctk.CENTER)
        
        # Resetting frame to display new one
        login_frame.destroy()

        # Main frame for PIN resetting page
        forgot_frame = ctk.CTkFrame(login_page,
                                    fg_color="#424242",
                                    bg_color="black")       
        forgot_frame.grid(column=0,
                        row=0,
                        sticky="news",
                        pady=120,
                        padx=80)
                        
        # Label for page text
        forgot_label = ctk.CTkLabel(forgot_frame,
                                   text="I forgot my PIN",
                                   font=("Terminal", 17))     
        forgot_label.pack()

        # Entry for recovery number
        recovery_number_entry = ctk.CTkEntry(forgot_frame,
                                             placeholder_text="Recovery Number",
                                             font=("Terminal", 15),
                                             show="*",
                                             width=200,
                                             height=40)        
        recovery_number_entry.place(rely=0.3,
                                    relx=0.5,
                                    anchor=ctk.CENTER)
        
        # Entry for PIN
        pin_entry = ctk.CTkEntry(forgot_frame,
                                 placeholder_text="New PIN",
                                 font=("Terminal", 15),
                                 show="*",
                                 width=200,
                                 height=40)        
        pin_entry.place(rely=0.5,
                        relx=0.5,
                        anchor=ctk.CENTER)
        
        # Button to reset PIN
        reset_pin_button = ctk.CTkButton(forgot_frame,
                                         text="Reset PIN",
                                         font=("Terminal", 15),
                                         fg_color="#3b3b3b",
                                         command=forgot_pin)        
        reset_pin_button.place(rely=0.7,
                               relx=0.5,
                               anchor=ctk.CENTER)
        
        # Button to open forgot recovery number page
        forgot_recovery_button = ctk.CTkButton(forgot_frame,
                                         text="I forgot the recovery number",
                                         font=("Terminal", 15),
                                         fg_color="#3b3b3b",
                                         command=forgot_recovery_number)        
        forgot_recovery_button.place(rely=0.9,
                                     relx=0.5,
                                     anchor=ctk.CENTER)
        

    # Login page geometry
    login_page = ctk.CTk()
    login_page.geometry("500x500")
    login_page.title("Login")
    login_page.resizable(False, False)
    login_page.columnconfigure(0, weight=1)
    login_page.rowconfigure(0, weight=1)

    # Icon
    login_page.iconbitmap("images/icon.ico")

    # Background image and label
    image = Image.open("images/app_wallpaper.jpg")
    bg = ctk.CTkImage(light_image=image,
                      dark_image=image,
                      size=(2000, 2000))
    bg_label = ctk.CTkLabel(login_page,
                            image=bg)
    bg_label.place(x=0,
                   y=0)

    # Main frame for login page
    login_frame = ctk.CTkFrame(login_page,
                               fg_color="#424242",
                               bg_color="black")    
    login_frame.grid(column=0,
                     row=0,
                     sticky="news",
                     pady=120,
                     padx=80)

    # Label for page text
    login_label = ctk.CTkLabel(login_frame,
                               text="Branch Notes Login",
                               font=("Terminal", 17))
    login_label.pack()

    # Entry for PIN
    pin = ctk.CTkEntry(login_frame,
                       placeholder_text="PIN",
                       font=("Terminal", 15),
                       show="*",
                       width=200,
                       height=40)    
    pin.place(rely=0.3,
              relx=0.5,
              anchor=ctk.CENTER)
    
    # Button to check inserted PIN and log in
    login_button = ctk.CTkButton(login_frame,
                                 text="Log In",
                                 font=("Terminal", 17),
                                 fg_color="#3b3b3b",
                                 command=check_pin)    
    login_button.place(rely=0.5,
                       relx=0.5,
                       anchor=ctk.CENTER)
    
    # Button to open reset PIN page
    reset_button = ctk.CTkButton(login_frame,
                                 text="Reset PIN",
                                 font=("Terminal", 15),
                                 fg_color="#3b3b3b",
                                 command=forgot)   
    reset_button.place(rely=0.9,
                       relx=0.5,
                       anchor=ctk.CENTER)

    # Login page mainloop
    login_page.mainloop()