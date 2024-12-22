# database.py
import cx_Oracle


class Database:
    def __init__(self, user, password, host, port, service_name):
        self.user = user
        self.password = password
        self.dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        self.connection = None

    def connect(self):
        try:
            self.connection = cx_Oracle.connect(
                user=self.user, password=self.password, dsn=self.dsn
            )
            print("Connection successful.")
        except cx_Oracle.DatabaseError as e:
            (error,) = e.args
            print(f"Database connection failed: {error.message}")
            self.connection = None

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                print("Connection closed successfully.")
            except cx_Oracle.DatabaseError as e:
                (error,) = e.args
                print(f"Failed to close connection: {error.message}")

    def execute_query(self, query, params=None):
        if not self.connection:
            print("No connection established.")
            return None

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except cx_Oracle.DatabaseError as e:
            (error,) = e.args
            print(f"Failed to execute query: {error.message}")
            return None
        finally:
            cursor.close()
