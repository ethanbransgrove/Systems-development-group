import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from models.maintenance_model import (
    get_branch_maintenance_requests,
    get_request_details,
    assign_request,
    update_request_status,
    create_maintenance_log
)


class MaintenanceFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        tk.Label(self, text="Maintenance Dashboard", font=("Arial", 20)).pack(pady=20)
        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=10)

        # Treeview frame
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Apartment/Tenant", "Description", "Priority", "Status", "Reported Date", "Assigned To")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Configure columns
        col_widths = [50, 150, 250, 80, 100, 150, 120]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Double-click to view details
        self.tree.bind("<Double-1>", lambda e: self.view_details())

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Refresh", command=self.load_requests).pack(side="left", padx=5)
        tk.Button(button_frame, text="View Details", command=self.view_details).pack(side="left", padx=5)
        tk.Button(button_frame, text="Assign to Me", command=self.assign_to_me).pack(side="left", padx=5)
        tk.Button(button_frame, text="Update Status", command=self.update_status).pack(side="left", padx=5)
        tk.Button(button_frame, text="Resolve (Log)", command=self.resolve_request).pack(side="left", padx=5)
        tk.Button(button_frame, text="Logout", command=self.logout).pack(side="left", padx=20)

        # Initial load
        self.load_requests()

    def tkraise(self, *args, **kwargs):
        """Called when the frame is raised; updates welcome message and refreshes data."""
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)
        self.load_requests()

    def load_requests(self):
        """Fetch and display maintenance requests for the current user's branch."""
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        user = self.controller.current_user
        if not user:
            return

        branch_id = user["branch_id"]
        requests = get_branch_maintenance_requests(branch_id)

        for req in requests:
            reported = req['reported_date'].strftime("%Y-%m-%d %H:%M") if req['reported_date'] else ""
            assigned = req['assigned_staff_name'] if req['assigned_staff_name'] else "Unassigned"
            self.tree.insert("", "end", values=(
                req['request_id'],
                req['tenant_apartment'],
                req['description'],
                req['priority'],
                req['status'],
                reported,
                assigned
            ))

    def get_selected_request_id(self):
        """Return the request_id of the selected treeview row, or None if no selection."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a request.")
            return None
        item = self.tree.item(selected[0])
        request_id = item['values'][0]
        return request_id

    def view_details(self):
        """Open a popup with full details of the selected request."""
        request_id = self.get_selected_request_id()
        if not request_id:
            return

        details = get_request_details(request_id)
        if not details:
            messagebox.showerror("Error", "Request not found.")
            return

        popup = tk.Toplevel(self)
        popup.title(f"Maintenance Request #{request_id}")
        popup.geometry("600x500")

        text = tk.Text(popup, wrap="word", padx=10, pady=10)
        text.pack(fill="both", expand=True)

        info = f"""
Request ID: {details['request_id']}
Status: {details['status']}
Priority: {details['priority']}
Reported Date: {details['reported_date']}
Tenant: {details['tenant_name']} (Phone: {details['phone']}, Email: {details['email']})
Apartment: {details['apartment_number']} - {details['type']}, {details['rooms']} rooms, Rent: £{details['monthly_rent']}
Property: {details['property_name']} - {details['property_address']}
Assigned Staff: {details['assigned_staff_name'] if details['assigned_staff_name'] else 'Unassigned'}

Description:
{details['description']}
"""
        text.insert("1.0", info)
        text.config(state="disabled")
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

    def assign_to_me(self):
        """Assign the selected request to the currently logged-in staff member."""
        request_id = self.get_selected_request_id()
        if not request_id:
            return
        user = self.controller.current_user
        staff_id = user['user_id']
        success = assign_request(request_id, staff_id)
        if success:
            messagebox.showinfo("Success", "Request assigned to you.")
            self.load_requests()
        else:
            messagebox.showerror("Error", "Assignment failed.")

    def update_status(self):
        """Open a popup to change the status (and optionally priority) of the selected request."""
        request_id = self.get_selected_request_id()
        if not request_id:
            return

        popup = tk.Toplevel(self)
        popup.title("Update Status")
        popup.geometry("400x250")

        tk.Label(popup, text="New Status:").pack(pady=5)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(popup, textvariable=status_var,
                                     values=["REPORTED", "IN_PROGRESS", "RESOLVED"],
                                     state="readonly")
        status_combo.pack(pady=5)
        status_combo.set("IN_PROGRESS")

        tk.Label(popup, text="Priority (optional):").pack(pady=5)
        priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(popup, textvariable=priority_var,
                                      values=["LOW", "MEDIUM", "HIGH"],
                                      state="readonly")
        priority_combo.pack(pady=5)
        priority_combo.set("")

        def submit():
            status = status_var.get()
            priority = priority_var.get() if priority_var.get() else None
            if not status:
                messagebox.showerror("Error", "Please select status.")
                return
            success = update_request_status(request_id, status, priority)
            if success:
                messagebox.showinfo("Success", "Status updated.")
                popup.destroy()
                self.load_requests()
            else:
                messagebox.showerror("Error", "Update failed.")

        tk.Button(popup, text="Update", command=submit).pack(pady=20)

    def resolve_request(self):
        """Open a popup to log resolution details and mark the request as resolved."""
        request_id = self.get_selected_request_id()
        if not request_id:
            return

        popup = tk.Toplevel(self)
        popup.title("Resolve Request")
        popup.geometry("500x450")

        # Resolution notes
        tk.Label(popup, text="Resolution Notes:").pack(pady=5)
        notes_text = tk.Text(popup, height=5, width=50)
        notes_text.pack(pady=5)

        # Hours spent
        tk.Label(popup, text="Hours Spent:").pack(pady=5)
        hours_entry = tk.Entry(popup)
        hours_entry.pack(pady=5)

        # Cost
        tk.Label(popup, text="Cost (£):").pack(pady=5)
        cost_entry = tk.Entry(popup)
        cost_entry.pack(pady=5)

        # Optional start and end time
        tk.Label(popup, text="Start Time (YYYY-MM-DD HH:MM:SS, optional):").pack(pady=5)
        start_entry = tk.Entry(popup)
        start_entry.pack(pady=5)

        tk.Label(popup, text="End Time (YYYY-MM-DD HH:MM:SS, optional):").pack(pady=5)
        end_entry = tk.Entry(popup)
        end_entry.pack(pady=5)

        def submit():
            notes = notes_text.get("1.0", tk.END).strip()
            hours_str = hours_entry.get().strip()
            cost_str = cost_entry.get().strip()
            start_str = start_entry.get().strip()
            end_str = end_entry.get().strip()

            if not notes:
                messagebox.showerror("Error", "Please enter resolution notes.")
                return
            if not hours_str:
                messagebox.showerror("Error", "Please enter hours spent.")
                return
            if not cost_str:
                messagebox.showerror("Error", "Please enter cost.")
                return

            try:
                hours = float(hours_str)
                cost = float(cost_str)
            except ValueError:
                messagebox.showerror("Error", "Hours and cost must be numbers.")
                return

            # Parse datetimes if provided
            start_time = None
            end_time = None
            if start_str:
                try:
                    start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    messagebox.showerror("Error", "Start time format should be YYYY-MM-DD HH:MM:SS")
                    return
            if end_str:
                try:
                    end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    messagebox.showerror("Error", "End time format should be YYYY-MM-DD HH:MM:SS")
                    return

            success = create_maintenance_log(request_id, start_time, end_time, hours, cost, notes)
            if success:
                messagebox.showinfo("Success", "Request resolved and logged.")
                popup.destroy()
                self.load_requests()
            else:
                messagebox.showerror("Error", "Failed to log resolution.")

        tk.Button(popup, text="Submit", command=submit).pack(pady=20)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")