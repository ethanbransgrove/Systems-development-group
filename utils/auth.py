# Group B3, Rory Foley (23071664), Zuhaib Asif (23039419), Ethan Bransgrove (23079243), Rodrigo Garrabou Socias (23018284)

import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
