import database.db as db

add_owned_file_details = ("INSERT INTO owned_file_details"
                          " (file_id, path, en_file_name, public_key, private_key)"
                          " VALUES (%s, %s, %s, %s, %s)")


class DfsDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_conn, self.db_cursor = db.db_conn(db_name)
        db.create_dfs_tables(self.db_cursor)

    def save_new_file_info(self, file_id, file_path, en_file_name, public_key, private_key):
        file_info = (file_id, file_path, en_file_name, public_key, private_key)
        self.db_cursor.execute(add_owned_file_details, file_info)

        self.db_conn.commit()
