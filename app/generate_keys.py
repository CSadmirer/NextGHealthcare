from cryptography.fernet import Fernet
import secrets

print("SECRET_KEY=" + secrets.token_hex(32))
print("ENCRYPTION_KEY=" + Fernet.generate_key().decode())
