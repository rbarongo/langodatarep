import oracledb
import os
from utils.decryption import decrypt

class DatabaseConnection:
    def __init__(self, data_source):
        self.conn = None
        self.user = None
        self.password = None
        self.dsn = None

        if data_source == "BSIS":
            self.user = decrypt(os.getenv("BSIS_USER"))
            self.password = decrypt(os.getenv("BSIS_PASS"))
            self.dsn = os.getenv("BSIS_DSN")
        elif data_source == "EDI":
            self.user = decrypt(os.getenv("EDI_USER"))
            self.password = decrypt(os.getenv("EDI_PASS"))
            self.dsn = os.getenv("EDI_DSN")
            
    
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
