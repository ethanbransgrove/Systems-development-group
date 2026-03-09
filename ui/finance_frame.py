from models.finance_model import get_active_leases, generate_next_invoice
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class FinanceFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Finance Manager Dashboard", font=("Arial", 20)).pack(pady=20)
        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=10)

        tk.Button(self, text="Generate Invoice", command=self.open_invoice_popup).pack(pady=10)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")


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

        lease_combo = ttk.Combobox(
            popup,
            values=lease_options,
            state="readonly"
        )
        lease_combo.pack(pady=10)

        def submit():

            if not lease_combo.get():
                messagebox.showerror("Error", "Please select a lease.")
                return

            lease_id = lease_dict[lease_combo.get()]

            success = generate_next_invoice(lease_id)

            if success:
                messagebox.showinfo(
                    "Success",
                    "Invoice generated automatically."
                )
                popup.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to generate invoice."
                )

        tk.Button(
            popup,
            text="Generate Invoice",
            command=submit
        ).pack(pady=20)