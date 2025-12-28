"""
Explanation
DatabaseConnection Class:

The DatabaseConnection class abstracts the logic of connecting to Oracle databases. It accepts a data_source parameter (either "BSIS" or "EDI"), decrypts the credentials if necessary, and provides an interface to execute queries.
Reusability:

Both scripts (check_user_status.py and auth_token.py) import the DatabaseConnection class, making the database connection and query execution logic reusable and centralized.
Token Management:

The authenticate_user function checks if the user has a valid token. If not, it prompts for credentials, verifies the user’s existence and active status in the BSIS database, and then generates a new token.
"""

import os
import jwt  # Install this package with pip install pyjwt
from datetime import datetime, timedelta
from utils.database import DatabaseConnection
from utils.logger import Logger
from utils.license_manager import validate_license
import requests
import sys
import getpass
import pytz  # Import pytz for timezone handling

CERT_PATH = os.path.join(os.getcwd(), "certificate", "_.bot.go.tz.crt")

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../MSPUsersDev')))


# Define the secret key for token generation
#SECRET_KEY = "spectacular"
#SECRET_KEY = os.getenv("SECRET_KEY", "spectacular")
#LOGIN_URL = os.getenv("LOGIN_URL", "https://help.bot.go.tz:9090")
#CERT_PATH = os.getenv("CERT_PATH", "./certificate/_.bot.go.tz.crt")


SECRET_KEY = os.getenv("SECRET_KEY")
LOGIN_URL = os.getenv("LOGIN_URL")
#CERT_PATH = os.getenv("CERT_PATH")
#CERT_PATH = "_.bot.go.tz.crt"
#CERT_PATH = os.path.join(os.getcwd(), "certificate", "_.bot.go.tz.crt")

def generate_token(username):
    """Generate a JWT token with a 30-minute expiration."""
    logger = Logger()
    try:
        #expiration_time = datetime.utcnow() + timedelta(minutes=30)
        # Define GMT+3 timezone
        gmt_plus_3 = pytz.timezone("Etc/GMT-3")
        expiration_time = datetime.now(gmt_plus_3) + timedelta(minutes=30)
        token = jwt.encode({"username": username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")
        #logger.info(f"Access granted that expires at {expiration_time}(GMT+3)")
        #os.environ["USER_TOKEN"] = token
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None


def verify_token(token):
    """Verify if the token is valid and not expired."""
    logger = Logger()
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        #logger.info(f"User validated successfully")
        return decoded_token
    except jwt.ExpiredSignatureError:
        logger.debug(f"Token has expired") 
    except jwt.InvalidTokenError:
        logger.debug(f"Invalid token")
    return None  


def perform_domain_login(username, password):
    """Placeholder for domain login logic."""
    logger = Logger()
    session = requests.Session()
    payload = {"username": username, "password": password, "submit": "Login"}
    
    try:
        response = session.post(LOGIN_URL, data=payload, verify=CERT_PATH)
        if response.status_code == 200:
            logger.info("Domain validation completed successfully")
            return True
        else:
            logger.error(f"Login failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Domain login error: {e}")
        return False    
   
def perform_bsis_login(username, password):
    """Perform BSIS login by verifying user credentials in the BSIS database."""
   
    logger = Logger()
    

    
    try:
        with DatabaseConnection("BSIS") as db:
            
        
            # Create a cursor object
            cursor = db.cursor()
            
            

            # Define a variable to store the output (1 or 0)
            match_result = cursor.var(int)
            
            

            # Call the PL/SQL procedure
            cursor.callproc('bsis_dev.dt_match_user_password', [username, password, match_result])
            
            

            # Fetch the result of the match (1 if passwords match, 0 if they do not)
            if match_result.getvalue() == 1:
                #logger.info("Password match successful")
                return True
            else:
                logger.warning("Incorrect password")
                return False

    except Exception as e:
        logger.error(f"Database error during BSIS login: {e}")
        return False         

  
       
def authenticate_user():
    logger = Logger()    
    domainLogin = False
    token = ""
    
    try:
        token = os.getenv("USER_TOKEN")

        #if token:
        decoded_token = verify_token(token)
        if decoded_token:
            #logger.info(f"Existing token is valid")
            domainLogin = True
            return token
    
    except Exception as e:
        logger.error(f"{e}") 

    else:
        # Prompt for login credentials
        print("Please log in to continue.")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    
        username = username.upper()

        # Perform login and verify user status in BSIS database
        try:
            if not (perform_bsis_login(username, password) == 1):
                logger.error(f"Login failed.")
                return None
        except Exception as e:
            logger.error(f"Connectivity or other error: {e}")
                #return None

      

        # Generate and return a new token
        token = generate_token(username)
        if verify_token(token):
            os.environ["USER_TOKEN"] = token
            logger.info("Login successful")
            return token

def binary_convert(mask: str) -> str:
    """
    Convert a character into an 8-bit binary representation.
    :param mask: The input character to convert.
    :return: The binary representation as a string of 8 bits.
    """
    # Get ASCII value of the character
    value = ord(mask)
    
    # Convert to binary (8 bits) and return
    return format(value, '08b')


def cryption(mask: str, data: str) -> str:
    """
    Encrypt a string using the binary conversion and a comparison bit by bit.
    :param mask: The mask string used for encryption.
    :param data: The data string to encrypt.
    :return: The encrypted string result.
    """
    result = ''
    
    # Iterate over each character in the mask and data strings
    for i in range(len(mask)):
        r1 = binary_convert(mask[i])  # Convert mask character to binary
        r2 = binary_convert(data[i])  # Convert data character to binary
        
        divisor = 128
        r3 = 0
        
        # Compare bit by bit
        for j in range(8):
            if int(r1[j]) + int(r2[j]) == 1:
                r3 += divisor
            divisor //= 2
        
        # Append the resulting character to the result string
        result += chr(r3)
    
    return result


# Example usage
if __name__ == "__main__":
    mask = "THEBSISBANKOFTANZANIADARESSALAAM"
    data = "SECRETENCRYPTIONTEXT123"
    
    # Encrypt the data using the mask
    encrypted_data = cryption(mask, data)
    
    print("Encrypted Data:", encrypted_data)
# Example usage
#if __name__ == "__main__":
#    authenticate_user()
