TABLES = {}

TABLES['owned_filed_details'] = (
    "CREATE TABLE `file_details` ("
    " `file_id` varchar(255) NOT NULL,"
    " `path` varchar(255) NOT NULL,"
    " `public_key` varchar(2048) NOT NULL,"
    " `private_key` varchar(2048) NOT NULL,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")

TABLES['replicated_file_details'] = (
    "CREATE TABLE `file_details` ("
    " `file_id` varchar(256) NOT NULL,"
    " `owner` varchar(256) NOT NULL,"
    " `path` varchar(256) NOT NULL,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")

TABLES['file_permissions'] = (
    "CREATE TABLE `file_details` ("
    " `file_id` varchar(256) NOT NULL,"
    " `owner` varchar(256) NOT NULL,"
    " `permission_write` boolean NOT NULL DEFAULT 0,"
    " `public_key` varchar(2048) NOT NULL,"
    " `private_key` varchar(2048) NOT NULL,"
    "  PRIMARY KEY (`file_id`)"
    ") ENGINE=InnoDB")
