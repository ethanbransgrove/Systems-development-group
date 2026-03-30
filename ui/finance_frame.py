# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

from models.finance_model import (
    get_active_leases,
    generate_next_invoice,
    get_all_payments,
    get_all_invoices,
    get_outstanding_balance,
    get_late_payment_count,
    get_monthly_revenue
)

import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt


class FinanceFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Finance Manager Dashboard",
                 font=("Arial", 22, "bold")).pack(pady=10)

        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=5)

        # ===== SUMMARY =====
        summary_frame = tk.Frame(self)
        summary_frame.pack(pady=10)

        self.balance_label = tk.Label(summary_frame, text="", font=("Arial", 11))
        self.balance_label.grid(row=0, column=0, padx=20)

        self.late_label = tk.Label(summary_frame, text="", font=("Arial", 11))
        self.late_label.grid(row=0, column=1, padx=20)

        # ===== DASHBOARD =====
        dashboard = tk.Frame(self)
        dashboard.pack(expand=True)

        dashboard.columnconfigure(0, weight=1)
        dashboard.columnconfigure(1, weight=1)

        # ---- INVOICES ----
        invoice_frame = tk.LabelFrame(dashboard, text="Invoices", padx=20, pady=15)
        invoice_frame.grid(row=0, column=0, padx=15, pady=10)

        tk.Button(invoice_frame, text="Generate Invoice",
                  command=self.open_invoice_popup, width=25).pack(pady=5)

        tk.Button(invoice_frame, text="View All Invoices",
                  command=self.view_invoices, width=25).pack(pady=5)

        # ---- PAYMENTS ----
        payment_frame = tk.LabelFrame(dashboard, text="Payments", padx=20, pady=15)
        payment_frame.grid(row=0, column=1, padx=15, pady=10)

        tk.Button(payment_frame, text="View All Payments",
                  command=self.view_payments, width=25).pack(pady=5)

        tk.Button(payment_frame, text="Monthly Revenue Graph",
                  command=self.show_revenue_graph, width=25).pack(pady=5)

        # ---- LOGOUT ----
        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    # ===== REFRESH =====
    def tkraise(self, *args, **kwargs):

        user = self.controller.current_user

        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")

            balance = get_outstanding_balance()
            late = get_late_payment_count()

            self.balance_label.config(
                text=f"Outstanding Balance: £{balance}"
            )

            self.late_label.config(
                text=f"Late Payments: {late}"
            )

        super().tkraise(*args, **kwargs)

    # ===== VIEW PAYMENTS =====
    def view_payments(self):

        popup = tk.Toplevel(self)
        popup.title("All Payments")
        popup.geometry("700x400")

        data = get_all_payments()

        columns = ("Tenant", "Amount", "Date")
        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        tree.pack(fill="both", expand=True)

        if not data:
            tree.insert("", "end", values=("No payments found", "", ""))
            return

        for row in data:
            tree.insert("", "end", values=(
                row["tenant_name"],
                f"£{row['amount']}",
                row["payment_date"]
            ))

    # ===== VIEW INVOICES =====
    def view_invoices(self):

        popup = tk.Toplevel(self)
        popup.title("All Invoices")
        popup.geometry("700x400")

        data = get_all_invoices()

        columns = ("Tenant", "Amount", "Due Date", "Status")
        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill="both", expand=True)

        if not data:
            tree.insert("", "end", values=("No invoices", "", "", ""))
            return

        for row in data:
            tree.insert("", "end", values=(
                row["tenant_name"],
                f"£{row['amount_due']}",
                row["due_date"],
                row["status"]
            ))

    # ===== GRAPH =====
    def show_revenue_graph(self):

        data = get_monthly_revenue()

        if not data:
            messagebox.showinfo("Info", "No payment data available")
            return

        months = [row[0] for row in data]
        totals = [float(row[1]) for row in data]

        plt.figure()
        plt.plot(months, totals, marker='o')
        plt.title("Monthly Revenue")
        plt.xlabel("Month")
        plt.ylabel("Revenue (£)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # ===== EXISTING FUNCTION (UNCHANGED) =====
    def open_invoice_popup(self):

        popup = tk.Toplevel(self)
        popup.title("Generate Monthly Invoice")
        popup.geometry("600x400")

        branch_id = self.controller.current_user["branch_id"]

        leases = get_active_leases(branch_id)

        if not leases:
            messagebox.showinfo("Info", "No active leases found.")
            popup.destroy()
            return

        lease_dict = {}
        lease_options = []

        for lease in leases:
            display = (
                f"Lease {lease['lease_id']} - "
                f"{lease['tenant_name']} - "
                f"Apt {lease['apartment_number']} "
                f"(£{lease['monthly_rent']})"
            )
            lease_options.append(display)
            lease_dict[display] = lease["lease_id"]

        tk.Label(popup, text="Select Lease").pack(pady=15)

        lease_combo = ttk.Combobox(popup, values=lease_options, state="readonly")
        lease_combo.pack(pady=10)

        def submit():

            if not lease_combo.get():
                messagebox.showerror("Error", "Please select a lease.")
                return

            lease_id = lease_dict[lease_combo.get()]

            success = generate_next_invoice(lease_id)

            if success:
                messagebox.showinfo("Success", "Invoice generated.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to generate invoice.")

        tk.Button(popup, text="Generate Invoice", command=submit).pack(pady=20)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")