# Student: [Your Name] | Student ID: [Your ID]

import tkinter as tk
from models.tenant_model import get_tenant_details
from models.payment_model import get_tenant_payments


class TenantFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Tenant Dashboard", font=("Arial", 20)).pack(pady=10)

        self.info_label = tk.Label(self, text="")
        self.info_label.pack(pady=5)

        tk.Button(self, text="View Payment History", command=self.view_payments).pack(pady=5)
        tk.Button(self, text="View Maintenance Requests", command=self.view_maintenance).pack(pady=5)
        tk.Button(self, text="View Complaints", command=self.view_complaints).pack(pady=5)
        tk.Button(self, text="Make Payment", command=self.make_payment).pack(pady=5)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

        self.output_box = tk.Text(self, height=15, width=80)
        self.output_box.pack(pady=10)


    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            tenant = get_tenant_details(user["tenant_id"])
            self.info_label.config(
                text=f"Welcome {tenant['name']} | Email: {tenant['email']}"
            )
        super().tkraise(*args, **kwargs)


    def view_payments(self):
        user = self.controller.current_user
        payments = get_tenant_payments(user["tenant_id"])

        self.output_box.delete("1.0", tk.END)

        if not payments:
            self.output_box.insert(tk.END, "No payments found.\n")
            return

        for payment in payments:
            self.output_box.insert(
                tk.END,
                f"£{payment['amount']} | {payment['payment_date']} | {payment['status']}\n"
            )


    def view_maintenance(self):
        # TODO (Fares): Display read-only list of this tenant's maintenance requests and their status
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Maintenance request progress will appear here.\n")


    def view_complaints(self):
        # TODO (Rodrigo): Display read-only list of this tenant's complaints and their status
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Complaint status will appear here.\n")


    def make_payment(self):
        # TODO (Ethan): Open payment popup with card validation
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Payment feature coming soon.\n")


    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")