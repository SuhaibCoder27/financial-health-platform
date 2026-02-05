import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="mydb",
        user="postgres",
        password="2709",
        host="localhost",
        port="5432"
    )
    return conn
