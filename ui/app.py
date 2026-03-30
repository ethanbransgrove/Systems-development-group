# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

import tkinter as tk

from ui.login_frame import LoginFrame
from ui.admin_frame import AdminFrame
from ui.manager_frame import ManagerFrame
from ui.finance_frame import FinanceFrame
from ui.frontdesk_frame import FrontDeskFrame
from ui.maintenance_frame import MaintenanceFrame
from ui.tenant_frame import TenantFrame


class PAMSApp(tk.Tk):

    """
    Main PAMS system and loads the different dashboards.
    """

    def __init__(self):
        super().__init__()

        self.title("PAMS System")

        self.state("zoomed")

        self.minsize(1200, 800)

        self.current_user = None

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)


        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Register all frames
        self.frames["Login"] = LoginFrame(container, self)
        self.frames["ADMIN"] = AdminFrame(container, self)
        self.frames["MANAGER"] = ManagerFrame(container, self)
        self.frames["FINANCE_MANAGER"] = FinanceFrame(container, self)
        self.frames["FRONT_DESK"] = FrontDeskFrame(container, self)
        self.frames["MAINTENANCE_STAFF"] = MaintenanceFrame(container, self)
        self.frames["TENANT"] = TenantFrame(container, self)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Login")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def set_user(self, user):
        self.current_user = user