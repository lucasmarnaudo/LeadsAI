# db_config.py
import mysql.connector
from mysql.connector import Error

def connect():
    """Conecta con la base de datos MySQL y retorna la conexión y el cursor."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='usuario',
            password='.Inde3011',
            database='google_places'
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor(dictionary=True)
            return connection, cursor
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None, None

def close(connection, cursor):
    """Cierra el cursor y la conexión."""
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

# Bloque de prueba para ejecutar cuando este archivo sea el script principal
if __name__ == '__main__':
    print("Testing database connection...")
    conn, cur = connect()
    if conn is not None and conn.is_connected():
        print("Connection was successful!")
        close(conn, cur)
    else:
        print("Failed to connect to the database.")