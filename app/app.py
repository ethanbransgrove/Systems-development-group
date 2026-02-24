import tkinter as tk

# Navigation

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Paragon Apartment Management System")
        self.geometry("1280x720")
        self.minsize(800, 600)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Dict to store pages
        self.pages = {}


    def register_page(self, page_class, *args, **kwargs):
        
        page_name = page_class.__name__

        page = page_class(
            parent=self.container,
            app=self, *args, **kwargs
        )

        self.pages[page_name] = page
        page.grid(row=0, column=0, sticky="nsew")


    def show_page(self, page_name):
        if page_name not in self.pages:
            raise ValueError(f"Page '{page_name}' not registered")
        
        page = self.pages[page_name]
        page.tkraise()
        

    def reset(self):
        for page in self.pages.values():
            if hasattr(page, "reset"):
                page.reset()


