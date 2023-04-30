import mysql.connector

from database.table_schemas import TABLES
from mysql.connector import errorcode
from utils import constants
from utils.misc import getLogger

addOwnedFiles = ("INSERT INTO owned_files (file_id) VALUES (%s)")

addReplicatedFiles = ("INSERT INTO replicated_files (file_id) VALUES (%s)")

addFileDetails = ("INSERT INTO file_details"
                  " (file_id, en_file_name, owner, path, public_key,"
                  " private_key)"
                  " VALUES (%s, %s, %s, %s, %s, %s)")

queryFileDetails = ("SELECT file_id, en_file_name, owner, path, public_key,"
                    " private_key FROM file_details"
                    " WHERE file_id = %s")

addOrUpdateNodeDetails = ("INSERT INTO node_details"
                          " (ip_address, hostname, public_key)"
                          " VALUES (%s, %s, %s)"
                          " ON DUPLICATE KEY UPDATE"
                          " hostname=%s, public_key=%s")

queryNodePublicKey = (
    "SELECT public_key FROM node_details WHERE ip_address = %s")

queryAllOwnedFiles = ("SELECT file_id FROM owned_files")

queryAllSharedFiles = ("SELECT file_id, permission_write"
                       " FROM replicated_file_permissions")

deleteFromOwnedFiles = ("DELETE FROM owned_files WHERE file_id = %s")

deleteFromReplicatedFiles = ("DELETE FROM"
                             " replicated_files WHERE file_id = %s")

deleteFromReplicatedFilePermissions = ("DELETE FROM"
                                       " replicated_file_permissions"
                                       " WHERE file_id = %s")

deleteFromFileDetails = ("DELETE FROM file_details WHERE file_id = %s")

addOrUpdatePermissionEntryRepl = ("INSERT INTO"
                                  " replicated_file_permissions"
                                  " (file_id, permission_write)"
                                  " VALUES (%s, %s)"
                                  " ON DUPLICATE KEY UPDATE"
                                  " permission_write=%s")

updateFileInfo = ("UPDATE file_details"
                  " SET public_key = %s, private_key = %s"
                  " WHERE file_id = %s")

queryFileLock = (
    "SELECT locked, ip_address FROM file_locks where file_id = %s")

createFileLock = ("INSERT INTO file_locks"
                  " (file_id, locked, ip_address)"
                  " VALUES (%s, %s, %s)")

deleteFileLock = ("DELETE FROM file_locks WHERE file_id = %s")

addOrUpdatePermissionEntry = ("INSERT INTO granted_permissions"
                              " (file_id, ip_address, permission)"
                              " VALUES (%s, %s, %s)"
                              " ON DUPLICATE KEY UPDATE"
                              " permission=%s")

storeDeletedFileKeys = ("INSERT IGNORE INTO deleted_files"
                        " (file_id, public_key, private_key)"
                        " VALUES (%s, %s, %s)")


queryDeletedFileKeys = ("SELECT public_key, private_key"
                        " FROM deleted_files"
                        " WHERE file_id = %s")


class DfsDB:
    def __init__(self, dbName):
        self.dbName = dbName
        self.logger = getLogger(
            "database", {"$HOSTNAME": constants.host_name})
        self.connect()
        self.createTables()

    @property
    def username(self):
        return "pcs"

    @property
    def password(self):
        return ""

    def connect(self):
        # TODO: Check and update host
        self.conn = mysql.connector.connect(
            user=self.username, password=self.password, host="localhost")
        cursor = self.conn.cursor()

        try:
            cursor.execute("USE {}".format(self.dbName))
        except mysql.connector.Error as e:
            self.logger.info(f"Database {self.dbName} does not exist")
            if e.errno == errorcode.ER_BAD_DB_ERROR:
                try:
                    cursor.execute(
                        f"CREATE DATABASE {self.dbName}"
                        " DEFAULT CHARACTER SET 'utf8'"
                    )
                except mysql.connector.Error as err:
                    self.logger.error(f"Failed to create database, {err}")
                    exit(1)
                self.logger.info("Database {self.dbName} created successfully")
                self.conn.database = self.dbName
            else:
                self.logger.error(e)
                exit(1)

        cursor.close()

    def createTables(self):
        cursor = self.conn.cursor()

        for tableName in TABLES:
            tableDescription = TABLES[tableName]
            try:
                self.logger.info(f"Creating table {tableName}")
                cursor.execute(tableDescription)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.info(f"Table {tableName} already exists.")
                else:
                    self.logger.error(err.msg)
            else:
                self.logger.info("OK")

        cursor.close()

    def saveNewFileInfo(self, fileId, filePath,
                        encryptedFileName, owner, publicKey, privateKey):
        # Add entry to tables `owned_files` and `file_details`.
        fileInfo = (fileId, encryptedFileName, owner,
                    filePath, publicKey, privateKey)
        cursor = self.conn.cursor()
        cursor.execute(addOwnedFiles, [fileId])
        cursor.execute(addFileDetails, fileInfo)
        self.conn.commit()
        cursor.close()

    def saveReplicationFileInfo(self, fileId, filePath,
                                encryptedFileName, owner):
        # Add entry to tables `replicated_files` and `file_details`.
        fileInfo = (fileId, encryptedFileName, owner, filePath, "", "")
        cursor = self.conn.cursor()
        cursor.execute(addReplicatedFiles, [fileId])
        cursor.execute(addFileDetails, fileInfo)
        self.conn.commit()
        cursor.close()

    def getFileDetails(self, fileId):
        fileDetails = {}
        cursor = self.conn.cursor()
        cursor.execute(queryFileDetails, [fileId])

        for (fileId, encryptedFileName, owner, filePath, publicKey,
             privateKey) in cursor:
            # There will be only one record in the query response
            fileDetails['file_id'] = fileId
            fileDetails['en_file_name'] = encryptedFileName
            fileDetails['owner'] = owner
            fileDetails['file_path'] = filePath
            fileDetails['public_key'] = publicKey
            fileDetails['private_key'] = privateKey

        cursor.close()
        return fileDetails

    def addOrUpdateNodePublicKey(self, address, hostname, publicKey):
        cursor = self.conn.cursor()
        nodeInfo = (address, hostname, publicKey, hostname, publicKey)
        cursor.execute(addOrUpdateNodeDetails, nodeInfo)
        self.conn.commit()
        cursor.close()

    def getNodePublicKey(self, address):
        publicKey = b""
        cursor = self.conn.cursor()
        cursor.execute(queryNodePublicKey, [address])
        for row in cursor:
            publicKey = row[0]
        cursor.close()
        return publicKey

    def getOwnedFiles(self):
        ownedFiles = []
        cursor = self.conn.cursor()
        cursor.execute(queryAllOwnedFiles)
        for row in cursor:
            ownedFiles.append(row[0])
        cursor.close()
        return ownedFiles

    def getSharedFiles(self):
        sharedFiles = []
        cursor = self.conn.cursor()
        cursor.execute(queryAllSharedFiles)
        for row in cursor:
            sharedFiles.append({
                'file_id': row[0],
                'write': row[1]
            })
        cursor.close()
        return sharedFiles

    def DeleteFileEntry(self, fileId):
        cursor = self.conn.cursor()
        cursor.execute(deleteFromOwnedFiles, [fileId])
        cursor.execute(deleteFromReplicatedFiles, [fileId])
        cursor.execute(deleteFromReplicatedFilePermissions, [fileId])
        cursor.execute(deleteFromFileDetails, [fileId])
        cursor.execute(deleteFileLock, [fileId])
        self.conn.commit()
        cursor.close()

    def addPermissionEntry(self, fileId, writePermission):
        cursor = self.conn.cursor()
        permissionInfo = (fileId, writePermission, writePermission)
        cursor.execute(addOrUpdatePermissionEntryRepl, permissionInfo)
        self.conn.commit()
        cursor.close()

    def updateFileDetails(self, fileId, privateKey, publicKey):
        cursor = self.conn.cursor()
        fileInfo = (publicKey, privateKey, fileId)
        cursor.execute(updateFileInfo, fileInfo)
        self.conn.commit()
        cursor.close()

    def isFileLocked(self, fileId):
        cursor = self.conn.cursor()
        cursor.execute(queryFileLock, [fileId])
        fileLocked = False
        for row in cursor:
            fileLocked = row[0]
        cursor.close()
        return fileLocked

    def getFileLockOwnerIp(self, fileId):
        cursor = self.conn.cursor()
        cursor.execute(queryFileLock, [fileId])
        ipAddress = ""
        for row in cursor:
            ipAddress = row[1]
        cursor.close()
        return ipAddress

    def getFileLock(self, ipAddress, fileId):
        cursor = self.conn.cursor()
        lockInfo = [fileId, 1, ipAddress]
        cursor.execute(createFileLock, lockInfo)
        self.conn.commit()
        cursor.close()

    def releaseFileLock(self, fileId):
        cursor = self.conn.cursor()
        cursor.execute(deleteFileLock, [fileId])
        self.conn.commit()
        cursor.close()

    def addGrantedPermissionEntry(self, fileId, ipAddress, permission):
        cursor = self.conn.cursor()
        permissionInfo = (fileId, ipAddress, permission, permission)
        cursor.execute(addOrUpdatePermissionEntry, permissionInfo)
        self.conn.commit()
        cursor.close()

    def insertRestoreEntry(self, fileId, publicKey, privateKey):
        cursor = self.conn.cursor()
        fileInfo = (fileId, publicKey, privateKey)
        cursor.execute(storeDeletedFileKeys, fileInfo)
        self.conn.commit()
        cursor.close()

    def getDeletedFileKeys(self, fileId):
        cursor = self.conn.cursor()
        cursor.execute(queryDeletedFileKeys, [fileId])
        publicKey, privateKey = None, None
        for resp in cursor:
            publicKey = resp[0]
            privateKey = resp[1]
        cursor.close()
        return publicKey, privateKey
