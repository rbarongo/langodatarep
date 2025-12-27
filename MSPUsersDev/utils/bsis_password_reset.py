import random
import string
import requests
from database import DatabaseConnection


class PasswordReset:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def generate_password(self) -> str:
        """
        Generate a random password.
        :return: A new password string.
        """
        random_string = ''.join(random.choices(string.ascii_uppercase, k=4))  # 4 random uppercase letters
        return f"BSIS12{random_string}"

    def reset_password(self, username: str) -> str:
        """
        Reset the user's password in the database.
        :param username: The username whose password is being reset.
        :return: The new password.
        """
        try:
            # Generate a new password
            new_password = self.generate_password()

            # Define the PL/SQL block
            plsql_block = """
            DECLARE
                ex_date DATE;
                mask VARCHAR2(32) := 'THEBSISBANKOFTANZANIADARESSALAAM';
                result VARCHAR2(30);
            BEGIN
                -- Set expiry date to tomorrow
                SELECT SYSDATE + 1 INTO ex_date FROM DUAL;

                -- Change the user password
                EXECUTE IMMEDIATE 'ALTER USER ' || :username || ' IDENTIFIED BY ' || :new_password || 
                                  ' DEFAULT TABLESPACE users TEMPORARY TABLESPACE temp';

                -- Encrypt the password
                result := data_cryption.cryption(:new_password, mask);

                -- Update the user table
                UPDATE bsis_dev.bsis_users
                SET password = result,
                    expiry_date = ex_date,
                    account_status = 'A'
                WHERE username = :username;

                -- Commit the transaction
                COMMIT;
            END;
            """

            # Connect to the database and execute the PL/SQL block
            with self.db_connection.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(plsql_block, {
                        "username": username,
                        "new_password": new_password
                    })
                    print(f"Password reset successful. New password: {new_password}")
                    return new_password

        except Exception as e:
            print(f"An error occurred while resetting the password: {str(e)}")
            raise

    def send_email(self, username: str, new_password: str) -> None:
        """
        Send the new password to the user's email.
        :param username: The username whose password was reset.
        :param new_password: The new password to send.
        """
        email = f"{username}@bot.go.tz"
        subject = "Password Reset Notification"
        body = (
            f"Dear {username},\n\n"
            f"Your password has been successfully reset.\n\n"
            f"New Password: {new_password}\n\n"
            f"Please change your password immediately after logging in.\n\n"
            f"Best regards,\n"
            f"Bank of Tanzania Support Team"
        )

        # Prepare the email payload
        email_payload = {
            "to": email,
            "subject": subject,
            "body": body,
            "msaada_username": "ribarongo",
            "msaada_password": "Bank@4321",
            "url": "https://owa.bot.go.tz/owa"
        }

        try:
            # Simulate email sending using the specified URL
            response = requests.post(
                url="https://owa.bot.go.tz/owa/send-email",  # Adjust endpoint as needed
                json=email_payload
            )
            if response.status_code == 200:
                print(f"Email sent successfully to {email}.")
            else:
                print(f"Failed to send email to {email}. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred while sending the email: {str(e)}")


if __name__ == "__main__":
    # Example usage
    # Create a DatabaseConnection instance
    db_connection = DatabaseConnection(data_source="BSIS")  # Replace "BSIS" with the correct data source

    # Create an instance of PasswordReset
    password_reset = PasswordReset(db_connection)

    # Reset the password for a specific username
    username_to_reset = "example_user"  # Replace with the actual username
    try:
        new_password = password_reset.reset_password(username_to_reset)
        password_reset.send_email(username_to_reset, new_password)
    except Exception as e:
        print(f"Failed to reset password and send email: {str(e)}")
