from models.frontdesk_model import (get_available_apartments, register_new_tenant)
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class FrontDeskFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Front Desk Dashboard", font=("Arial", 20)).pack(pady=20)
        
        self.welcome_label = tk.Label(self, text="")
        self.welcome_label.pack(pady=10)

        tk.Button(self, text="Register New Tenant", command=self.open_register_popup).pack(pady=10)

        tk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)

    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")

    
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


        # Submit Function
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

            success = register_new_tenant(
                tenant_data,
                start_date,
                end_date,
                apartment_id,
                branch_id
            )

            if success:
                messagebox.showinfo("Success", "Tenant registered successfully.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "Registration failed.")

        tk.Button(popup, text="Register Tenant", command=submit).pack(pady=20)