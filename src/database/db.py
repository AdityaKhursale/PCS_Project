import mysql.connector

from mysql.connector import errorcode


def db_connection(db_user="pcs", db_pswd=""):
    conn = mysql.connector.connect(
        user=db_user, password=db_pswd, host="localhost")
    return conn, conn.cursor()


def create_db(cursor, db_name):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


def db_conn(db_name):
    conn, cursor = db_connection()
    try:
        cursor.execute("USE {}".format(db_name))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(db_name))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_db(cursor, db_name)
            print("Database {} created successfully.".format(db_name))
            conn.database = db_name
        else:
            print(err)
            exit(1)

    cursor.close()
    return conn
