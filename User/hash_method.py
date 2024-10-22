import hashlib
import secrets

# Password hashing functions
def hashing_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return salt, hashed

def login_hash(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()
