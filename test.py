import oracledb

try:
    cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient")
    print("Oracle Instant Client is properly configured.")
except cx_Oracle.DatabaseError as e:
    print(f"Error: {e}")
