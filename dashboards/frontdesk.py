import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from app.session import logout

from app.session import session
from app.services.tenant_service import register_tenant, get_tenants_for_city

class FrontdeskDashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Front Desk Dashboard", font=("Arial", 20)).pack(pady=20)
        tk.Button(self, text="Logout", command=self.handle_logout).pack()


        tk.Label(self, text="Register Tenant", font=("Arial", 18)).pack(pady=20)

        self.build_form()
        self.build_tenant_table()
        
        tk.Button(
            self,
            text="Refresh Tenants",
            command=self.load_tenants
        ).pack(pady=5)


    def build_form(self):
        form = tk.Frame(self)
        form.pack(pady=10)

        self.entries = {}

        fields = [
            ("NI Number", "ni_number"),
            ("Full Name", "name"),
            ("Phone Number", "phone"),
            ("Email", "email"),
            ("Occupation", "occupation"),
            ("Lease Start (YYYY-MM-DD)", "lease_start"),
            ("Lease End (YYYY-MM-DD)", "lease_end")
            #("City", "city")
        ]

        for row, (label_text, key) in enumerate(fields):
            tk.Label(form, text=label_text, width=25).grid(row=row, column=0, pady=5)
            entry = tk.Entry(form, width=30)
            entry.grid(row=row, column=1, pady=5)
            self.entries[key] = entry

        tk.Button(
            self,
            text="Submit",
            command=self.submit_form,
            width=20
        ).pack(pady=20)


    def submit_form(self):
        tenant_data = {}

        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"{key.replace('_', ' ').title()} is required")
                return
            tenant_data[key] = value

        try:
            register_tenant(session, tenant_data)
            messagebox.showinfo("Success", "Tenant registered successfully")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)


    # Tenant Table
    def build_tenant_table(self):
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        columns = (
            "ni_number",
            "name",
            "phone",
            "email",
            "occupation",
            "lease_start",
            "lease_end",
            "city"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "ni_number": "NI Number",
            "name": "Full Name",
            "phone": "Phone Number",
            "email": "Email",    
            "occupation": "Occupation",
            "lease_start": "Lease Start",
            "lease_end": "Lease End",
            "city": "City",
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True)

        #self.load_tenants() #### Potential error


    def load_tenants(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            tenants = get_tenants_for_city(session)
            
            for tenant in tenants:
                self.tree.insert("", "end", values=(
                    tenant["ni_number"],
                    tenant["name"],
                    tenant["phone"],
                    tenant["email"],
                    tenant["occupation"],
                    tenant["lease_start"],
                    tenant["lease_end"],
                    tenant["city"],
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def handle_logout(self):
        logout()
        self.app.show_page("LoginView")