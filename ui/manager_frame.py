import tkinter as tk
from tkinter import messagebox, ttk
from models.manager_model import (
    get_occupancy_by_location,
    get_performance_report_by_location,
    get_all_cities,
    add_new_city,
    get_leases_expiring_soon
)


class ManagerFrame(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Manager Dashboard", font=("Arial", 22, "bold")).pack(pady=10)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 11))
        self.welcome_label.pack(pady=5)

        # Main dashboard container
        dashboard = tk.Frame(self)
        dashboard.pack(expand=True)

        dashboard.columnconfigure(0, weight=1)
        dashboard.columnconfigure(1, weight=1)

        # Occupancy Section
        occupancy_frame = tk.LabelFrame(dashboard, text="Occupancy", padx=20, pady=15)
        occupancy_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        tk.Button(occupancy_frame,
                  text="View Occupancy by Location",
                  width=25,
                  font=("Arial", 10, "bold"),
                  command=self.view_occupancy).pack(pady=5)

        tk.Button(occupancy_frame,
                  text="View Expiring Leases",
                  width=25,
                  font=("Arial", 10, "bold"),
                  command=self.view_expiring_leases).pack(pady=5)

        # Reports Section
        reports_frame = tk.LabelFrame(dashboard, text="Reports", padx=20, pady=15)
        reports_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        tk.Button(reports_frame,
                  text="Performance Report by Location",
                  width=25,
                  font=("Arial", 10, "bold"),
                  command=self.view_performance_report).pack(pady=5)

        tk.Button(reports_frame,
                  text="Occupancy Graph",
                  width=25,
                  font=("Arial", 10, "bold"),
                  command=self.view_occupancy_graph).pack(pady=5)

        # Business Expansion Section
        expansion_frame = tk.LabelFrame(dashboard, text="Business Expansion", padx=20, pady=15)
        expansion_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")

        tk.Button(expansion_frame,
                  text="Add New City / Branch",
                  width=25,
                  font=("Arial", 10, "bold"),
                  command=self.add_city_popup).pack(pady=5)

        tk.Button(expansion_frame,
                  text="View All Cities",
                  width=25,
                  font=("Arial", 10, "bold"),
                  command=self.view_cities).pack(pady=5)

        # Logout
        tk.Button(self,
                  text="Logout",
                  width=25,
                  font=("Arial", 11, "bold"),
                  bg="#d9534f",
                  fg="white",
                  command=self.logout).pack(pady=25)


    def tkraise(self, *args, **kwargs):
        user = self.controller.current_user
        if user:
            self.welcome_label.config(text=f"Welcome {user['name']}")
        super().tkraise(*args, **kwargs)


    def view_occupancy(self):

        """
        Displays occupancy statistics per city showing total,
        occupied and vacant apartments.
        """

        popup = tk.Toplevel(self)
        popup.title("Occupancy by Location")
        popup.geometry("600x400")

        data = get_occupancy_by_location()

        columns = ("City", "Total Apartments", "Occupied", "Vacant")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)

        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        if not data:
            tree.insert("", "end", values=("No data found", "", "", ""))
            return

        for row in data:
            tree.insert("", "end", values=(
                row["city"],
                row["total_apartments"],
                row["occupied"],
                row["vacant"]
            ))


    def view_expiring_leases(self):

        """
        Shows all leases expiring in the next 60 days across all locations.
        """

        popup = tk.Toplevel(self)
        popup.title("Leases Expiring Soon (Next 60 Days)")
        popup.geometry("700x400")

        data = get_leases_expiring_soon()

        columns = ("Tenant", "Apartment", "City", "End Date")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160)

        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        if not data:
            tree.insert("", "end", values=("No expiring leases found", "", "", ""))
            return

        for row in data:
            tree.insert("", "end", values=(
                row["tenant_name"],
                row["apartment_number"],
                row["city"],
                row["end_date"]
            ))


    def view_performance_report(self):

        """
        Displays a financial performance report per city showing
        collected rent, pending rent and number of late payments.
        """

        popup = tk.Toplevel(self)
        popup.title("Performance Report by Location")
        popup.geometry("700x400")

        data = get_performance_report_by_location()

        columns = ("City", "Collected (£)", "Pending (£)", "Late Payments")

        tree = ttk.Treeview(popup, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160)

        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        if not data:
            tree.insert("", "end", values=("No data found", "", "", ""))
            return

        for row in data:
            tree.insert("", "end", values=(
                row["city"],
                f"£{row['collected']}",
                f"£{row['pending']}",
                row["late_payments"]
            ))


    def view_occupancy_graph(self):

        """
        Bar chart comparing occupied vs vacant apartments per city.
        """

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        popup = tk.Toplevel(self)
        popup.title("Occupancy Graph")
        popup.geometry("700x500")

        data = get_occupancy_by_location()

        if not data:
            messagebox.showinfo("Info", "No occupancy data available.")
            popup.destroy()
            return

        cities = [row["city"] for row in data]
        occupied = [row["occupied"] for row in data]
        vacant = [row["vacant"] for row in data]

        x = range(len(cities))
        bar_width = 0.35

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.bar([i - bar_width/2 for i in x], occupied, width=bar_width, label="Occupied")
        ax.bar([i + bar_width/2 for i in x], vacant, width=bar_width, label="Vacant")

        ax.set_title("Occupancy by Location")
        ax.set_xlabel("City")
        ax.set_ylabel("Number of Apartments")
        ax.set_xticks(list(x))
        ax.set_xticklabels(cities)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    def add_city_popup(self):

        """
        Allows the manager to expand the business by adding a new
        city and branch office. If the city already exists, just
        adds a new branch to it.
        """

        popup = tk.Toplevel(self)
        popup.title("Add New City / Branch")
        popup.geometry("400x300")

        tk.Label(popup, text="City Name *").pack(pady=5)
        city_entry = tk.Entry(popup, width=30)
        city_entry.pack(pady=5)

        tk.Label(popup, text="Branch Name *").pack(pady=5)
        branch_entry = tk.Entry(popup, width=30)
        branch_entry.pack(pady=5)

        tk.Label(popup, text="Branch Address *").pack(pady=5)
        address_entry = tk.Entry(popup, width=30)
        address_entry.pack(pady=5)

        def submit():
            city = city_entry.get().strip()
            branch = branch_entry.get().strip()
            address = address_entry.get().strip()

            if not city or not branch or not address:
                messagebox.showerror("Error", "All fields are required.")
                return

            success = add_new_city(city, branch, address)

            if success:
                messagebox.showinfo("Success", f"Branch '{branch}' added in {city}.")
                popup.destroy()
            else:
                messagebox.showerror("Error", "A branch with that name already exists.")

        tk.Button(popup, text="Add Branch", command=submit).pack(pady=20)


    def view_cities(self):

        """
        Displays all cities that currently have branches registered.
        """

        popup = tk.Toplevel(self)
        popup.title("All Cities")
        popup.geometry("300x400")

        cities = get_all_cities()

        tk.Label(popup, text="Cities", font=("Arial", 12, "bold")).pack(pady=10)

        listbox = tk.Listbox(popup, width=30, height=20, font=("Arial", 11))
        listbox.pack(pady=10, padx=10, fill="both", expand=True)

        if not cities:
            listbox.insert(tk.END, "No cities found")
            return

        for city in cities:
            listbox.insert(tk.END, city["name"])


    def logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("Login")