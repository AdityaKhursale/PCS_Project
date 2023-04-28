import database.db as db
import mysql.connector

from mysql.connector import errorcode
from database.table_schemas import TABLES
from utils.misc import getLogger
from utils import constants

add_owned_files = ("INSERT INTO owned_files (file_id) VALUES (%s)")

add_replicated_files = ("INSERT INTO replicated_files (file_id) VALUES (%s)")

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

query_node_public_key = (
    "SELECT public_key FROM node_details WHERE ip_address = %s")

query_all_owned_files = ("SELECT file_id FROM owned_files")

query_all_shared_files = ("SELECT file_id, permission_write"
                          " FROM replicated_file_permissions")

delete_from_owned_files = ("DELETE FROM owned_files WHERE file_id = %s")

delete_from_replicated_files = ("DELETE FROM"
                                " replicated_files WHERE file_id = %s")

delete_from_replicated_file_permissions = ("DELETE FROM"
                                           " replicated_file_permissions"
                                           " WHERE file_id = %s")

delete_from_file_details = ("DELETE FROM file_details WHERE file_id = %s")

add_or_update_permission_entry_repl = ("INSERT INTO"
                                       " replicated_file_permissions"
                                       " (file_id, permission_write)"
                                       " VALUES (%s, %s)"
                                       " ON DUPLICATE KEY UPDATE"
                                       " permission_write=%s")

update_file_info = ("UPDATE file_details"
                    " SET public_key = %s, private_key = %s"
                    " WHERE file_id = %s")

query_file_lock = (
    "SELECT locked, ip_address FROM file_locks where file_id = %s")

create_file_lock = ("INSERT INTO file_locks"
                    " (file_id, locked, ip_address)"
                    " VALUES (%s, %s, %s)")

delete_file_lock = ("DELETE FROM file_locks WHERE file_id = %s")

add_or_update_permission_entry = ("INSERT INTO granted_permissions"
                                  " (file_id, ip_address, permission)"
                                  " VALUES (%s, %s, %s)"
                                  " ON DUPLICATE KEY UPDATE"
                                  " permission=%s")


class DfsDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_conn = db.db_conn(db_name)
        self.logger = getLogger(
            "database", {"$HOSTNAME": constants.host_name})
        self.create_dfs_tables()

    def create_dfs_tables(self):
        cursor = self.db_conn.cursor()

        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                self.logger.info(f"Creating table {table_name}")
                cursor.execute(table_description)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.info(f"Table {table_name} already exists.")
                else:
                    self.logger.error(err.msg)
            else:
                self.logger.info("OK")

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

    def save_replication_file_info(self, file_id, file_path,
                                   en_file_name, owner):
        # Add entry to tables `replicated_files` and `file_details`.
        file_info = (file_id, en_file_name, owner, file_path, "", "")

        cursor = self.db_conn.cursor()

        cursor.execute(add_replicated_files, [file_id])
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

    def get_node_public_key(self, address):
        public_key = b""
        cursor = self.db_conn.cursor()
        cursor.execute(query_node_public_key, [address])

        for row in cursor:
            public_key = row[0]

        cursor.close()
        return public_key

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
        cursor.execute(add_or_update_permission_entry_repl, permission_info)
        self.db_conn.commit()
        cursor.close()

    def update_file_details(self, file_id, private_key, public_key):
        cursor = self.db_conn.cursor()

        file_info = (public_key, private_key, file_id)
        cursor.execute(update_file_info, file_info)

        self.db_conn.commit()
        cursor.close()

    def is_file_locked(self, file_id):
        cursor = self.db_conn.cursor()
        cursor.execute(query_file_lock, [file_id])

        file_locked = False
        for row in cursor:
            file_locked = row[0]

        cursor.close()
        return file_locked

    def get_file_lock_owner_ip(self, file_id):
        cursor = self.db_conn.cursor()
        cursor.execute(query_file_lock, [file_id])

        ip_address = ""
        for row in cursor:
            ip_address = row[1]

        cursor.close()
        return ip_address

    def get_file_lock(self, ip_address, file_id):
        cursor = self.db_conn.cursor()
        lock_info = [file_id, 1, ip_address]
        cursor.execute(create_file_lock, lock_info)
        self.db_conn.commit()
        cursor.close()

    def release_file_lock(self, file_id):
        cursor = self.db_conn.cursor()
        cursor.execute(delete_file_lock, [file_id])
        self.db_conn.commit()
        cursor.close()

    def add_granted_permission_entry(self, file_id, ip_address, permission):
        cursor = self.db_conn.cursor()

        permission_info = (file_id, ip_address, permission, permission)
        cursor.execute(add_or_update_permission_entry, permission_info)

        self.db_conn.commit()
        cursor.close()
