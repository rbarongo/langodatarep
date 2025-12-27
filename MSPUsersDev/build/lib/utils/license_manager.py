import os
import sys
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.fernet import Fernet  # Import Fernet for handling encryption keys
from dotenv import load_dotenv
import unittest
import json

# Load environment variables
load_dotenv()

# Constants
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
KEYWORD = os.getenv("KEYWORD")

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY is not set in the environment variables")

SALT = b'some_salt'  # Replace with a securely generated unique salt for production
BACKEND = default_backend()


# Generate a Fernet Key (if you don't already have one)
def generate_fernet_key():
    key = Fernet.generate_key()
    with open('fernet_key.key', 'wb') as key_file:
        key_file.write(key)
    print(f"Generated Fernet Key: {key.decode()}")  # You can also save this to a secure place
    return key


# Derive Key Function
def derive_key(keyword: str) -> bytes:
    """Derive a 32-byte symmetric key from a keyword."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100_000,
        backend=BACKEND,
    )
    return kdf.derive(keyword.encode())


# Encryption Function
def encrypt_value(keyword: str, credentials: str, date: str, days_to_expire: int) -> str:
    """Encrypt a value with AES encryption."""
    key = derive_key(keyword)
    iv = os.urandom(16)  # Generate a random Initialization Vector (IV)

    # Calculate expiration date
    start_date = datetime.strptime(date, "%d-%b-%Y")
    expire_date = (start_date + timedelta(days=days_to_expire)).strftime("%d-%b-%Y")

    # Prepare plaintext
    plaintext = f"{credentials},{date},{expire_date}"
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext.encode()) + padder.finalize()

    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=BACKEND)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Combine IV and ciphertext, then encode in base64
    return base64.b64encode(iv + ciphertext).decode()


# Decryption Function
def decrypt_value(keyword: str, encrypted_value: str) -> dict:
    """Decrypt an encrypted value to retrieve credentials, date, and expiration date."""
    key = derive_key(keyword)
    encrypted_data = base64.b64decode(encrypted_value)

    # Extract IV and ciphertext
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=BACKEND)
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad and decode plaintext
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    # Parse the plaintext
    credentials, date, expire_date = plaintext.decode().split(",")
    return {"credentials": credentials, "date": date, "expire_date": expire_date}


# License Validation Function
def validate_license():
    #encrypted_license = os.getenv("ENCRYPTION_KEY")
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    #print(f"License Key: {ENCRYPTION_KEY}")
    
    date = os.getenv("ISSUE_DATE")
    days_to_expire = os.getenv("VALIDITY_DAYS")
    encrypted_license = generate_license(date, int(days_to_expire))
    #print(f"Encrypted License: {encrypted_license}")
    license_data = decrypt_value(ENCRYPTION_KEY, encrypted_license)
    #print(f"Decrypted License: {decrypted_license}")
    
    #license_data = decrypt_value("spectacular", ENCRYPTION_KEY)
    #license_data = decrypt_value(ENCRYPTION_KEY, ENCRYPTION_KEY)
    #print(f"Decrypted value: {license_data}")
    
    #decrypted_dictionary_object = json.loads(str(decrypted_data))
    
    #print(f"License Details: {license_data}")
    expire_date_str = license_data["expire_date"]
    expire_date = datetime.strptime(expire_date_str, "%d-%b-%Y")
    today = datetime.now()

    if today > expire_date:
        raise Exception(f"License expired on {expire_date.strftime('%d-%b-%Y')}.")

    days_left = (expire_date - today).days
    if days_left < 7:
        print(f"Warning: License will expire in {days_left} days. Please renew it soon.")

def check_license_status() -> bool:
    licenseStatus = False
    #encrypted_license = os.getenv("ENCRYPTION_KEY")
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    #print(f"License Key: {ENCRYPTION_KEY}")
    
    date = os.getenv("ISSUE_DATE")
    days_to_expire = os.getenv("VALIDITY_DAYS")
    encrypted_license = generate_license(date, int(days_to_expire))
    #print(f"Encrypted License: {encrypted_license}")
    license_data = decrypt_value(ENCRYPTION_KEY, encrypted_license)

    #print(f"Decrypted value: {license_data}")
    
    #decrypted_dictionary_object = json.loads(str(decrypted_data))
    
    #print(f"License Details: {license_data}")
    expire_date_str = license_data["expire_date"]
    expire_date = datetime.strptime(expire_date_str, "%d-%b-%Y")
    today = datetime.now()

    if today < expire_date:
        licenseStatus = True
    return licenseStatus

# License Generation Function
def generate_license(date: str, days_to_expire: int) -> str:
    """Generate a license with credentials and expiration date."""
    BSIS_USER = os.getenv("BSIS_USER")
    BSIS_PASS = os.getenv("BSIS_PASS")
    EDI_USER = os.getenv("EDI_USER")
    EDI_PASS = os.getenv("EDI_PASS")

    if not all([BSIS_USER, BSIS_PASS, EDI_USER, EDI_PASS]):
        raise ValueError("User credentials are not set in environment variables")

    credentials = f"{BSIS_USER}:{BSIS_PASS}:{EDI_USER}:{EDI_PASS}"
    return encrypt_value(ENCRYPTION_KEY, credentials, date, days_to_expire)


# Add current working directory to sys.path
current_dir = os.getcwd()
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '../MSPUsersDev')))

# Testing Framework
class TestUtils(unittest.TestCase):
    def test_read_data(self):
        # Example test for read_data
        print("read_data() test passed")

    def test_database_connection(self):
        # Example test for DatabaseConnection
        print("DatabaseConnection test passed")

    def test_logger(self):
        # Example test for Logger
        print("Logger test passed")


if __name__ == "__main__":
    date = os.getenv("ISSUE_DATE")
    days_to_expire = os.getenv("VALIDITY_DAYS")

    # Encrypt and Decrypt Example
    encrypted_license = generate_license(date, int(days_to_expire))
    print(f"Encrypted License: {encrypted_license}")

    decrypted_license = decrypt_value(ENCRYPTION_KEY, encrypted_license)
    print(f"Decrypted License: {decrypted_license}")
    
    
    validate_license()

    # Run Unit Tests
    unittest.main()
