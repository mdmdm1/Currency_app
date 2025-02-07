from fastapi import FastAPI
import cx_Oracle

app = FastAPI()

# dsn = "localhost:1521/?service_name=MANAGEMENT4&encoding=utf8&nencoding=utf8"
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="MANAGEMENT4")
username = "admin"
password = "2024"


@app.get("/clients")
async def get_clients():
    connection = None
    cursor = None  # Initialize cursor to avoid "UnboundLocalError"
    try:
        connection = cx_Oracle.connect(username, password, dsn)
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM CUSTOMER")
        clients = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

        if not clients:
            return {"message": "No clients found"}
        return clients

    except cx_Oracle.DatabaseError as e:
        return {"error": f"Database error: {str(e)}"}

    finally:
        if cursor:  # Only close if cursor exists
            cursor.close()
        if connection:  # Only close if connection exists
            connection.close()
