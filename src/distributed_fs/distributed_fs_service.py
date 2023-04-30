import base64
import os
import traceback
from types import FunctionType
from functools import wraps

import grpc

import distributed_fs.distributed_fs_pb2 as pb
from distributed_fs.distributed_fs_pb2_grpc import \
    (DistributedFileSystemStub, DistributedFileSystemServicer)
from utils import constants, cryptography
from utils import file_io as fileIO
from utils.misc import getLogger
from utils.network import getNodesExcept


def wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            args[0].logger.error(traceback.format_exc())
            return pb.DummyErrorResponse()
    return wrapped


class SilentAndLogException(type):
    def __new__(cls, classname, bases, classDict):
        newClassDict = {}

        for attrName, attr in classDict.items():
            if isinstance(attr, FunctionType):
                attr = wrapper(attr)

            newClassDict[attrName] = attr

        return type.__new__(cls, classname, bases, newClassDict)


class DistributedFileSystemService(DistributedFileSystemServicer, metaclass=SilentAndLogException):
    def __init__(self, root, trashstore):
        super().__init__()
        self.root = root
        self.trashstore = trashstore
        self.logger = getLogger(
            "distributed_fs", {"$HOSTNAME": constants.HOST_NAME})
        self.setupDirectories()

    def setupDirectories(self):
        fileIO.createDir(self.root)
        fileIO.createDir(self.trashstore)

    def CreateFile(self, request, context):
        fileName = request.filename
        # Use UUID for the file as we will be encrypting file name as well.
        fileId = fileIO.getFileId(fileName)
        filePath = self._getFilePathById(fileId)
        owner = constants.ADDRESS

        privateKey, publicKey = cryptography.createRsaKeyPair()
        encryptedFileName = cryptography.encryptData(publicKey, fileName)
        encryptedFileContent = cryptography.encryptData(
            publicKey, "")

        constants.DB_INSTANCE.saveNewFileInfo(
            fileId, filePath, encryptedFileName, owner, publicKey, privateKey)
        fileIO.writeBinaryFile(filePath, encryptedFileContent)

        nodes = getNodesExcept(constants.ADDRESS)
        for node in nodes:
            self.logger.info(f"Replicating file '{fileId}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateFile(pb.ReplicateFileRequest(
                    fileId=fileId,
                    fileName=base64.b64encode(encryptedFileName),
                    owner=owner,
                    fileContent=base64.b64encode(encryptedFileContent)
                ))

        context.set_code(grpc.StatusCode.OK)
        context.set_details('File Created on Server!')

    def ReplicateFile(self, request, context):
        fileId = request.fileId
        encryptedFileContent = base64.b64decode(request.fileContent)
        encryptedFileName = base64.b64decode(request.fileName)
        owner = request.owner

        # Store file on filesystem
        self.logger.info(f"Received replication request for: {fileId}")
        filePath = self._getFilePathById(fileId)
        if not fileIO.fileExists(filePath):
            # This is new file, so make entry to database.
            constants.DB_INSTANCE.saveReplicationFileInfo(
                fileId, filePath, encryptedFileName, owner)

        # Check if the request is from the owner of file
        resp = ""
        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)
        if (owner == fileDetails['owner']):
            self.logger.info("Request authentication successful,"
                             " saving to filesystem!")
            fileIO.writeBinaryFile(filePath, encryptedFileContent)
            resp = "Success!"
        else:
            self.logger.error("Request authentication failed!")
            resp = "Failed!"
        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateFileResponse(status=resp)

    def ListFiles(self, request, context):
        ownedFiles = constants.DB_INSTANCE.getOwnedFiles()
        sharedFiles = constants.DB_INSTANCE.getSharedFiles()

        listResponse = pb.ListResponse()
        for fileId in ownedFiles:
            listResponse.files.append(self._get_file_name(fileId))

        for f in sharedFiles:
            listResponse.files.append(self._get_file_name(f['file_id']))

        return listResponse

    def ReadFile(self, request, context):
        fileId = fileIO.getFileId(request.filename)
        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)

        if len(fileDetails) == 0:
            return pb.ReadResponse(status="File doesn't exist!")

        if len(fileDetails['private_key']) == 0:
            return pb.ReadResponse(status="Permission denied!")

        encryptedData = fileIO.readBinaryFile(
            fileDetails['file_path'])
        decryptedData = cryptography.decryptData(
            fileDetails['private_key'], encryptedData)

        return pb.ReadResponse(filecontent=decryptedData)

    def CreateNodeKeys(self, request, context):
        _, publicKey = cryptography.dumpRsaKeyPair(self.root)
        nodes = getNodesExcept(constants.ADDRESS)
        for node in nodes:
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.UpdateNodePublicKey(pb.UpdateKeyRequest(
                    address=constants.ADDRESS,
                    hostname=constants.HOST_NAME,
                    publicKey=publicKey
                ))
        context.set_code(grpc.StatusCode.OK)
        return pb.CreateNodeKeyResponse(status="Success!")

    def UpdateNodePublicKey(self, request, context):
        ipAddress = request.address
        hostname = request.hostname
        publicKey = request.publicKey
        constants.DB_INSTANCE.addOrUpdateNodePublicKey(
            ipAddress, hostname, publicKey)

        context.set_code(grpc.StatusCode.OK)
        return pb.UpdateKeyResponse(status="Success!")

    def ReplicateDeleteFile(self, request, context):
        fileId = request.fileId
        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)

        # Delete the file and clear relevant entries from the database.
        fileName = os.path.basename(fileDetails['file_path'])
        fileIO.moveFile(fileDetails['file_path'], os.path.join(
            self.trashstore, fileName))
        constants.DB_INSTANCE.insertRestoreEntry(
            fileId, fileDetails["public_key"], fileDetails["private_key"])
        constants.DB_INSTANCE.DeleteFileEntry(fileId)

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateDeleteResponse(status="Success!")

    def DeleteFile(self, request, context):
        fileId = fileIO.getFileId(request.filename)
        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)

        if len(fileDetails) == 0:
            return pb.DeleteResponse(status="File doesn't exist!")

        # Only file owner can issue delete request.
        ownedFiles = constants.DB_INSTANCE.getOwnedFiles()
        if fileId not in ownedFiles:
            return pb.DeleteResponse(status="Permission denied!")

        # Delete the file and clear relevant entries from the database.
        fileName = os.path.basename(fileDetails['file_path'])
        fileIO.moveFile(fileDetails['file_path'], os.path.join(
            self.trashstore, fileName))
        constants.DB_INSTANCE.insertRestoreEntry(
            fileId, fileDetails["public_key"], fileDetails["private_key"])
        constants.DB_INSTANCE.DeleteFileEntry(fileId)

        # Delete the file on other nodes.
        nodes = getNodesExcept(constants.ADDRESS)
        for node in nodes:
            self.logger.info(f"\nDeleting file '{fileId}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateDeleteFile(pb.ReplicateDeleteRequest(
                    fileId=fileId
                ))

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateDeleteResponse(status="Success!")

    def ReplicatePermissions(self, request, context):
        fileId = request.fileId
        encryptedPublicKey = base64.b64decode(request.filePublicKey)
        encryptedPrivateKey = base64.b64decode(request.filePrivateKey)
        filePublicKey = b""
        filePrivateKey = b""

        # Decode the received file keys using node's private key.
        nodesPrivateKey = fileIO.readBinaryFile(
            os.path.join(self.root, "private_key"))
        if len(encryptedPublicKey) != 0:
            filePublicKey = cryptography.decryptBinaryData(
                nodesPrivateKey, encryptedPublicKey)
        if len(encryptedPrivateKey) != 0:
            filePrivateKey = cryptography.decryptBinaryData(
                nodesPrivateKey, encryptedPrivateKey)

        # Note the granted permission and file keys.
        writePermission = 1 if len(filePublicKey) != 0 else 0
        constants.DB_INSTANCE.addPermissionEntry(
            fileId, writePermission)
        constants.DB_INSTANCE.updateFileDetails(
            fileId, filePrivateKey, filePublicKey)

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicatePermissionResponse(status="Success!")

    def GrantPermissions(self, request, context):
        fileId = fileIO.getFileId(request.filename)
        ipAddr = constants.HOST_ADDRESS_BY_NAME[request.hostname]
        permission = request.permission
        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)

        if len(fileDetails) == 0:
            return pb.PermissionResponse(status="File doesn't exist!")

        # Only file owner can grant permissions.
        ownedFiles = constants.DB_INSTANCE.getOwnedFiles()
        if fileId not in ownedFiles:
            return pb.PermissionResponse(status="Permission denied!")

        # Encrypt private key for read access and public key if write acccess
        # is granted. The keys are encrypted using the public key of the node
        # with whom the file is being shared.
        sharedNodesPublicKey = constants.DB_INSTANCE.getNodePublicKey(
            ipAddr)
        filePrivateKey = cryptography.encryptKey(
            sharedNodesPublicKey, fileDetails['private_key'])

        filePublicKey = b""
        if permission == "write":
            filePublicKey = cryptography.encryptKey(
                sharedNodesPublicKey, fileDetails['public_key'])
        with grpc.insecure_channel(ipAddr) as channel:
            stub = DistributedFileSystemStub(channel)
            stub.ReplicatePermissions(pb.ReplicatePermissionRequest(
                fileId=fileId,
                filePrivateKey=base64.b64encode(filePrivateKey),
                filePublicKey=base64.b64encode(filePublicKey)
            ))

        constants.DB_INSTANCE.addGrantedPermissionEntry(
            fileId, ipAddr, permission)

        context.set_code(grpc.StatusCode.OK)
        return pb.PermissionResponse(status="Success!")

    def GetFileLock(self, request, context):
        fileId = request.fileId
        ipAddress = request.address

        lockGranted = self._getFileLock(fileId, ipAddress)

        context.set_code(grpc.StatusCode.OK)
        return pb.FileLockResponse(lockGranted=lockGranted)

    def UpdateFile(self, request, context):
        fileId = fileIO.getFileId(request.filename)
        fileContent = request.filecontent
        overwrite = request.overwrite

        fileDetails = constants.DB_INSTANCE.getFileDetails(
            fileId)
        if len(fileDetails) == 0:
            return pb.UpdateResponse(status="File doesn't exist!")

        isFileOwner = False
        ownedFiles = constants.DB_INSTANCE.getOwnedFiles()
        if fileId in ownedFiles:
            isFileOwner = True

        # Only host with permission can edit the file.
        if not isFileOwner:
            shared = False
            sharedFiles = constants.DB_INSTANCE.getSharedFiles()
            for f in sharedFiles:
                if f['file_id'] == fileId and f['write'] == 1:
                    shared = True
                    break
            if not shared:
                return pb.UpdateResponse(status="Permission denied!")

        # Get File Lock.
        if isFileOwner:
            if not self._getFileLock(fileId, constants.ADDRESS):
                return pb.UpdateResponse(status="Concurrent write not permitted!")
        else:
            # If shared file then get the lock from file owner.
            fileLockResponse = pb.FileLockResponse()
            with grpc.insecure_channel(fileDetails['owner']) as channel:
                stub = DistributedFileSystemStub(channel)
                fileLockResponse = stub.GetFileLock(pb.FileLockRequest(
                    fileId=fileId,
                    address=constants.ADDRESS
                ))
            if not fileLockResponse.lockGranted:
                return pb.UpdateResponse(status="Concurrent write not permitted!")

        # Encrypt the content.
        encryptedFileContent = b""
        if overwrite:
            encryptedFileContent = cryptography.encryptData(
                fileDetails['public_key'], fileContent)
        else:
            encryptedData = fileIO.readBinaryFile(
                fileDetails['file_path'])
            decryptedData = cryptography.decryptData(
                fileDetails['private_key'], encryptedData)
            newFileContent = decryptedData + fileContent
            encryptedFileContent = cryptography.encryptData(
                fileDetails['public_key'], newFileContent)
        if isFileOwner:
            # If the current node is file owner then store on local server
            # and send update to other nodes.
            fileIO.writeBinaryFile(
                fileDetails['file_path'], encryptedFileContent)

            nodes = getNodesExcept(
                constants.ADDRESS)
            for node in nodes:
                with grpc.insecure_channel(node) as channel:
                    stub = DistributedFileSystemStub(channel)
                    stub.ReplicateFile(pb.ReplicateFileRequest(
                        fileId=fileId,
                        fileName=base64.b64encode(
                            fileDetails['en_file_name']),
                        owner=constants.ADDRESS,
                        fileContent=base64.b64encode(encryptedFileContent)
                    ))

            # Drop the file lock.
            constants.DB_INSTANCE.releaseFileLock(fileId)
        else:
            # If the current node is not owner and has right to edit file
            # then, send the udpate request to file owner for replication.
            with grpc.insecure_channel(fileDetails['owner']) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateUpdateFile(pb.ReplicateUpdateRequest(
                    fileId=fileId,
                    fileContent=base64.b64encode(encryptedFileContent),
                    address=constants.ADDRESS
                ))

        context.set_code(grpc.StatusCode.OK)
        return pb.UpdateResponse(status="Success!")

    def ReplicateUpdateFile(self, request, context):
        fileId = request.fileId
        encryptedFileContent = base64.b64decode(request.fileContent)
        requestIpAddress = request.address

        fileLockOwnerIp = constants.DB_INSTANCE.getFileLockOwnerIp(
            fileId)

        if fileLockOwnerIp != requestIpAddress:
            return pb.ReplicateUpdateResponse(status="Permission Denied!")

        # Drop the file lock.
        constants.DB_INSTANCE.releaseFileLock(fileId)

        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)
        fileIO.writeBinaryFile(fileDetails['file_path'], encryptedFileContent)

        nodes = getNodesExcept(constants.ADDRESS)
        for node in nodes:
            self.logger.info(f"Replicating file '{fileId}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateFile(pb.ReplicateFileRequest(
                    fileId=fileId,
                    fileName=base64.b64encode(fileDetails['en_file_name']),
                    owner=constants.ADDRESS,
                    fileContent=base64.b64encode(encryptedFileContent)
                ))
        return pb.ReplicateUpdateResponse(status="Success!")

    def RestoreFile(self, request, context):
        fileName = request.filename
        # Use UUID for the file as we will be encrypting file name as well.
        fileId = fileIO.getFileId(fileName)
        filePath = self._getFilePathById(fileId)
        owner = constants.ADDRESS

        publicKey, privateKey = constants.DB_INSTANCE.getDeletedFileKeys(
            fileId)
        encryptedFileName = cryptography.encryptData(publicKey, fileName)
        encryptedFileContent = fileIO.readBinaryFile(
            os.path.join(self.trashstore, os.path.basename(filePath)))
        constants.DB_INSTANCE.saveNewFileInfo(
            fileId, filePath, encryptedFileName, owner, publicKey, privateKey)
        trashedFilePath = os.path.join(self.trashstore,
                                       os.path.basename(filePath))
        fileIO.moveFile(trashedFilePath, filePath)

        nodes = getNodesExcept(constants.ADDRESS)
        for node in nodes:
            self.logger.info(
                f"Replicating file '{fileId}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateRestore(
                    pb.ReplicateRestoreRequest(filePath=trashedFilePath))
                stub.ReplicateFile(pb.ReplicateFileRequest(
                    fileId=fileId,
                    fileName=base64.b64encode(encryptedFileName),
                    owner=constants.ADDRESS,
                    fileContent=base64.b64encode(encryptedFileContent)
                ))

        context.set_code(grpc.StatusCode.OK)
        context.set_details('File Restored on Server!')
        return pb.RestoreResponse()

    def ReplicateRestore(self, request, context):
        fileIO.deleteFile(os.path.join(self.trashstore,
                                       os.path.basename(request.filePath)))
        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateRestoreResponse()

    def _get_file_name(self, fileId):
        fileDetails = constants.DB_INSTANCE.getFileDetails(fileId)
        return cryptography.decryptData(fileDetails['private_key'],
                                        fileDetails['en_file_name'])

    def _getFileLock(self, fileId, ipAddress):
        lockGranted = False
        if constants.DB_INSTANCE.isFileLocked(fileId):
            lockGranted = False
        else:
            constants.DB_INSTANCE.getFileLock(ipAddress, fileId)
            lockGranted = True
        return lockGranted

    def _getFilePathById(self, fileId):
        return os.path.join(self.root, fileId)
