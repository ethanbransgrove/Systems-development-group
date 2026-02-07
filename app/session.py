session = {
    "user_id": None,
    "name": None,
    "role": None,
    "city": None,
    "authenticated": False
}

def login(user_id, name, role, city):
    session["user_id"] = user_id
    session["name"] = name
    session["role"] = role
    session["city"] = city
    session["authenticated"] = True


def logout():
    session["user_id"] = None
    session["name"] = None
    session["role"] = None
    session["city"] = None
    session["authenticated"] = False


def is_auth():
    return session["authenticated"]


def has_role(role):
    return session["role"] == role