import pymysql

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password=" ",
        database=" ",
        charset="utf8mb4"
    )
