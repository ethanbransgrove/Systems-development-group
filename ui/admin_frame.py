import tkinter as tk
from tkinter import messagebox
from models.admin_model import create_staff_user, get_all_branches


class AdminFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Admin Dashboard", font=("Arial", 20)).pack(pady=20)

        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=10)

        tk.Button(self, text="Create Staff User", command=self.open_create_user_popup).pack(pady=10)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")


    def open_create_user_popup(self):

        popup = tk.Toplevel(self)
        popup.title("Create Staff User")

        tk.Label(popup, text="Name").pack()
        name_entry = tk.Entry(popup)
        name_entry.pack()

        tk.Label(popup, text="Email").pack()
        email_entry = tk.Entry(popup)
        email_entry.pack()

        tk.Label(popup, text="Password").pack()
        password_entry = tk.Entry(popup, show="*")
        password_entry.pack()

        tk.Label(popup, text="Role").pack()

        role_var = tk.StringVar()
        role_var.set("FRONT_DESK")

        roles = ["ADMIN","FRONT_DESK", "FINANCE_MANAGER", "MAINTENANCE_STAFF", "MANAGER"]

        role_menu = tk.OptionMenu(popup, role_var, *roles)
        role_menu.pack()

        branches = get_all_branches()

        tk.Label(popup, text="Branch").pack()

        branch_var = tk.StringVar()
        branch_names = [b["name"] for b in branches]
        branch_var.set(branch_names[0])

        branch_menu = tk.OptionMenu(popup, branch_var, *branch_names)
        branch_menu.pack()


        def submit():

            name = name_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            role = role_var.get()
            branch_name = branch_var.get()

            branch_id = None

            for b in branches:
                if b["name"] == branch_name:
                    branch_id = b["branch_id"]
                    break

            success = create_staff_user(name, email, password, role, branch_id)

            if success:
                messagebox.showinfo("Success", "User created successfully")
                popup.destroy()
            else:
                messagebox.showerror("Error", "User creation failed")

        tk.Button(popup, text="Create User", command=submit).pack(pady=10)