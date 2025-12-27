"""
from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()
print(f"Your new encryption key: {key.decode()}")

Make sure .env is not included in version control (e.g., Git). To do this, add .env to your .gitignore file.
"""

#from cryptography.fernet import Fernet

#import os
#from dotenv import load_dotenv

#load_dotenv()
#ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # Fetch the key from .env or a secure location

#if not ENCRYPTION_KEY:
#    raise ValueError(
#        "Encryption key is missing! Ensure the .env file is properly configured "
#        "and contains the ENCRYPTION_KEY variable."
#    )

# Initialize the Fernet decryption object
#cipher = Fernet(ENCRYPTION_KEY)

    
def decrypt(credential: str) -> str:
    try:
        listZ = credential[::-1].split('ukr')
        
        # Ensure the split produces at least two parts
        if len(listZ) < 2:
            raise ValueError("Invalid credential format: 'ukr' delimiter not found.")
     
        x = listZ[0][::-1]
        y = listZ[1][::-1]
        fin = ""
        for valY in range(len(y)-1):
            fin = fin + y[valY] + x[valY]
        decrypted = fin + y[-1]
        return decrypted.strip()    
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
        
        
def encrypt(original: str) -> str:
    try:
        # Split the original string into two interleaved parts
        x = original[::2]  # Characters at even indices
        y = original[1::2]  # Characters at odd indices
        
        # Reverse the two parts
        reversed_x = x[::-1]
        reversed_y = y[::-1]
        
        # Combine the reversed parts with 'ukr' in between
        interleaved = reversed_y + "ukr" + reversed_x
        
        # Reverse the entire string to produce the encrypted output
        encrypted = interleaved[::-1]
        return encrypted
    except Exception as e:
        raise ValueError(f"Encryption failed: {e}")   
"""
def decrypt_key(encrypted_data: bytes) -> str:
    
    #Decrypts the given encrypted data using the predefined encryption key.
    
    #Args:
    #    encrypted_data (bytes): The data to decrypt (must be in bytes format).
    
    #Returns:
    #    str: The decrypted string.
    
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode("utf-8")  # Convert bytes to string
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")        

def decrypt_license(encrypted_value: str) -> str:
    
    #Decrypts a base64-encoded string value.
    
    #Args:
    #    encrypted_value (str): The encrypted string to decrypt (in base64 format).
    
    #Returns:
    #   str: The decrypted value.

    try:
        encrypted_bytes = encrypted_value.encode("utf-8")  # Convert string to bytes
        return decrypt_key(encrypted_bytes)
    except Exception as e:
        raise ValueError(f"Decryption of value failed: {e}")

"""