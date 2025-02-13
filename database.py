import psycopg2

DB_HOST = "localhost"
DB_NAME = "library_db"
DB_USER = "postgres"
DB_PASSWORD = "password"

connection = psycopg2.connect(
    host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
)
cursor = connection.cursor()



