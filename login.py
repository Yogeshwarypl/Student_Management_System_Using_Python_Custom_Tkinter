# # customtkinter_login.py

# import customtkinter as ctk
# from PIL import Image, ImageTk
# from tkinter import messagebox
# from customtkinter import CTkImage
# import os

#     # === Login Function ===
# def login():
#     if username_entry.get() == '' or password_entry.get() == '':
#         ctk.CTkMessagebox(title="Error", message="Fields cannot be empty", icon="cancel")
#     elif username_entry.get() == 'Yogesh' and password_entry.get() == '1234':
#         ctk.CTkMessagebox(title="Success", message="Welcome...", icon="check")
#         window.destroy()
#         import student_management_system
#     else:
#         ctk.CTkMessagebox(title="Error", message="Please enter correct details", icon="cancel")
        
# def login():
#     if username_entry.get() == '' or password_entry.get() == '':
#         messagebox.showerror('Error', 'Fields cannot be empty')
#     elif username_entry.get() == 'Yogesh' and password_entry.get() == '1234':
#         messagebox.showinfo('Success', 'Welcome...')
#         window.destroy()
#         import student_management_system
#     else:
#         messagebox.showerror('Error', 'Please enter correct details')


# # === App Window ===
# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("blue")

# window = ctk.CTk()
# window.geometry('1280x700+0+0')
# window.title('Login System - Student Management System')
# window.resizable(False, False)

# # === Background Image ===
# bg_image = Image.open("bg.jpg").resize((1280, 700))
# # bg_image = Image.open("bg.jpg")
# bg_ctk_image = CTkImage(light_image=bg_image, dark_image=bg_image, size=(1280, 700))
# bg_label = ctk.CTkLabel(window, image=bg_ctk_image, text="")
# bg_label.place(x=0, y=0)

# # === Login Frame ===
# login_frame = ctk.CTkFrame(window, width=500, height=400, corner_radius=15)
# login_frame.place(x=400, y=150)

# # === Logo ===
# logo_img = Image.open("logo.png").resize((100, 100))
# logo_photo = ImageTk.PhotoImage(logo_img)
# logo_label = ctk.CTkLabel(login_frame, image=logo_photo, text="")
# logo_label.grid(row=0, column=0, columnspan=2, pady=20)

# # === Username ===
# user_icon = Image.open("user.png").resize((25, 25))
# user_ctk_icon = CTkImage(light_image=user_icon, dark_image=user_icon, size=(25, 25))
# user_label = ctk.CTkLabel(login_frame, image=user_ctk_icon, text=" UserName", compound="left", font=("Arial", 20))
# user_label.grid(row=1, column=0, pady=10, padx=20)

# username_entry = ctk.CTkEntry(login_frame, font=("Arial", 20), width=250)
# username_entry.grid(row=1, column=1, pady=10, padx=20)

# # === Password ===
# password_icon = Image.open("password.png").resize((25, 25))
# password_photo = ImageTk.PhotoImage(password_icon)
# password_label = ctk.CTkLabel(login_frame, image=password_photo, text=" Password", compound="left", font=("Arial", 20))
# password_label.grid(row=2, column=0, pady=10, padx=20)

# password_entry = ctk.CTkEntry(login_frame, font=("Arial", 20), show="*", width=250)
# password_entry.grid(row=2, column=1, pady=10, padx=20)

# # === Login Button ===
# login_button = ctk.CTkButton(login_frame, text="Login", command=login, width=150)
# login_button.grid(row=3, column=1, pady=20)

# window.mainloop()


# customtkinter_login.py

import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from customtkinter import CTkImage
import subprocess
import sys
import os

# === Login Function ===
def login():
    if username_entry.get() == '' or password_entry.get() == '':
        messagebox.showerror('Error', 'Fields cannot be empty')
    elif username_entry.get() == 'Yogesh' and password_entry.get() == '1234':
        messagebox.showinfo('Success', 'Welcome...')
        window.destroy()
        subprocess.Popen([sys.executable, "student_management_system.py"])  
        # import student_management_system
    else:
        messagebox.showerror('Error', 'Please enter correct details')

# === App Window ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.geometry('1280x700+0+0')
window.title('Login System - Student Management System')
window.resizable(False, False)

# === Background Image ===
bg_image = Image.open("bg.jpg").resize((1280, 700))
bg_ctk_image = CTkImage(light_image=bg_image, dark_image=bg_image, size=(1280, 700))
bg_label = ctk.CTkLabel(window, image=bg_ctk_image, text="")
bg_label.place(x=0, y=0)

# === Login Frame ===
login_frame = ctk.CTkFrame(window, width=500, height=400, corner_radius=15)
login_frame.place(x=400, y=150)

# === Logo ===
logo_img = Image.open("logo.png").resize((100, 100))
logo_ctk_image = CTkImage(light_image=logo_img, dark_image=logo_img, size=(100, 100))
logo_label = ctk.CTkLabel(login_frame, image=logo_ctk_image, text="")
logo_label.grid(row=0, column=0, columnspan=2, pady=20)

# === Username ===
user_icon = Image.open("user.png").resize((25, 25))
user_ctk_icon = CTkImage(light_image=user_icon, dark_image=user_icon, size=(25, 25))
user_label = ctk.CTkLabel(login_frame, image=user_ctk_icon, text=" UserName", compound="left", font=("Arial", 20))
user_label.grid(row=1, column=0, pady=10, padx=20)

username_entry = ctk.CTkEntry(login_frame, font=("Arial", 20), width=250)
username_entry.grid(row=1, column=1, pady=10, padx=20)

# === Password ===
password_icon = Image.open("password.png").resize((25, 25))
password_ctk_icon = CTkImage(light_image=password_icon, dark_image=password_icon, size=(25, 25))
password_label = ctk.CTkLabel(login_frame, image=password_ctk_icon, text=" Password", compound="left", font=("Arial", 20))
password_label.grid(row=2, column=0, pady=10, padx=20)

password_entry = ctk.CTkEntry(login_frame, font=("Arial", 20), show="*", width=250)
password_entry.grid(row=2, column=1, pady=10, padx=20)

# === Login Button ===
login_button = ctk.CTkButton(login_frame, text="Login", command=login, width=150)
login_button.grid(row=3, column=1, pady=20)

window.mainloop()
