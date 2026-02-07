import tkinter as tk
from app.session import logout

class FrontdeskDashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Front Desk Dashboard", font=("Arial", 18)).pack(pady=20)
        tk.Button(self, text="Logout", command=self.handle_logout).pack()

    def handle_logout(self):
        logout()
        self.app.show_page("LoginView")