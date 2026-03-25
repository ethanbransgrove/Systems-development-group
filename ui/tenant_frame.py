import tkinter as tk
from tkinter import messagebox, ttk
from models.tenant_model import get_tenant_details, get_tenant_invoices, update_late_invoices, create_late_payment_notification, get_late_invoice_count
from models.payment_model import get_tenant_payments, create_payment, get_monthly_payments, get_neighbour_payment_totals
from models.maintenance_model import create_maintenance_request, get_tenant_maintenance_requests
from models.complaint_model import create_complaint, get_tenant_complaints
from models.notification_model import get_unread_notifications, mark_notifications_read, get_all_notifications
from models.analytics_model import get_late_payments_per_property
from models.user_model import update_user_password
from utils.validators import validate_card_number, validate_expiry, validate_cvv, check_password_strength

"""  
This is the Tenant dashboard as required by the Systems development group project. 
Which is an extension of the ASD project.
"""

class TenantFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        """ 
        This section of the class creates all the buttons which appear as part of the UI.
        The they are in sets where the functions are aligned so the user can find the desired
        action faster. 
        """

        tk.Label(self, text="Tenant Dashboard", font=("Arial", 22, "bold")).pack(pady=10)

        self.info_label = tk.Label(self, text="", font=("Arial", 11))
        self.info_label.pack(pady=5)

        # Late payment warning banner. Hidden by default
        self.warning_label = tk.Label(
            self,
            text="",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#d9534f",
            padx=10,
            pady=5
        )

        self.warning_label.pack(side= "bottom", fill="x")
        self.warning_label.pack_forget()

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
        
        tk.Button(notification_frame,
                  text="Change Password",
                  width=20,
                  font=("Arial",10,"bold"),
                  command=self.change_password).pack(pady=5)
        

        # Analytics Section
        analytics_frame = tk.LabelFrame(dashboard, text="Tenant Analytics", padx=20, pady=15)
        analytics_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")

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
                  font=("Arial",10,"bold"),
                  bg="#d9534f",
                  fg="white",
                  command=self.logout).pack(side="bottom")


    def tkraise(self, *args, **kwargs):
        
        """ 
        This function establishes who the tenant who has logged in is and makes sure the notification
        system is up to date and checks for late payments to display a warning banner to the user. 
        """
        
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


            late_count = get_late_invoice_count(tenant_id)

            if late_count > 0:
                self.warning_label.config(
                    text=f"WARNING: You have {late_count} overdue invoice(s)"
                )
                self.warning_label.pack(pady=5, fill="x")
            else:
                self.warning_label.pack_forget()


            # Get unread notifications
            notifications = get_unread_notifications(user_id)

            if notifications:

                messages = "\n\n".join(n["message"] for n in notifications[:3])

                messagebox.showwarning(
                    "Notifications",
                    messages
                )


    def view_payments(self):

        """ 
        As a requirement tenants should be able to see there previous payments in table format.
        This function displays all previous payments the tenant has made. 
        """

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

        """ 
        Tenants have the ability to make maintenance request which are logged directly in the 
        database so that staff can log the request.
             
        A tenant can describe what the problem is. If field is left empty this request wont be 
        logged. 
        """

        popup = tk.Toplevel(self)
        popup.title("New Maintenance Request")
        popup.geometry("500x320")

        form = tk.Frame(popup, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Maintenance Request", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=(0,15))

        tk.Label(form, text="Description:").grid(row=1, column=0, sticky="nw")

        description_box = tk.Text(form, height=6, width=40)
        description_box.grid(row=1, column=1, pady=5)

        # FIX: Re-added priority dropdown
        tk.Label(form, text="Priority:").grid(row=2, column=0, sticky="w", pady=5)
        priority_var = tk.StringVar(value="LOW")
        tk.OptionMenu(form, priority_var, "LOW", "MEDIUM", "HIGH").grid(row=2, column=1, sticky="w", pady=5)

        button_frame = tk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        def submit():

            description = description_box.get("1.0", tk.END).strip()
            priority = priority_var.get()
            user = self.controller.current_user

            if not description:
                messagebox.showerror("Error", "Description cannot be empty.")
                return

            success = create_maintenance_request(
                user["tenant_id"],
                description,
                priority
            )

            if success:
                messagebox.showinfo("Success", "Maintenance request submitted.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "No active lease found.")

        tk.Button(button_frame, text="Submit", width=12, command=submit).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", width=12, command=popup.destroy).pack(side="left", padx=10)


    def submit_complaint(self):

        """ 
        Tenants can submit complaints directly to the database which can then be processed by staff.
        Tenants can describe their complaint in the text box. If empty the complaint is not logged. 
        """

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

        """
        Tenants are able to see a log of their unpaid invoices and see wether they are unpaid, late, or paid.
        This function pulls the tenant's current invoices straight from the database and displays them. 
        """

        popup = tk.Toplevel(self)
        popup.title("My Invoices")
        popup.geometry("800x400")

        user = self.controller.current_user
        tenant_id = user["tenant_id"]

        # Automatically update late invoices first
        update_late_invoices(tenant_id)

        invoices = get_tenant_invoices(tenant_id)

        columns = ("ID", "Period", "Amount", "Due Date", "Status")

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

        """
        This function is the way that tenants can pay there invoice.
        
        Displays a drop down menu for the tenant to select which invoice they would like to pay.
        
        Then the tenant can input their card details (which get validated) and then the payment is logged
        in the database.
        """

        popup = tk.Toplevel(self)
        popup.title("Pay Invoice")
        popup.geometry("500x420")

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

        # FIX: Added expiry and CVV fields
        tk.Label(popup, text="Expiry Date (MM/YY)").pack(pady=5)
        expiry_entry = tk.Entry(popup, width=10)
        expiry_entry.pack(pady=5)

        tk.Label(popup, text="CVV (3 digits)").pack(pady=5)
        cvv_entry = tk.Entry(popup, show="*", width=6)
        cvv_entry.pack(pady=5)

        def submit_payment():

            selected = invoice_menu.current()

            if selected == -1:
                messagebox.showerror("Error", "Select an invoice.")
                return

            card_number = card_entry.get()
            expiry = expiry_entry.get().strip()
            cvv = cvv_entry.get().strip()

            if not validate_card_number(card_number):
                messagebox.showerror("Error", "Invalid card number.")
                return

            # FIX: Added expiry and CVV validation
            if not validate_expiry(expiry):
                messagebox.showerror("Error", "Invalid or expired expiry date. Use MM/YY format.")
                return

            if not validate_cvv(cvv):
                messagebox.showerror("Error", "Invalid CVV. Must be 3 digits.")
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

        """
        Tenants need to be aware that they may have a payment which is late which this function will
        show them. 
        Once the tenant opens the notification menu each notification status is set to "read" to signify
        they have viewed this notification before.
        """

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

        """
        Tenants are able to see graphical representations of their payments.

        This function displays a graph which shows how much money the tenant has paid in total that month

        Tenants can decide to pay for multiple months upfront and therefore the graph can show a higher total
        for said month.
        """

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
        
        """
        Tenants can also see a graphical representation of there payment totals as
        compared to their neighbours in the same building.

        This is a bar chart with the neighbour name and the total they have spent.
        """

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

        """
        Tenants can see a graphical representation the total amount of 
        late payments due in their building.

        If all tenants in the building have paid their invoice then the graph will not display.

        If a tenant in the building has a late payment due then this will display on the graph.
        """

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
        
        """ 
        As tenants can submit complaints they also can see a log of previous complaints they have
        submitted.

        This function displays in table format all previous and active complaints.

        Staff can also update the status of complaints which then get displayed in this table to show
        the progress of the complaint. 
        """

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

        """ 
        Tenants can see in table format a log of requests they have made.
        They can also see the status of each request which gets updated by staff and shown here.
        """

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


    def change_password(self):
        
        """
        When tenants are first logged to the system and put into the database they have a default password.

        This function allows a tenant to update there password.

        Also this function dynamically tells the tenant how strong or weak their password is.
        """

        popup = tk.Toplevel(self)
        popup.title("Change Password")
        popup.geometry("400x300")

        tk.Label(popup, text="New Password").pack(pady=5)
        password_entry = tk.Entry(popup, show="*")
        password_entry.pack(pady=5)

        tk.Label(popup, text="Confirm Password").pack(pady=5)
        confirm_entry = tk.Entry(popup, show="*")
        confirm_entry.pack(pady=5)

        strength_label = tk.Label(popup, text="Strength: ")
        strength_label.pack(pady=5)

        def check_strength(event):
            password = password_entry.get()
            strength = check_password_strength(password)
            strength_label.config(text=f"Strength: {strength}")

        password_entry.bind("<KeyRelease>", check_strength)

        def submit():

            password = password_entry.get()
            confirm = confirm_entry.get()

            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            
            user = self.controller.current_user

            success = update_user_password(user["user_id"], password)

            if success:
                messagebox.showinfo("Success", "Password updated successfully")
            else:
                messagebox.showerror("Error", "Password update failed")

        tk.Button(popup, text="Update Password", command=submit).pack(pady=20)


    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")