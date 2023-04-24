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

add_or_update_node_details = ("INSERT INTO node_details"
                              " (ip_address, hostname, public_key)"
                              " VALUES (%s, %s, %s)"
                              " ON DUPLICATE KEY UPDATE"
                              " hostname=%s, public_key=%s")

query_all_owned_files = ("SELECT file_id FROM owned_files")

query_all_shared_files = ("SELECT file_id, permission_write"
                          " FROM replicated_file_permissions")

delete_from_owned_files = ("DELETE FROM owned_files WHERE file_id = %s")

delete_from_replicated_files = ("DELETE FROM"
                                " replicated_files WHERE file_id = %s")

delete_from_replicated_file_permissions = ("DELETE FROM"
                                           " replicated_file_permissions"
                                           " WHERE file_id = %s")

delete_from_file_details = ("DELETE FROM file_details WHERE file_details = %s")

add_or_update_permission_entry = ("INSERT INTO replicated_file_permissions"
                                  " (file_id, permission_write)"
                                  " VALUES (%s, %d)"
                                  " ON DUPLICATE KEY UPDATE"
                                  " permission_write=%d")

update_file_details = ("UPDATE file_details"
                       " SET public_key = %s, private_key = %s"
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

    def add_or_update_node_public_key(self, address, hostname, public_key):
        cursor = self.db_conn.cursor()

        node_info = (address, hostname, public_key, hostname, public_key)
        cursor.execute(add_or_update_node_details, node_info)

        self.db_conn.commit()
        cursor.close()

    def get_owned_files(self):
        owned_files = []
        cursor = self.db_conn.cursor()
        cursor.execute(query_all_owned_files)

        for row in cursor:
            owned_files.append(row[0])

        cursor.close()
        return owned_files

    def get_shared_files(self):
        shared_files = []
        cursor = self.db_conn.cursor()
        cursor.execute(query_all_shared_files)

        for row in cursor:
            shared_files.append({
                'file_id': row[0],
                'write': row[1]
            })

        cursor.close()
        return shared_files

    def delete_file_entry(self, file_id):
        cursor = self.db_conn.cursor()

        cursor.execute(delete_from_owned_files, [file_id])
        cursor.execute(delete_from_replicated_files, [file_id])
        cursor.execute(delete_from_replicated_file_permissions, [file_id])
        cursor.execute(delete_from_file_details, [file_id])

        self.db_conn.commit()
        cursor.close()

    def add_permission_entry(self, file_id, is_write_permission):
        cursor = self.db_conn.cursor()

        permission_info = (file_id, is_write_permission, is_write_permission)
        cursor.execute(add_or_update_permission_entry, permission_info)

        self.db_conn.commit()
        cursor.close()

    def update_file_details(self, file_id, private_key, public_key):
        cursor = self.db_conn.cursor()

        file_info = (public_key, private_key, file_id)
        cursor.execute(update_file_details, file_info)

        self.db_conn.commit()
        cursor.close()