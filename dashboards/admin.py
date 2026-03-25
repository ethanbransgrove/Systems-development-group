# dashboards/admin.py

import re
import tkinter as tk
from tkinter import messagebox, ttk
from app.session import session, logout
from app.services.admin_service import (
    create_staff_user, get_all_staff_users, update_staff_user, delete_staff_user,
    get_all_branches, get_all_properties,
    get_all_apartments, update_apartment, add_apartment, delete_apartment,
    apartment_number_exists
)

ROLES    = ["ADMIN", "FRONT_DESK", "FINANCE_MANAGER", "MAINTENANCE_STAFF", "MANAGER"]
STATUSES = ["AVAILABLE", "OCCUPIED", "UNDER_MAINTENANCE"]


def _valid_email(email: str) -> bool:
    """Basic email format check."""
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


class AdminDashboard(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Admin Dashboard", font=("Arial", 18, "bold")).pack(pady=15)
        self.welcome_label = tk.Label(self, text="", font=("Arial", 12))
        self.welcome_label.pack(pady=4)

        dashboard = tk.Frame(self)
        dashboard.pack(pady=15)

        # Staff Management
        staff_frame = tk.LabelFrame(dashboard, text="Staff Management", padx=20, pady=15)
        staff_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        tk.Button(staff_frame, text="Create Staff User", width=22,
                  font=("Arial", 10, "bold"),
                  command=self.open_create_user_popup).pack(pady=5)
        tk.Button(staff_frame, text="View / Edit Staff Users", width=22,
                  font=("Arial", 10, "bold"),
                  command=self.open_manage_staff_popup).pack(pady=5)

        # Apartment Management
        apt_frame = tk.LabelFrame(dashboard, text="Apartment Management", padx=20, pady=15)
        apt_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        tk.Button(apt_frame, text="View / Edit Apartments", width=22,
                  font=("Arial", 10, "bold"),
                  command=self.open_manage_apartments_popup).pack(pady=5)
        tk.Button(apt_frame, text="Add New Apartment", width=22,
                  font=("Arial", 10, "bold"),
                  command=self.open_add_apartment_popup).pack(pady=5)

        tk.Button(self, text="Logout", font=("Arial", 10), width=15,
                  command=self.handle_logout).pack(pady=15)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.welcome_label.config(text=f"Welcome, {session.get('name') or 'Admin'}")

    # ─────────────────────────────────────────────────────────────────────────
    # STAFF MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def open_create_user_popup(self):
        branches = get_all_branches()
        if not branches:
            messagebox.showerror("Error", "Could not load branches. Check config.py.")
            return

        popup = tk.Toplevel(self)
        popup.title("Create Staff User")
        popup.geometry("400x370")
        popup.resizable(False, False)

        form = tk.Frame(popup, padx=20, pady=15)
        form.pack(fill="both", expand=True)

        fields = {}
        for i, label in enumerate(["Name", "Email", "Password"]):
            tk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(form, width=28, show="*" if label == "Password" else "")
            entry.grid(row=i, column=1, pady=5)
            fields[label] = entry

        tk.Label(form, text="Role").grid(row=3, column=0, sticky="w", pady=5)
        role_var = tk.StringVar(value="FRONT_DESK")
        tk.OptionMenu(form, role_var, *ROLES).grid(row=3, column=1, sticky="w", pady=5)

        tk.Label(form, text="Branch").grid(row=4, column=0, sticky="w", pady=5)
        branch_names = [b["name"] for b in branches]
        branch_var = tk.StringVar(value=branch_names[0])
        tk.OptionMenu(form, branch_var, *branch_names).grid(row=4, column=1, sticky="w", pady=5)

        def submit():
            name     = fields["Name"].get().strip()
            email    = fields["Email"].get().strip()
            password = fields["Password"].get().strip()

            if not name or not email or not password:
                messagebox.showerror("Error", "All fields are required.")
                return
            if not _valid_email(email):
                messagebox.showerror("Error", "Please enter a valid email address.")
                return

            branch_id = next((b["branch_id"] for b in branches if b["name"] == branch_var.get()), None)
            if create_staff_user(name, email, password, role_var.get(), branch_id):
                messagebox.showinfo("Success", f"Staff user '{name}' created.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Creation failed. Email may already be in use.")

        tk.Button(form, text="Create User", width=18, command=submit).grid(
            row=5, column=0, columnspan=2, pady=20)


    def open_manage_staff_popup(self):
        branches = get_all_branches()
        if not branches:
            messagebox.showerror("Error", "Could not load branches. Check config.py.")
            return

        popup = tk.Toplevel(self)
        popup.title("Manage Staff Users")
        popup.geometry("820x500")

        # ── Search bar ───────────────────────────────────────────────────────
        search_frame = tk.Frame(popup)
        search_frame.pack(fill="x", padx=10, pady=6)
        tk.Label(search_frame, text="Search:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=6)

        # ── Table ────────────────────────────────────────────────────────────
        columns = ("ID", "Name", "Email", "Role", "Branch")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=14)
        for col, w in zip(columns, [50, 160, 200, 160, 150]):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        sb = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        all_users = []

        def load():
            nonlocal all_users
            all_users = get_all_staff_users()
            _apply_filter()

        def _apply_filter(*_):
            term = search_var.get().lower()
            for row in tree.get_children():
                tree.delete(row)
            for u in all_users:
                if (term in u["name"].lower() or
                        term in u["email"].lower() or
                        term in u["role"].lower()):
                    tree.insert("", "end", values=(
                        u["user_id"], u["name"], u["email"], u["role"], u["branch_name"]
                    ))

        search_var.trace_add("write", _apply_filter)
        load()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def get_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Select a user first.")
                return None
            return tree.item(sel[0])["values"]

        def edit_user():
            values = get_selected()
            if not values:
                return
            user_id, name, email, role, branch_name = values

            edit = tk.Toplevel(popup)
            edit.title(f"Edit User — {name}")
            edit.geometry("400x370")
            edit.resizable(False, False)

            form = tk.Frame(edit, padx=20, pady=15)
            form.pack(fill="both", expand=True)

            tk.Label(form, text="Name").grid(row=0, column=0, sticky="w", pady=5)
            name_entry = tk.Entry(form, width=28)
            name_entry.insert(0, name)
            name_entry.grid(row=0, column=1, pady=5)

            tk.Label(form, text="Email").grid(row=1, column=0, sticky="w", pady=5)
            email_entry = tk.Entry(form, width=28)
            email_entry.insert(0, email)
            email_entry.grid(row=1, column=1, pady=5)

            tk.Label(form, text="New Password\n(leave blank to keep)").grid(row=2, column=0, sticky="w", pady=5)
            pwd_entry = tk.Entry(form, show="*", width=28)
            pwd_entry.grid(row=2, column=1, pady=5)

            tk.Label(form, text="Role").grid(row=3, column=0, sticky="w", pady=5)
            role_var = tk.StringVar(value=role)
            tk.OptionMenu(form, role_var, *ROLES).grid(row=3, column=1, sticky="w", pady=5)

            tk.Label(form, text="Branch").grid(row=4, column=0, sticky="w", pady=5)
            branch_names = [b["name"] for b in branches]
            branch_var = tk.StringVar(value=branch_name)
            tk.OptionMenu(form, branch_var, *branch_names).grid(row=4, column=1, sticky="w", pady=5)

            def save():
                new_name  = name_entry.get().strip()
                new_email = email_entry.get().strip()
                new_pwd   = pwd_entry.get().strip()

                if not new_name or not new_email:
                    messagebox.showerror("Error", "Name and email are required.")
                    return
                if not _valid_email(new_email):
                    messagebox.showerror("Error", "Please enter a valid email address.")
                    return

                new_branch_id = next(
                    (b["branch_id"] for b in branches if b["name"] == branch_var.get()), None
                )
                if update_staff_user(user_id, new_name, new_email,
                                     role_var.get(), new_branch_id, new_pwd):
                    messagebox.showinfo("Success", "User updated.")
                    edit.destroy()
                    load()
                else:
                    messagebox.showerror("Error", "Update failed. Email may already be in use.")

            tk.Button(form, text="Save Changes", width=18, command=save).grid(
                row=5, column=0, columnspan=2, pady=20)

        def remove_user():
            values = get_selected()
            if not values:
                return
            user_id, name = values[0], values[1]

            # Prevent admin from deleting their own account
            if user_id == session.get("user_id"):
                messagebox.showerror("Error", "You cannot delete your own account.")
                return

            if not messagebox.askyesno("Confirm", f"Delete user '{name}'? This cannot be undone."):
                return

            if delete_staff_user(user_id):
                messagebox.showinfo("Success", f"User '{name}' deleted.")
                load()
            else:
                messagebox.showerror("Error", "Deletion failed.")

        tk.Button(btn_frame, text="Edit Selected", width=16, command=edit_user).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Delete Selected", width=16, fg="white", bg="#d9534f",
                  command=remove_user).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Refresh", width=12, command=load).pack(side="left", padx=8)


    # ─────────────────────────────────────────────────────────────────────────
    # APARTMENT MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def open_manage_apartments_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Manage Apartments")
        popup.geometry("950x520")

        # ── Search bar ───────────────────────────────────────────────────────
        search_frame = tk.Frame(popup)
        search_frame.pack(fill="x", padx=10, pady=6)
        tk.Label(search_frame, text="Search:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=6)

        # ── Table ────────────────────────────────────────────────────────────
        columns = ("ID", "Property", "Number", "Type", "Rooms", "Rent (£)", "Status", "Branch")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=14)
        widths = [40, 160, 80, 120, 60, 90, 130, 130]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        sb = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        apartments = []

        def load():
            nonlocal apartments
            apartments = get_all_apartments()
            _apply_filter()

        def _apply_filter(*_):
            term = search_var.get().lower()
            for row in tree.get_children():
                tree.delete(row)
            for a in apartments:
                if (term in (a["property_name"] or "").lower() or
                        term in (a["apartment_number"] or "").lower() or
                        term in (a["type"] or "").lower() or
                        term in (a["status"] or "").lower()):
                    tree.insert("", "end", values=(
                        a["apartment_id"], a["property_name"], a["apartment_number"],
                        a["type"], a["rooms"], f"{a['monthly_rent']:.2f}",
                        a["status"], a["branch_name"]
                    ))

        search_var.trace_add("write", _apply_filter)
        load()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def get_selected_apt():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Select an apartment first.")
                return None, None
            values = tree.item(sel[0])["values"]
            apt_id = values[0]
            apt = next((a for a in apartments if a["apartment_id"] == apt_id), None)
            return apt_id, apt

        def edit_apartment():
            apt_id, apt = get_selected_apt()
            if not apt:
                return

            edit = tk.Toplevel(popup)
            edit.title(f"Edit Apartment — {apt['apartment_number']}")
            edit.geometry("380x360")
            edit.resizable(False, False)

            form = tk.Frame(edit, padx=20, pady=15)
            form.pack(fill="both", expand=True)

            labels   = ["Apartment Number", "Type", "Rooms", "Monthly Rent (£)"]
            defaults = [apt["apartment_number"], apt["type"] or "",
                        str(apt["rooms"] or ""), str(apt["monthly_rent"])]
            entries  = {}
            for i, (lbl, val) in enumerate(zip(labels, defaults)):
                tk.Label(form, text=lbl).grid(row=i, column=0, sticky="w", pady=5)
                e = tk.Entry(form, width=24)
                e.insert(0, val)
                e.grid(row=i, column=1, pady=5)
                entries[lbl] = e

            tk.Label(form, text="Status").grid(row=4, column=0, sticky="w", pady=5)
            status_var = tk.StringVar(value=apt["status"])
            tk.OptionMenu(form, status_var, *STATUSES).grid(row=4, column=1, sticky="w", pady=5)

            def save():
                apt_number = entries["Apartment Number"].get().strip()
                apt_type   = entries["Type"].get().strip()
                new_status = status_var.get()

                if not apt_number:
                    messagebox.showerror("Error", "Apartment number is required.")
                    return

                try:
                    rooms = int(entries["Rooms"].get().strip())
                    rent  = float(entries["Monthly Rent (£)"].get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Rooms must be a whole number. Rent must be a number.")
                    return

                if rooms <= 0:
                    messagebox.showerror("Error", "Rooms must be greater than 0.")
                    return
                if rent <= 0:
                    messagebox.showerror("Error", "Rent must be greater than £0.")
                    return

                # Duplicate apartment number check
                if apartment_number_exists(apt["property_id"], apt_number, exclude_id=apt_id):
                    messagebox.showerror(
                        "Error",
                        f"Apartment '{apt_number}' already exists in this property."
                    )
                    return

                # Warn if changing an OCCUPIED apartment away from OCCUPIED
                if apt["status"] == "OCCUPIED" and new_status != "OCCUPIED":
                    if not messagebox.askyesno(
                        "Warning",
                        f"This apartment is currently OCCUPIED by a tenant.\n\n"
                        f"Changing the status to '{new_status}' will not remove the active lease.\n\n"
                        f"Are you sure you want to continue?"
                    ):
                        return

                if update_apartment(apt_id, apt_number, apt_type, rooms, rent, new_status):
                    messagebox.showinfo("Success", "Apartment updated.")
                    edit.destroy()
                    load()
                else:
                    messagebox.showerror("Error", "Update failed.")

            tk.Button(form, text="Save Changes", width=18, command=save).grid(
                row=5, column=0, columnspan=2, pady=20)

        def remove_apartment():
            apt_id, apt = get_selected_apt()
            if not apt:
                return

            # Block deletion of OCCUPIED apartments
            if apt["status"] == "OCCUPIED":
                messagebox.showerror(
                    "Cannot Delete",
                    f"Apartment '{apt['apartment_number']}' is currently OCCUPIED.\n\n"
                    "Please terminate the tenant's lease before deleting this apartment."
                )
                return

            if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete apartment '{apt['apartment_number']}' in {apt['property_name']}?\n\n"
                "This cannot be undone."
            ):
                return

            success, reason = delete_apartment(apt_id)
            if success:
                messagebox.showinfo("Success", f"Apartment '{apt['apartment_number']}' deleted.")
                load()
            elif reason == "occupied":
                messagebox.showerror("Error", "Cannot delete an occupied apartment.")
            else:
                messagebox.showerror("Error", "Deletion failed.")

        tk.Button(btn_frame, text="Edit Selected", width=16,
                  command=edit_apartment).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Delete Selected", width=16, fg="white", bg="#d9534f",
                  command=remove_apartment).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Refresh", width=12, command=load).pack(side="left", padx=8)


    def open_add_apartment_popup(self):
        properties = get_all_properties()
        if not properties:
            messagebox.showerror("Error", "No properties found in the database.")
            return

        popup = tk.Toplevel(self)
        popup.title("Add New Apartment")
        popup.geometry("400x340")
        popup.resizable(False, False)

        form = tk.Frame(popup, padx=20, pady=15)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Property").grid(row=0, column=0, sticky="w", pady=5)
        prop_names = [f"{p['name']} ({p['branch_name']})" for p in properties]
        prop_var = tk.StringVar(value=prop_names[0])
        tk.OptionMenu(form, prop_var, *prop_names).grid(row=0, column=1, sticky="w", pady=5)

        labels  = ["Apartment Number", "Type (e.g. 1 Bedroom)", "Rooms", "Monthly Rent (£)"]
        entries = {}
        for i, lbl in enumerate(labels, start=1):
            tk.Label(form, text=lbl).grid(row=i, column=0, sticky="w", pady=5)
            e = tk.Entry(form, width=24)
            e.grid(row=i, column=1, pady=5)
            entries[lbl] = e

        def submit():
            prop_index  = prop_names.index(prop_var.get())
            property_id = properties[prop_index]["property_id"]
            apt_number  = entries["Apartment Number"].get().strip()
            apt_type    = entries["Type (e.g. 1 Bedroom)"].get().strip()

            if not apt_number:
                messagebox.showerror("Error", "Apartment number is required.")
                return

            try:
                rooms = int(entries["Rooms"].get().strip())
                rent  = float(entries["Monthly Rent (£)"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Rooms must be a whole number. Rent must be a number.")
                return

            if rooms <= 0:
                messagebox.showerror("Error", "Rooms must be greater than 0.")
                return
            if rent <= 0:
                messagebox.showerror("Error", "Rent must be greater than £0.")
                return

            # Duplicate apartment number check
            if apartment_number_exists(property_id, apt_number):
                messagebox.showerror(
                    "Error",
                    f"Apartment '{apt_number}' already exists in this property."
                )
                return

            if add_apartment(property_id, apt_number, apt_type, rooms, rent):
                messagebox.showinfo("Success", f"Apartment '{apt_number}' added successfully.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to add apartment.")

        tk.Button(form, text="Add Apartment", width=18, command=submit).grid(
            row=5, column=0, columnspan=2, pady=20)

    # ── Logout ────────────────────────────────────────────────────────────────
    def handle_logout(self):
        logout()
        self.app.show_page("LoginView")