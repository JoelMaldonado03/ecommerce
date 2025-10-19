# utils.py - Funciones auxiliares (puede crecer con validaciones, hashing, etc.)
def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password  # Aquí deberías usar hashing real

