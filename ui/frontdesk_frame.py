# Student: [Your Name] | Student ID: [Your ID]

import tkinter as tk
from tkinter import messagebox
from models.tenant_model import get_tenant_details
from models.frontdesk_model import register_tenant, search_tenant
from models.maintenance_model import create_maintenance_request, get_all_maintenance_requests
from models.complaint_model import create_complaint, get_all_complaints
from models.frontdesk_model import register_tenant


class FrontDeskFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Front Desk Dashboard", font=("Arial", 20)).pack(pady=10)

        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=5)

        # --- Buttons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Register New Tenant", width=25,
                  command=self.register_tenant_popup).grid(row=0, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text="Lookup Tenant", width=25,
                  command=self.lookup_tenant_popup).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(btn_frame, text="Submit Maintenance Request", width=25,
                  command=self.submit_maintenance_popup).grid(row=1, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text="Submit Complaint", width=25,
                  command=self.submit_complaint_popup).grid(row=1, column=1, padx=10, pady=5)

        tk.Button(btn_frame, text="View All Maintenance Requests", width=25,
                  command=self.view_maintenance).grid(row=2, column=0, padx=10, pady=5)

        tk.Button(btn_frame, text="View All Complaints", width=25,
                  command=self.view_complaints).grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=10)

        self.output_box = tk.Text(self, height=15, width=90)
        self.output_box.pack(pady=10)


    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)


    # ------------------------------------------------------------------ #
    #  Register New Tenant
    # ------------------------------------------------------------------ #
    def register_tenant_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Register New Tenant")
        popup.geometry("500x650")

        fields = {}

        def add_field(label, key, row):
            tk.Label(popup, text=label).grid(row=row, column=0, sticky="e", padx=10, pady=4)
            entry = tk.Entry(popup, width=30)
            entry.grid(row=row, column=1, padx=10, pady=4)
            fields[key] = entry

        add_field("NI Number *",        "ni_number",   0)
        add_field("Full Name *",         "name",        1)
        add_field("Phone Number *",      "phone",       2)
        add_field("Email *",             "email",       3)
        add_field("Occupation",          "occupation",  4)
        add_field("References",          "references",  5)
        add_field("Apartment Required",  "apt_req",     6)
        add_field("Lease Period (mths)", "lease_period",7)
        add_field("Lease Start Date",    "start_date",  8)
        add_field("Monthly Rent (£)",    "monthly_rent",9)
        add_field("Deposit (£)",         "deposit",     10)
        add_field("Emergency Contact",   "emergency",   11)

        def submit():
            data = {k: v.get().strip() for k, v in fields.items()}

            # Basic required field validation
            required = ["ni_number", "name", "phone", "email"]
            for field in required:
                if not data[field]:
                    messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required.")
                    return

            success = register_tenant(data)

            if success:
                messagebox.showinfo("Success", f"Tenant '{data['name']}' registered successfully.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Registration failed. NI number may already exist.")

        tk.Button(popup, text="Register Tenant", command=submit).grid(
            row=12, column=0, columnspan=2, pady=20)


    # ------------------------------------------------------------------ #
    #  Lookup Tenant
    # ------------------------------------------------------------------ #
    def lookup_tenant_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Lookup Tenant")
        popup.geometry("400x200")

        tk.Label(popup, text="Search by Name or Email:").pack(pady=10)
        search_entry = tk.Entry(popup, width=30)
        search_entry.pack(pady=5)

        def search():
            term = search_entry.get().strip()
            if not term:
                messagebox.showerror("Error", "Please enter a search term.")
                return

            results = search_tenant(term)
            self.output_box.delete("1.0", tk.END)

            if not results:
                self.output_box.insert(tk.END, "No tenants found.\n")
            else:
                for t in results:
                    self.output_box.insert(
                        tk.END,
                        f"ID: {t['tenant_id']} | {t['name']} | {t['email']} | {t['phone']}\n"
                    )
            popup.destroy()

        tk.Button(popup, text="Search", command=search).pack(pady=10)


    # ------------------------------------------------------------------ #
    #  Submit Maintenance Request (on behalf of tenant)
    # ------------------------------------------------------------------ #
    def submit_maintenance_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Submit Maintenance Request")
        popup.geometry("500x400")

        tk.Label(popup, text="Tenant ID:").pack(pady=5)
        tenant_id_entry = tk.Entry(popup, width=20)
        tenant_id_entry.pack(pady=5)

        tk.Label(popup, text="Description:").pack(pady=5)
        description_box = tk.Text(popup, height=5, width=40)
        description_box.pack(pady=5)

        tk.Label(popup, text="Priority:").pack(pady=5)
        priority_var = tk.StringVar(value="LOW")
        tk.OptionMenu(popup, priority_var, "LOW", "MEDIUM", "HIGH").pack(pady=5)

        def submit():
            tenant_id = tenant_id_entry.get().strip()
            description = description_box.get("1.0", tk.END).strip()
            priority = priority_var.get()

            if not tenant_id or not description:
                messagebox.showerror("Error", "Tenant ID and description are required.")
                return

            success = create_maintenance_request(tenant_id, description, priority)

            if success:
                messagebox.showinfo("Success", "Maintenance request submitted.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "No active lease found for this tenant.")

        tk.Button(popup, text="Submit", command=submit).pack(pady=15)


    # ------------------------------------------------------------------ #
    #  Submit Complaint (on behalf of tenant)
    # ------------------------------------------------------------------ #
    def submit_complaint_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Submit Complaint")
        popup.geometry("500x350")

        tk.Label(popup, text="Tenant ID:").pack(pady=5)
        tenant_id_entry = tk.Entry(popup, width=20)
        tenant_id_entry.pack(pady=5)

        tk.Label(popup, text="Complaint Description:").pack(pady=5)
        description_box = tk.Text(popup, height=5, width=40)
        description_box.pack(pady=5)

        def submit():
            tenant_id = tenant_id_entry.get().strip()
            description = description_box.get("1.0", tk.END).strip()

            if not tenant_id or not description:
                messagebox.showerror("Error", "Tenant ID and description are required.")
                return

            create_complaint(tenant_id, description)
            messagebox.showinfo("Success", "Complaint submitted.")
            popup.destroy()

        tk.Button(popup, text="Submit", command=submit).pack(pady=15)


    # ------------------------------------------------------------------ #
    #  View All Maintenance Requests
    # ------------------------------------------------------------------ #
    def view_maintenance(self):
        requests = get_all_maintenance_requests()
        self.output_box.delete("1.0", tk.END)

        if not requests:
            self.output_box.insert(tk.END, "No maintenance requests found.\n")
            return

        for r in requests:
            self.output_box.insert(
                tk.END,
                f"ID: {r['request_id']} | Tenant: {r['tenant_id']} | "
                f"Priority: {r['priority']} | Status: {r['status']} | {r['description'][:50]}\n"
            )


    # ------------------------------------------------------------------ #
    #  View All Complaints
    # ------------------------------------------------------------------ #
    def view_complaints(self):
        complaints = get_all_complaints()
        self.output_box.delete("1.0", tk.END)

        if not complaints:
            self.output_box.insert(tk.END, "No complaints found.\n")
            return

        for c in complaints:
            self.output_box.insert(
                tk.END,
                f"ID: {c['complaint_id']} | Tenant: {c['tenant_id']} | "
                f"Status: {c['status']} | {c['description'][:60]}\n"
            )


    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")