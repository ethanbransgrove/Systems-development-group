import tkinter as tk
from tkinter import messagebox
from models.user_model import login_user


class LoginFrame(tk.Frame):

    """
    Logs in a user based on their user details and logs a user into the correct dashboard based on role of user in
    database.
    """


    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        tk.Label(self, text="Login", font=("Arial", 20)).pack(pady=20)

        tk.Label(self, text="Email").pack()
        self.email_entry = tk.Entry(self)
        self.email_entry.pack()

        tk.Label(self, text="Password").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        user = login_user(email, password)

        if user:
            self.controller.set_user(user)
            self.controller.show_frame(user["role"])
        else:
            messagebox.showerror("Error", "Invalid credentials")