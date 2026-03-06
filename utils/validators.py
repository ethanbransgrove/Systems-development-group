def validate_card_number(card_number):
    card_number = card_number.replace(" ", "")

    if card_number.isdigit() and len(card_number) == 16:
        return True
    
    return False