import tkinter as tk
from tkinter import messagebox, ttk
from models.tenant_model import get_tenant_details, get_tenant_invoices, update_late_invoices, create_late_payment_notification
from models.payment_model import get_tenant_payments, create_payment, get_monthly_payments, get_neighbour_payment_totals
from models.maintenance_model import create_maintenance_request, get_tenant_maintenance_requests
from models.complaint_model import create_complaint, get_tenant_complaints
from models.notification_model import get_unread_notifications, mark_notifications_read, get_all_notifications
from models.analytics_model import get_late_payments_per_property
from utils.validators import validate_card_number



class TenantFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Tenant Dashboard", font=("Arial", 22, "bold")).pack(pady=10)

        self.info_label = tk.Label(self, text="", font=("Arial", 11))
        self.info_label.pack(pady=5)

        # Main dashboard container
        dashboard = tk.Frame(self)
        dashboard.pack(expand=True)

        dashboard.columnconfigure(0, weight=1)
        dashboard.columnconfigure(1, weight=1)

        # Payments Section
        payments_frame = tk.LabelFrame(dashboard, text="Payments", padx=20, pady=15)
        payments_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        tk.Button(payments_frame,
                  text="View Invoices",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.view_invoices).pack(pady=5)

        tk.Button(payments_frame,
                  text="Pay Invoice",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.open_payment_popup).pack(pady=5)

        tk.Button(payments_frame,
                  text="Payment History",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.view_payments).pack(pady=5)


        # Maintenace Section
        maintenance_frame = tk.LabelFrame(dashboard, text="Maintenance", padx=20, pady=15)
        maintenance_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        tk.Button(maintenance_frame,
                  text="Submit Request",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.submit_maintenance).pack(pady=5)

        tk.Button(maintenance_frame,
                  text="View Requests",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.view_maintenance_requests).pack(pady=5)


        # Complaints Section
        complaint_frame = tk.LabelFrame(dashboard, text="Complaints", padx=20, pady=15)
        complaint_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")

        tk.Button(complaint_frame,
                  text="Submit Complaint",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.submit_complaint).pack(pady=5)

        tk.Button(complaint_frame,
                  text="View Complaints",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.view_complaints).pack(pady=5)


        # Notification Section
        notification_frame = tk.LabelFrame(dashboard, text="Notifications", padx=20, pady=15)
        notification_frame.grid(row=1, column=1, padx=15, pady=10, sticky="nsew")

        tk.Button(notification_frame,
                  text="View Notifications",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.view_notifications).pack(pady=5)
        

        # Analytics Section
        analytics_frame = tk.LabelFrame(dashboard, text="Tenant Analytics", padx=20, pady=15)
        analytics_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")

        tk.Button(analytics_frame,
                  text="Monthly Payment Graph",
                  width=25,
                  font=("Arial",10,"bold"),
                  command=self.view_monthly_graph).pack(pady=5)
        
        tk.Button(analytics_frame,
                  text="Late Payments Graph",
                  width=25,
                  font=("Arial",10,"bold"),
                  command=self.view_late_payments_graph).pack(pady=5)

        tk.Button(analytics_frame,
                  text="Neighbour Payment Comparison",
                  width=25,
                  font=("Arial",10,"bold"),
                  command=self.view_neighbour_graph).pack(pady=5)
        
        

        # Logout button
        tk.Button(self,
                  text="Logout",
                  width=25,
                  font=("Arial",11,"bold"),
                  bg="#d9534f",
                  fg="white",
                  command=self.logout).pack(pady=25)


    def tkraise(self, *args, **kwargs):
    
        super().tkraise(*args, **kwargs)


        user = self.controller.current_user
        
        if user:

            tenant_id = user["tenant_id"]
            user_id = user["user_id"]

            tenant = get_tenant_details(tenant_id)

            self.info_label.config(
                text=f"Welcome {tenant['name']} | Email: {tenant['email']}"
            )

            # Update invoice status
            update_late_invoices(tenant_id)

            # Create notifications if invoices are late
            create_late_payment_notification(user_id, tenant_id)

            # Get unread notifications
            notifications = get_unread_notifications(user_id)

            if notifications:

                messages = "\n\n".join(n["message"] for n in notifications[:3])

                messagebox.showwarning(
                    "Notifications",
                    messages
                )


    def view_payments(self):

        popup = tk.Toplevel(self)
        popup.title("Payment History")
        popup.geometry("600x400")

        user = self.controller.current_user
        payments = get_tenant_payments(user["tenant_id"])

        columns = ("Amount", "Date")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        if not payments:
            tree.insert("", "end", values=("No payments found", ""))
            return

        for payment in payments:
            tree.insert("", "end", values=(
                f"£{payment['amount']}",
                payment["payment_date"]
            ))
    

    def submit_maintenance(self):

        popup = tk.Toplevel(self)
        popup.title("New Maintenance Request")
        popup.geometry("500x300")

        form = tk.Frame(popup, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Maintenance Request", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=(0,15))

        tk.Label(form, text="Description:").grid(row=1, column=0, sticky="nw")

        description_box = tk.Text(form, height=6, width=40)
        description_box.grid(row=1, column=1, pady=5)

        button_frame = tk.Frame(form)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        def submit():

            description = description_box.get("1.0", tk.END).strip()
            user = self.controller.current_user

            if not description:
                messagebox.showerror("Error", "Description cannot be empty.")
                return

            success = create_maintenance_request(
                user["tenant_id"],
                description
            )

            if success:
                messagebox.showinfo("Success", "Maintenance request submitted.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "No active lease found.")

        tk.Button(button_frame, text="Submit", width=12, command=submit).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", width=12, command=popup.destroy).pack(side="left", padx=10)


    def submit_complaint(self):

        popup = tk.Toplevel(self)
        popup.title("Submit Complaint")
        popup.geometry("500x300")

        tk.Label(popup, text="Complaint Description").pack(pady=10)

        description_box = tk.Text(popup, height=6, width=40)
        description_box.pack(pady=5)

        def submit():

            description = description_box.get("1.0", tk.END).strip()
            user = self.controller.current_user

            if not description:
                messagebox.showerror("Error", "Description cannot be empty.")
                return

            success = create_complaint(user["tenant_id"], description)

            if success:
                messagebox.showinfo("Success", "Complaint submitted.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Complaint submission failed.")

        tk.Button(popup, text="Submit", command=submit).pack(pady=15)  


    def view_invoices(self):

        popup = tk.Toplevel(self)
        popup.title("My Invoices")
        popup.geometry("800x400")

        user = self.controller.current_user
        tenant_id = user["tenant_id"]

        # Automatically update late invoices first
        update_late_invoices(tenant_id)

        invoices = get_tenant_invoices(tenant_id)

        columns = ("ID", "Period", "Amount", "Due Date", "Status")

        #tree = ttk.Treeview(popup, columns=columns, show="headings")
        self.invoice_tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=120)

        self.invoice_tree.pack(fill="both", expand=True)

        for invoice in invoices:
            period = f"{invoice['period_start']} to {invoice['period_end']}"

            self.invoice_tree.insert("", "end", values=(
                invoice["invoice_id"],
                period,
                f"£{invoice['amount_due']}",
                invoice["due_date"],
                invoice["status"]
            ))


    def open_payment_popup(self):

        popup = tk.Toplevel(self)
        popup.title("Pay Invoice")
        popup.geometry("500x350")

        user = self.controller.current_user
        tenant_id = user["tenant_id"]

        invoices = get_tenant_invoices(tenant_id)

        # Only show unpaid invoices
        unpaid_invoices = [i for i in invoices if i["status"] != "PAID"]

        if not unpaid_invoices:
            messagebox.showinfo("Info", "No unpaid invoices.")
            popup.destroy()
            return

        tk.Label(popup, text="Select Invoice").pack(pady=5)

        invoice_var = tk.StringVar()

        invoice_options = []

        for inv in unpaid_invoices:
            label = f"Invoice {inv['invoice_id']} - £{inv['amount_due']} - Due {inv['due_date']}"
            invoice_options.append(label)

        invoice_menu = ttk.Combobox(popup, textvariable=invoice_var, values=invoice_options, width=50)
        invoice_menu.pack(pady=5)

        tk.Label(popup, text="Card Number").pack(pady=5)
        card_entry = tk.Entry(popup)
        card_entry.pack(pady=5)

        def submit_payment():

            selected = invoice_menu.current()

            if selected == -1:
                messagebox.showerror("Error", "Select an invoice.")
                return

            card_number = card_entry.get()

            if not validate_card_number(card_number):
                messagebox.showerror("Error", "Invalid card number.")
                return

            invoice = unpaid_invoices[selected]

            invoice_id = invoice["invoice_id"]
            lease_id = invoice["lease_id"]
            amount = invoice["amount_due"]

            success = create_payment(
                invoice_id,
                lease_id,
                amount,
                card_number
            )

            if success:
                messagebox.showinfo("Success", "Payment successful.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Payment failed.")

        tk.Button(popup, text="Pay", command=submit_payment).pack(pady=20)


    def view_notifications(self):

        popup = tk.Toplevel(self)
        popup.title("Notifications")
        popup.geometry("650x400")

        user = self.controller.current_user
        user_id = user["user_id"]

        notifications = get_all_notifications(user_id)

        columns = ("Message", "Type", "Status", "Date")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill="both", expand=True)

        if not notifications:
            tree.insert("", "end", values=("No notifications", "", "", ""))
            return

        for n in notifications:

            status = "Unread" if n["is_read"] == 0 else "Read"

            tree.insert("", "end", values=(
                n["message"],
                n["type"],
                status,
                n["create_at"]
            ))

        # Mark notifications as read when opened
        mark_notifications_read(user_id)


    def view_monthly_graph(self):

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        popup = tk.Toplevel(self)
        popup.title("Monthly Payments")
        popup.geometry("700x500")

        user = self.controller.current_user
        tenant_id = user["tenant_id"]

        data = get_monthly_payments(tenant_id)

        if not data:
            messagebox.showinfo("Info", "No payment data available.")
            popup.destroy()
            return
        
        months = [d["month"] for d in data]
        totals = [d["total"] for d in data]

        fig = plt.Figure(figsize=(6,4))
        ax = fig.add_subplot(111)

        ax.bar(months, totals)

        ax.set_title("Monthly Rent Payments")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount (£)")

        canvas = FigureCanvasTkAgg(fig, popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def view_neighbour_graph(self):
        
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        popup = tk.Toplevel(self)
        popup.title("Neighbour Payment Comparison")
        popup.geometry("700x500")

        user = self.controller.current_user
        tenant_id = user["tenant_id"]

        data = get_neighbour_payment_totals(tenant_id)

        if not data:
            messagebox.showinfo("Info", "No data available.")
            popup.destroy()
            return
        
        names = [d["name"] for d in data]
        totals = [float(d["total"]) for d in data]

        fig = plt.Figure(figsize=(6,4))
        ax = fig.add_subplot(111)

        ax.bar(names, totals)

        ax.set_title("Tenant Payments Comparison")
        ax.set_xlabel("Tenants")
        ax.set_ylabel("Total Paid (£)")

        ax.tick_params(axis="x", rotation=45)

        canvas = FigureCanvasTkAgg(fig, popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    
    def view_late_payments_graph(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        popup = tk.Toplevel(self)
        popup.title("Late Payments by Property")
        popup.geometry("700x500")

        data = get_late_payments_per_property()

        if not data:
            messagebox.showinfo("Info", "No late payments found.")
            popup.destroy()
            return
        
        properties = [d["name"] for d in data]
        late_counts = [d["late_count"] for d in data]

        fig = plt.Figure(figsize=(6,4))
        ax = fig.add_subplot(111)

        ax.bar(properties, late_counts)

        ax.set_title("Late Payments per Property")
        ax.set_xlabel("Property")
        ax.set_ylabel("Number of Late Invoices")

        ax.tick_params(axis="x")

        canvas = FigureCanvasTkAgg(fig, popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def view_complaints(self):

        popup = tk.Toplevel(self)
        popup.title("My Complaints")
        popup.geometry("700x400")

        user = self.controller.current_user
        complaints = get_tenant_complaints(user["tenant_id"])

        columns = ("ID", "Description", "Status", "Date")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill="both", expand=True)

        for c in complaints:
            tree.insert("", "end", values=(
                c["complaint_id"],
                c["description"],
                c["status"],
                c["created_date"]
            ))


    def view_maintenance_requests(self):

        popup = tk.Toplevel(self)
        popup.title("My Maintenance Requests")
        popup.geometry("750x400")

        user = self.controller.current_user
        requests = get_tenant_maintenance_requests(user["tenant_id"])

        columns = ("ID", "Description", "Priority", "Status", "Date")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill="both", expand=True)

        if not requests:
            tree.insert("", "end", values=("No requests found", "", "", "", ""))
            return

        for r in requests:
            tree.insert("", "end", values=(
                r["request_id"],
                r["description"],
                r["priority"],
                r["status"],
                r["reported_date"]
            ))


    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")