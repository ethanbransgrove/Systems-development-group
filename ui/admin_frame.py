import tkinter as tk

class AdminFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Admin Dashboard", font=("Arial", 20)).pack(pady=20)

        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=10)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")