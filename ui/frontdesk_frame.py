import tkinter as tk
from tkinter import messagebox, ttk
from models.frontdesk_model import get_available_apartments, register_new_tenant, get_tenants_by_branch, get_tenant_details_with_lease
from models.maintenance_model import get_branch_maintenance_requests, create_maintenance_request_by_staff
from models.complaint_model import get_branch_complaints, create_complaint_by_staff

class FrontDeskFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        tk.Label(self, text="Front Desk Dashboard", font=("Arial", 20)).pack(pady=20)
        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=10)

        # Main container with two columns
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ========== LEFT COLUMN ==========
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # Tenant Management Section
        tenant_frame = tk.LabelFrame(left_frame, text="Tenant Management", padx=15, pady=15)
        tenant_frame.pack(fill="x", pady=10)

        tk.Button(tenant_frame, text="Search / View Tenants", width=25,
                  command=self.open_tenant_search).pack(pady=5)
        tk.Button(tenant_frame, text="Register New Tenant", width=25,
                  command=self.open_register_popup).pack(pady=5)

        # Maintenance Requests Section
        maint_frame = tk.LabelFrame(left_frame, text="Maintenance Requests", padx=15, pady=15)
        maint_frame.pack(fill="x", pady=10)

        tk.Button(maint_frame, text="View All Requests", width=25,
                  command=self.view_maintenance_requests).pack(pady=5)
        tk.Button(maint_frame, text="Create Request for Tenant", width=25,
                  command=self.open_create_maintenance).pack(pady=5)

        # ========== RIGHT COLUMN ==========
        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Complaints Section
        complaint_frame = tk.LabelFrame(right_frame, text="Complaints", padx=15, pady=15)
        complaint_frame.pack(fill="x", pady=10)

        tk.Button(complaint_frame, text="View All Complaints", width=25,
                  command=self.view_complaints).pack(pady=5)
        tk.Button(complaint_frame, text="Create Complaint for Tenant", width=25,
                  command=self.open_create_complaint).pack(pady=5)

        # Logout button at the bottom
        tk.Button(self, text="Logout", command=self.logout, width=20,
                  bg="#d9534f", fg="white").pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")

    # --------------------------------------------------------------
    # Existing register tenant popup (unchanged)
    # --------------------------------------------------------------
    def open_register_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Register New Tenant")
        popup.geometry("600x400")

        branch_id = self.controller.current_user["branch_id"]

        # Tenant Info
        tenant_frame = tk.LabelFrame(popup, text="Tenant Information")
        tenant_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(tenant_frame, text="NI Number").grid(row=0, column=0)
        ni_entry = tk.Entry(tenant_frame)
        ni_entry.grid(row=0, column=1)

        tk.Label(tenant_frame, text="Name").grid(row=1, column=0)
        name_entry = tk.Entry(tenant_frame)
        name_entry.grid(row=1, column=1)

        tk.Label(tenant_frame, text="Email").grid(row=2, column=0)
        email_entry = tk.Entry(tenant_frame)
        email_entry.grid(row=2, column=1)

        tk.Label(tenant_frame, text="Phone").grid(row=3, column=0)
        phone_entry = tk.Entry(tenant_frame)
        phone_entry.grid(row=3, column=1)

        tk.Label(tenant_frame, text="Occupation").grid(row=4, column=0)
        occupation_entry = tk.Entry(tenant_frame)
        occupation_entry.grid(row=4, column=1)

        tk.Label(tenant_frame, text="Reference").grid(row=5, column=0)
        reference_entry = tk.Entry(tenant_frame)
        reference_entry.grid(row=5, column=1)

        # Lease Info
        lease_frame = tk.LabelFrame(popup, text="Lease Information")
        lease_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(lease_frame, text="Start Date (YYYY-MM-DD)").grid(row=0, column=0)
        start_entry = tk.Entry(lease_frame)
        start_entry.grid(row=0, column=1)

        tk.Label(lease_frame, text="End Date (YYYY-MM-DD)").grid(row=1, column=0)
        end_entry = tk.Entry(lease_frame)
        end_entry.grid(row=1, column=1)

        # Apartment Selection
        apartment_frame = tk.LabelFrame(popup, text="Apartment Selection")
        apartment_frame.pack(fill="x", padx=10, pady=10)

        apartments = get_available_apartments(branch_id)
        apartment_dict = {}
        apartment_options = []
        for apt in apartments:
            display = f"{apt['apartment_number']} (£{apt['monthly_rent']})"
            apartment_options.append(display)
            apartment_dict[display] = apt['apartment_id']

        tk.Label(apartment_frame, text="Select Apartment").grid(row=0, column=0)
        apartment_combo = ttk.Combobox(apartment_frame, values=apartment_options, state="readonly")
        apartment_combo.grid(row=0, column=1)

        def submit():
            if not apartment_combo.get():
                messagebox.showerror("Error", "Please select an apartment.")
                return
            tenant_data = (
                ni_entry.get(),
                name_entry.get(),
                email_entry.get(),
                phone_entry.get(),
                occupation_entry.get(),
                reference_entry.get()
            )
            start_date = start_entry.get()
            end_date = end_entry.get()
            apartment_id = apartment_dict[apartment_combo.get()]
            success = register_new_tenant(tenant_data, start_date, end_date, apartment_id, branch_id)
            if success:
                messagebox.showinfo("Success", "Tenant registered successfully.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Registration failed.")

        tk.Button(popup, text="Register Tenant", command=submit).pack(pady=20)

    # --------------------------------------------------------------
    # Tenant Search / View
    # --------------------------------------------------------------
    def open_tenant_search(self):
        branch_id = self.controller.current_user["branch_id"]
        tenants = get_tenants_by_branch(branch_id)

        if not tenants:
            messagebox.showinfo("Info", "No tenants found in this branch.")
            return

        popup = tk.Toplevel(self)
        popup.title("Search Tenants")
        popup.geometry("800x500")

        # Search entry
        search_frame = tk.Frame(popup)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left")
        search_entry = tk.Entry(search_frame, width=30)
        search_entry.pack(side="left", padx=5)

        # Treeview to list tenants
        columns = ("ID", "Name", "Email", "Phone", "NI Number")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill="both", expand=True)

        # Populate tree initially
        def populate(tenant_list):
            for row in tree.get_children():
                tree.delete(row)
            for t in tenant_list:
                tree.insert("", "end", values=(t["tenant_id"], t["name"], t["email"], t["phone"], t["ni_number"]))

        populate(tenants)

        # Search filtering
        def filter_tenants(event=None):
            term = search_entry.get().lower()
            filtered = [t for t in tenants if term in t["name"].lower() or term in t["email"].lower() or term in t["ni_number"].lower()]
            populate(filtered)

        search_entry.bind("<KeyRelease>", filter_tenants)

        # View details on double-click
        def on_double_click(event):
            selected = tree.selection()
            if not selected:
                return
            item = tree.item(selected[0])
            tenant_id = item["values"][0]
            self.show_tenant_details(tenant_id, popup)

        tree.bind("<Double-1>", on_double_click)

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def show_tenant_details(self, tenant_id, parent):
        details = get_tenant_details_with_lease(tenant_id)
        if not details:
            messagebox.showerror("Error", "Tenant not found.")
            return

        popup = tk.Toplevel(parent)
        popup.title(f"Tenant Details - {details['name']}")
        popup.geometry("500x450")

        text = tk.Text(popup, wrap="word", padx=10, pady=10)
        text.pack(fill="both", expand=True)

        info = f"""
Name: {details['name']}
NI Number: {details['ni_number']}
Email: {details['email']}
Phone: {details['phone']}
Occupation: {details['occupation']}
Reference: {details['reference']}

Current Lease:
  Lease ID: {details['lease_id']}
  Start: {details['start_date']}
  End: {details['end_date']}
  Monthly Rent: £{details['monthly_rent']}
  Status: {details['lease_status']}

Apartment:
  Number: {details['apartment_number']}
  Type: {details['type']}
  Rooms: {details['rooms']}
  Property: {details['property_name']}
  Address: {details['property_address']}
"""
        text.insert("1.0", info)
        text.config(state="disabled")
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

    # --------------------------------------------------------------
    # Maintenance Requests: View All
    # --------------------------------------------------------------
    def view_maintenance_requests(self):
        branch_id = self.controller.current_user["branch_id"]
        requests = get_branch_maintenance_requests(branch_id)

        if not requests:
            messagebox.showinfo("Info", "No maintenance requests found.")
            return

        popup = tk.Toplevel(self)
        popup.title("Maintenance Requests")
        popup.geometry("900x500")

        columns = ("ID", "Tenant/Apt", "Description", "Priority", "Status", "Reported", "Assigned")
        tree = ttk.Treeview(popup, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True)

        for req in requests:
            reported = req['reported_date'].strftime("%Y-%m-%d %H:%M") if req['reported_date'] else ""
            assigned = req['assigned_staff_name'] if req['assigned_staff_name'] else "Unassigned"
            tree.insert("", "end", values=(
                req['request_id'],
                req['tenant_apartment'],
                req['description'],
                req['priority'],
                req['status'],
                reported,
                assigned
            ))

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    # --------------------------------------------------------------
    # Maintenance Requests: Create for Tenant
    # --------------------------------------------------------------
    def open_create_maintenance(self):
        branch_id = self.controller.current_user["branch_id"]
        tenants = get_tenants_by_branch(branch_id)

        if not tenants:
            messagebox.showinfo("Info", "No tenants found in this branch.")
            return

        popup = tk.Toplevel(self)
        popup.title("Create Maintenance Request")
        popup.geometry("500x400")

        # Tenant selection
        tk.Label(popup, text="Select Tenant:").pack(pady=5)
        tenant_var = tk.StringVar()
        tenant_options = [f"{t['tenant_id']} - {t['name']} ({t['email']})" for t in tenants]
        tenant_combo = ttk.Combobox(popup, textvariable=tenant_var, values=tenant_options, width=50, state="readonly")
        tenant_combo.pack(pady=5)

        # Priority
        tk.Label(popup, text="Priority:").pack(pady=5)
        priority_var = tk.StringVar(value="LOW")
        priority_combo = ttk.Combobox(popup, textvariable=priority_var, values=["LOW", "MEDIUM", "HIGH"], state="readonly")
        priority_combo.pack(pady=5)

        # Description
        tk.Label(popup, text="Description:").pack(pady=5)
        desc_text = tk.Text(popup, height=6, width=50)
        desc_text.pack(pady=5)

        def submit():
            if not tenant_combo.get():
                messagebox.showerror("Error", "Select a tenant.")
                return
            selected_tenant = tenant_combo.get()
            tenant_id = int(selected_tenant.split(" - ")[0])
            priority = priority_var.get()
            description = desc_text.get("1.0", tk.END).strip()
            if not description:
                messagebox.showerror("Error", "Description cannot be empty.")
                return
            success = create_maintenance_request_by_staff(tenant_id, description, priority)
            if success:
                messagebox.showinfo("Success", "Maintenance request created.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Tenant has no active lease or request failed.")

        tk.Button(popup, text="Create", command=submit).pack(pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack()

    # --------------------------------------------------------------
    # Complaints: View All
    # --------------------------------------------------------------
    def view_complaints(self):
        branch_id = self.controller.current_user["branch_id"]
        complaints = get_branch_complaints(branch_id)

        if not complaints:
            messagebox.showinfo("Info", "No complaints found.")
            return

        popup = tk.Toplevel(self)
        popup.title("Complaints")
        popup.geometry("900x500")

        columns = ("ID", "Tenant", "Apartment", "Property", "Description", "Status", "Date")
        tree = ttk.Treeview(popup, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True)

        for c in complaints:
            tree.insert("", "end", values=(
                c['complaint_id'],
                c['tenant_name'],
                c['apartment_number'],
                c['property_name'],
                c['description'],
                c['status'],
                c['created_date']
            ))

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    # --------------------------------------------------------------
    # Complaints: Create for Tenant
    # --------------------------------------------------------------
    def open_create_complaint(self):
        branch_id = self.controller.current_user["branch_id"]
        tenants = get_tenants_by_branch(branch_id)

        if not tenants:
            messagebox.showinfo("Info", "No tenants found in this branch.")
            return

        popup = tk.Toplevel(self)
        popup.title("Create Complaint")
        popup.geometry("500x400")

        # Tenant selection
        tk.Label(popup, text="Select Tenant:").pack(pady=5)
        tenant_var = tk.StringVar()
        tenant_options = [f"{t['tenant_id']} - {t['name']} ({t['email']})" for t in tenants]
        tenant_combo = ttk.Combobox(popup, textvariable=tenant_var, values=tenant_options, width=50, state="readonly")
        tenant_combo.pack(pady=5)

        # Description
        tk.Label(popup, text="Complaint Description:").pack(pady=5)
        desc_text = tk.Text(popup, height=6, width=50)
        desc_text.pack(pady=5)

        def submit():
            if not tenant_combo.get():
                messagebox.showerror("Error", "Select a tenant.")
                return
            selected_tenant = tenant_combo.get()
            tenant_id = int(selected_tenant.split(" - ")[0])
            description = desc_text.get("1.0", tk.END).strip()
            if not description:
                messagebox.showerror("Error", "Description cannot be empty.")
                return
            success = create_complaint_by_staff(tenant_id, description)
            if success:
                messagebox.showinfo("Success", "Complaint created.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Tenant has no active lease or complaint failed.")

        tk.Button(popup, text="Create", command=submit).pack(pady=10)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack()