ROLE_PERMISSIONS = {    # Roles and Actions
    "frontdesk": {
        "register_tenant",
        "create_maintenance_request",
        "log_complaint",
        "view_tenant"
    },

    "finance": {
        "generate_invoice",
        "record_payment",
        "generate_financial_report"
    },

    "maintenance": {
        "view_maintenance_request",
        "resolve_maintenance",
        "update_status"
    },

    "admin": {
        "manage_users",
        "manage_apartments",
        "generate_location_report",
        "view_tenant",
        "track_leases"
    },

    "manager": {
        "view_reports",
        "view_occupancy",
        "add_city",
        "generate_performance_report"
    },

    # For Systems Development Project ALSO
    "tenant": {
        "request_early_termination",
        "send_maintenance_request",
        "send_complaint",
        "view_repair_progress",
        "view_payment_history",
        "make_payment",
        "generate_payment_graph"
    }
}


def has_permission(role, action):
    if role not in ROLE_PERMISSIONS:
        return False
    
    return action in ROLE_PERMISSIONS[role]


def get_permissions_for_role(role):
    return ROLE_PERMISSIONS.get(role, set())