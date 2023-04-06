import mysql.connector
from mysql.connector import Error

class Database:

    def __init__(self):    
        try:
            # Create the connection object
            self.connection = mysql.connector.connect(
                host="data608-db.cplphre1gvif.us-east-2.rds.amazonaws.com", user="admin", passwd="Data608db")
            
            self.cursor = self.connection.cursor()

            if self.connection.is_connected():
                self.cursor.execute("USE Data608ProjectDB;")              

        except Error as e:
            print("Error while connecting to MySQL", e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._connection
    
    @connection.setter
    def connection(self, connection):
        self._connection = connection

    @property
    def cursor(self):
        return self._cursor
    
    @cursor.setter
    def cursor(self, cursor):
        self._cursor = cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()
