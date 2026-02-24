from app.app import App
from db.schema import create_tables, seed_users, create_tenants_table
from auth.login_view import LoginView

from dashboards.admin import AdminDashboard
from dashboards.finance import FinanceDashboard
from dashboards.frontdesk import FrontdeskDashboard
from dashboards.maintenance import MaintenanceDashboard
from dashboards.manager import ManagerDashboard
from dashboards.tenant import TenantDashboard

from app.session import session

#print(session)

create_tables()
create_tenants_table()
seed_users()
app = App()


app.register_page(LoginView)
app.register_page(AdminDashboard)
app.register_page(FinanceDashboard)
app.register_page(FrontdeskDashboard)
app.register_page(MaintenanceDashboard)
app.register_page(ManagerDashboard)
app.register_page(TenantDashboard)


app.show_page("LoginView")
app.mainloop()

# Test