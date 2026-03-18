import re
from datetime import datetime


def validate_card_number(card_number):

    """
    FIX: Upgraded to use the Luhn algorithm — the industry standard for card validation.
    Still checks for 16 digits and no whitespaces as before.
    """

    card_number = card_number.replace(" ", "")

    if not card_number.isdigit() or len(card_number) != 16:
        return False

    # Luhn algorithm
    total = 0
    reverse = card_number[::-1]

    for i, digit in enumerate(reverse):
        n = int(digit)
        if i % 2 == 1:      # Double every second digit from the right
            n *= 2
            if n > 9:        # If result > 9, subtract 9
                n -= 9
        total += n

    return total % 10 == 0


def validate_expiry(expiry):

    """
    FIX: New function. Validates expiry date in MM/YY format and rejects expired cards.
    """

    if not re.match(r"^\d{2}/\d{2}$", expiry):
        return False

    try:
        month, year = expiry.split("/")
        month = int(month)
        year = int("20" + year)

        if month < 1 or month > 12:
            return False

        now = datetime.now()
        expiry_date = datetime(year, month, 1)

        return expiry_date >= datetime(now.year, now.month, 1)

    except ValueError:
        return False


def validate_cvv(cvv):

    """
    FIX: New function. Validates CVV — must be exactly 3 digits.
    """

    return cvv.isdigit() and len(cvv) == 3


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