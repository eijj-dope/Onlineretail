import mysql.connector
from config import DB_CONFIG

def get_db():
    return mysql.connector.connect(
        host=DB_CONFIG['localhost'],
        user=DB_CONFIG['Eijj_05'],
        password=DB_CONFIG['Russelflores2005'],
        database=DB_CONFIG['Online_store']
    )