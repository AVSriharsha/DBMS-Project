import mysql.connector


def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Arvinth@1980820716",
        database="car_customizer"
    )