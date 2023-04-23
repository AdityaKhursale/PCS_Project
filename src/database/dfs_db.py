import database.db as db
import mysql.connector

from mysql.connector import errorcode
from database.table_schemas import TABLES

add_owned_files = ("INSERT INTO owned_files (file_id) VALUES (%s)")


add_file_details = ("INSERT INTO file_details"
                    " (file_id, en_file_name, owner, path, public_key,"
                    " private_key)"
                    " VALUES (%s, %s, %s, %s, %s, %s)")

query_file_details = ("SELECT file_id, en_file_name, owner, path, public_key,"
                      " private_key FROM file_details"
                      " WHERE file_id = %s")


class DfsDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_conn = db.db_conn(db_name)
        self.create_dfs_tables()

    def create_dfs_tables(self):
        cursor = self.db_conn.cursor()

        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print("Creating table {}: ".format(table_name), end='')
                cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("\n\t -> already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

        cursor.close()

    def save_new_file_info(self, file_id, file_path,
                           en_file_name, owner, public_key, private_key):
        # Add entry to tables `owned_files` and `file_details`.
        file_info = (file_id, en_file_name, owner,
                     file_path, public_key, private_key)

        cursor = self.db_conn.cursor()

        cursor.execute(add_owned_files, [file_id])
        cursor.execute(add_file_details, file_info)

        self.db_conn.commit()
        cursor.close()

    def get_file_details(self, file_id):
        file_details = {}
        cursor = self.db_conn.cursor()
        cursor.execute(query_file_details, [file_id])

        for (file_id, en_file_name, owner, file_path, public_key,
             private_key) in cursor:
            # There will be only one record in the query response.
            file_details['file_id'] = file_id
            file_details['en_file_name'] = en_file_name
            file_details['owner'] = owner
            file_details['file_path'] = file_path
            file_details['public_key'] = public_key
            file_details['private_key'] = private_key

        cursor.close()

        return file_details
