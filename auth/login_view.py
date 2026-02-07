import tkinter as tk
from auth.auth import login_user

class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Paragon Login", font=("Arial", 20)).pack(pady=30)

        # Username
        tk.Label(self, text="Username").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        # Passowrd
        tk.Label(self, text="Password").pack()
        self.pwd_entry = tk.Entry(self, show="*")
        self.pwd_entry.pack(pady=5)

        # Message
        self.message_label = tk.Label(self, text="", fg="red")
        self.message_label.pack(pady=10)


        # Login Button
        tk.Button(
            self,
            text="Login",
            width=15,
            command=self.handle_login
        ).pack(pady=10)


    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.pwd_entry.get().strip()

        role = login_user(username, password)
        #print("ROLE:", role) # Debugging

        if not role: 
            self.message_label.config(text="Invalid username or password")
            return

        if role == "admin":
            self.app.show_page("AdminDashboard")
        elif role == "tenant":
            self.app.show_page("TenantDashboard")
        elif role == "frontdesk":
            self.app.show_page("FrontdeskDashboard")
        elif role == "finance":
            self.app.show_page("FinanceDashboard")
        elif role == "manager":
            self.app.show_page("ManagerDashboard")
        elif role == "maintenance":
            self.app.show_page("MaintenanceDashboard")
        else:
            self.message_label.config(text="No dashboard for this role")
