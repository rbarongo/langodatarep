import oracledb
import os
from langodata.utils.decryption import decrypt


def _get_env_and_decrypt(key: str) -> str:
    """Fetch environment variable `key` and decrypt it.

    Raises a ValueError with an informative message if the environment
    variable is missing or decryption fails.
    """
    val = os.getenv(key)
    if val is None:
        raise ValueError(f"Environment variable {key} is not set; cannot obtain credentials.")
    try:
        return decrypt(val)
    except Exception as e:
        raise ValueError(f"Failed to decrypt environment variable {key}: {e}")

class DatabaseConnection:
    def __init__(self, data_source):
        self.conn = None
        self.user = None
        self.password = None
        self.dsn = None

        if data_source == "BSIS":
            self.user = _get_env_and_decrypt("BSIS_USER")
            self.password = _get_env_and_decrypt("BSIS_PASS")
            self.dsn = os.getenv("BSIS_DSN")
        if data_source == "BSISA":
            self.user = _get_env_and_decrypt("BSIS_USERA")
            self.password = _get_env_and_decrypt("BSIS_PASSA")
            self.dsn = os.getenv("BSIS_DSN")    
        elif data_source == "EDI":
            self.user = _get_env_and_decrypt("EDI_USER")
            self.password = _get_env_and_decrypt("EDI_PASS")
            self.dsn = os.getenv("EDI_DSN")
        if data_source == "DWH":
            self.user = _get_env_and_decrypt("DWH_USER")
            self.password = _get_env_and_decrypt("DWH_PASS")
            self.dsn = os.getenv("DWH_DSN")           

  
    def connect(self):
        if not self.conn:
            self.conn = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
        return self.conn
        
    def cursor(self):
        """Get a cursor object."""
        return self.connect().cursor()    

    def __enter__(self):
        self.connect()
        return self

    def execute_query(self, query, params=None):
        with self.conn.cursor() as cursor:
            if params:
                return cursor.execute(query, params).fetchall()
            else:
                return cursor.execute(query).fetchall()


    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()


    # Expose user, password, and dsn as properties
    @property
    def get_user(self):
        return self.user

    @property
    def get_password(self):
        return self.password

    @property
    def get_dsn(self):
        return self.dsn