import mysql.connector


def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="P14Y3R",
        database="car_customizer"
    )