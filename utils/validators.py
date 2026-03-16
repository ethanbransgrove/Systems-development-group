import re

def validate_card_number(card_number):

    """
    Makes sure that the inputted card number is a number, is 16 didgits long and has no whitespaces
    """

    card_number = card_number.replace(" ", "")

    if card_number.isdigit() and len(card_number) == 16:
        return True
    
    return False


def check_password_strength(password):
    
    """
    Facilitates the creation of new passwords by telling the tenant how strong there new password is dynamically
    while they write it.
    """

    if len(password) < 8:
        return "Weak"
    
    if (re.search("[a-z]", password) and
        re.search("[A-Z]", password) and 
        re.search("[0-9]", password) and
        re.search("[!@#$%^&*£]", password)):
        return "Strong"
    
    return "Medium"