import tkinter as tk
from tkinter import messagebox, ttk
from models.tenant_model import get_tenant_details, get_tenant_invoices, update_late_invoices
from models.payment_model import get_tenant_payments, create_payment
from models.maintenance_model import create_maintenance_request
from models.complaint_model import create_complaint
from utils.validators import validate_card_number


class TenantFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Tenant Dashboard", font=("Arial", 20)).pack(pady=10)
        
        self.info_label = tk.Label(self, text="")
        self.info_label.pack(pady=5)

        tk.Button(self, text="View Payment History", command=self.view_payments).pack(pady=5)
        
        tk.Button(self, text="Submit Maintenance Request", command=self.submit_maintenance).pack(pady=5)
        
        tk.Button(self, text="Submit Complaint", command=self.submit_complaint).pack(pady=5)

        tk.Button(self, text="View My Invoices", command=self.view_invoices).pack(pady=5)
        
        tk.Button(self, text="Pay Invoice", command=self.open_payment_popup).pack(pady=5)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

        #self.output_box = tk.Text(self, height=15, width=80)
        #self.output_box.pack(pady=10)


    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            tenant = get_tenant_details(user["tenant_id"])
            self.info_label.config(
                text=f"Welcome {tenant['name']} | Email: {tenant['email']}"
            )
        super().tkraise(*args, **kwargs)


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
        popup.geometry("600x400")

        tk.Label(popup, text="Description").pack(pady=5)
        description_box = tk.Text(popup, height=5, width=40)
        description_box.pack(pady=5)

        tk.Label(popup, text="Priority").pack(pady=5)

        priority_var = tk.StringVar(value="LOW")
        priority_menu = tk.OptionMenu(popup, priority_var, "LOW", "MEDIUM", "HIGH")
        priority_menu.pack(pady=5)

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
        
        tk.Button(popup, text="Submit", command=submit).pack(pady=15)


    def submit_complaint(self):
        user = self.controller.current_user
        create_complaint(user["tenant_id"], "General Complaint")

        messagebox.showinfo("Success", "Complaint submitted.")


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



    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")