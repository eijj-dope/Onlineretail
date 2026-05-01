DB_CONFIG = {
    "host": "localhost",
    "user": "Eijj_05",
    "password": "Russelflores2005",
    "database": "online_store2"
}

SECRET_KEY = "supersecretkey123"

import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn