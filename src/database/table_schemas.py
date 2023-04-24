TABLES = {}

TABLES['owned_files'] = (
    "CREATE TABLE `owned_files` ("
    " `file_id` varchar(255) NOT NULL,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")

TABLES['replicated_files'] = (
    "CREATE TABLE `replicated_files` ("
    " `file_id` varchar(256) NOT NULL,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")

TABLES['replicated_file_permissions'] = (
    "CREATE TABLE `replicated_file_permissions` ("
    " `file_id` varchar(256) NOT NULL,"
    " `permission_write` boolean NOT NULL DEFAULT 0,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")

TABLES['file_details'] = (
    "CREATE TABLE `file_details` ("
    " `file_id` varchar(256) NOT NULL,"
    " `en_file_name` BLOB NOT NULL,"
    " `owner` varchar(256) NOT NULL,"
    " `path` varchar(256) NOT NULL,"
    " `public_key` varchar(2048),"
    " `private_key` varchar(2048),"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")

TABLES['node_details'] = (
    "CREATE TABLE `node_details` ("
    " `ip_address` varchar(256) NOT NULL,"
    " `hostname` varchar(256) NOT NULL,"
    " `public_key` varchar(2048),"
    "  PRIMARY KEY (`ip_address`)"
    ") ENGINE=InnoDB")

TABLES['file_locks'] = (
    "CREATE TABLE `file_locks` ("
    " `file_id` varchar(256) NOT NULL,"
    " `locked` boolean NOT NULL DEFAULT 0,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")
