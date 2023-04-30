import base64
import distributed_fs.distributed_fs_pb2 as pb
import grpc
import os
import traceback

from distributed_fs.distributed_fs_pb2_grpc import \
    (DistributedFileSystemStub, DistributedFileSystemServicer)
from utils import constants, cryptography
from utils import file_io as fileIO
from utils.misc import getLogger
from utils.network import getNodesExcept


class DistributedFileSystemService(DistributedFileSystemServicer):
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
        file_name = request.filename
        # Use UUID for the file as we will be encrypting file name as well.
        file_id = fileIO.getFileId(file_name)
        file_path = self._getFilePathById(file_id)
        owner = constants.ADDRESS

        private_key, public_key = cryptography.createRsaKeyPair()
        en_file_name = cryptography.encryptData(public_key, file_name)
        en_file_content = cryptography.encryptData(
            public_key, "")

        constants.DB_INSTANCE.saveNewFileInfo(
            file_id, file_path, en_file_name, owner, public_key, private_key)
        fileIO.writeBinaryFile(file_path, en_file_content)

        nodes_in_network = getNodesExcept(constants.ADDRESS)
        for node in nodes_in_network:
            self.logger.info(f"Replicating file '{file_id}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateFile(pb.ReplicateFileRequest(
                    fileId=file_id,
                    fileName=base64.b64encode(en_file_name),
                    owner=constants.ADDRESS,
                    fileContent=base64.b64encode(en_file_content)
                ))

        context.set_code(grpc.StatusCode.OK)
        context.set_details('File Created on Server!')

    def ReplicateFile(self, request, context):
        file_id = request.fileId
        en_file_content = base64.b64decode(request.fileContent)
        en_file_name = base64.b64decode(request.fileName)
        owner = request.owner

        # Store file on filesystem
        self.logger.info(f"Received replication request for: {file_id}")
        file_path = self._getFilePathById(file_id)
        if not fileIO.fileExists(file_path):
            # This is new file, so make entry to database.
            constants.DB_INSTANCE.saveReplicationFileInfo(
                file_id, file_path, en_file_name, owner)

        # Check if the request is from the owner of file
        resp_msg = ""
        file_details = constants.DB_INSTANCE.getFileDetails(file_id)
        if (owner == file_details['owner']):
            self.logger.info("Request authentication successful,"
                             " saving to filesystem!")
            fileIO.writeBinaryFile(file_path, en_file_content)
            resp_msg = "Success!"
        else:
            self.logger.error("Request authentication failed!")
            resp_msg = "Failed!"
        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateFileResponse(status=resp_msg)

    def ListFiles(self, request, context):
        owned_files = constants.DB_INSTANCE.getOwnedFiles()
        shared_files = constants.DB_INSTANCE.getSharedFiles()

        list_response = pb.ListResponse()
        for file_id in owned_files:
            list_response.files.append(self._get_file_name(file_id))

        for file in shared_files:
            list_response.files.append(self._get_file_name(file['file_id']))

        return list_response

    def ReadFile(self, request, context):
        file_id = fileIO.getFileId(request.filename)
        file_details = constants.DB_INSTANCE.getFileDetails(file_id)

        if len(file_details) == 0:
            return pb.ReadResponse(status="File doesn't exist!")

        if len(file_details['private_key']) == 0:
            return pb.ReadResponse(status="Permission denied!")

        encrypted_data = fileIO.readBinaryFile(
            file_details['file_path'])
        decrypted_data = cryptography.decryptData(
            file_details['private_key'], encrypted_data)

        return pb.ReadResponse(filecontent=decrypted_data)

    def CreateNodeKeys(self, request, context):
        _, public_key = cryptography.dumpRsaKeyPair(self.root)
        nodes_in_network = getNodesExcept(constants.ADDRESS)
        for node in nodes_in_network:
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.UpdateNodePublicKey(pb.UpdateKeyRequest(
                    address=constants.ADDRESS,
                    hostname=constants.HOST_NAME,
                    publicKey=public_key
                ))
        context.set_code(grpc.StatusCode.OK)
        return pb.CreateNodeKeyResponse(status="Success!")

    def UpdateNodePublicKey(self, request, context):
        ip_address = request.address
        hostname = request.hostname
        public_key = request.publicKey
        constants.DB_INSTANCE.addOrUpdateNodePublicKey(
            ip_address, hostname, public_key)

        context.set_code(grpc.StatusCode.OK)
        return pb.UpdateKeyResponse(status="Success!")

    def ReplicateDeleteFile(self, request, context):
        file_id = request.fileId
        file_details = constants.DB_INSTANCE.getFileDetails(file_id)

        # Delete the file and clear relevant entries from the database.
        fileName = os.path.basename(file_details['file_path'])
        fileIO.moveFile(file_details['file_path'], os.path.join(
            self.trashstore, fileName))
        constants.DB_INSTANCE.insertRestoreEntry(
            file_id, file_details["public_key"], file_details["private_key"])
        constants.DB_INSTANCE.DeleteFileEntry(file_id)

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateDeleteResponse(status="Success!")

    def DeleteFile(self, request, context):
        file_id = fileIO.getFileId(request.filename)
        file_details = constants.DB_INSTANCE.getFileDetails(file_id)

        if len(file_details) == 0:
            return pb.DeleteResponse(status="File doesn't exist!")

        # Only file owner can issue delete request.
        owned_files = constants.DB_INSTANCE.getOwnedFiles()
        if file_id not in owned_files:
            return pb.DeleteResponse(status="Permission denied!")

        # Delete the file and clear relevant entries from the database.
        fileName = os.path.basename(file_details['file_path'])
        fileIO.moveFile(file_details['file_path'], os.path.join(
            self.trashstore, fileName))
        constants.DB_INSTANCE.insertRestoreEntry(
            file_id, file_details["public_key"], file_details["private_key"])
        constants.DB_INSTANCE.DeleteFileEntry(file_id)

        # Delete the file on other nodes.
        nodes_in_network = getNodesExcept(constants.ADDRESS)
        for node in nodes_in_network:
            self.logger.info(f"\nDeleting file '{file_id}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateDeleteFile(pb.ReplicateDeleteRequest(
                    fileId=file_id
                ))

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateDeleteResponse(status="Success!")

    def ReplicatePermissions(self, request, context):
        file_id = request.fileId
        en_public_key = base64.b64decode(request.filePublicKey)
        en_private_key = base64.b64decode(request.filePrivateKey)
        file_public_key = b""
        file_private_key = b""

        # Decode the received file keys using node's private key.
        nodes_private_key = fileIO.readBinaryFile(
            os.path.join(self.root, "private_key"))
        if len(en_public_key) != 0:
            file_public_key = cryptography.decryptBinaryData(
                nodes_private_key, en_public_key)
        if len(en_private_key) != 0:
            file_private_key = cryptography.decryptBinaryData(
                nodes_private_key, en_private_key)

        # Note the granted permission and file keys.
        is_write_permission = 1 if len(file_public_key) != 0 else 0
        constants.DB_INSTANCE.addPermissionEntry(
            file_id, is_write_permission)
        constants.DB_INSTANCE.updateFileDetails(
            file_id, file_private_key, file_public_key)

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicatePermissionResponse(status="Success!")

    def GrantPermissions(self, request, context):
        file_id = fileIO.getFileId(request.filename)
        ip_addr = request.hostname
        permission = request.permission
        file_details = constants.DB_INSTANCE.getFileDetails(file_id)

        if len(file_details) == 0:
            return pb.PermissionResponse(status="File doesn't exist!")

        # Only file owner can grant permissions.
        owned_files = constants.DB_INSTANCE.getOwnedFiles()
        if file_id not in owned_files:
            return pb.PermissionResponse(status="Permission denied!")

        # Encrypt private key for read access and public key if write acccess
        # is granted. The keys are encrypted using the public key of the node
        # with whom the file is being shared.
        shared_nodes_public_key = constants.DB_INSTANCE.getNodePublicKey(
            ip_addr)
        file_private_key = cryptography.encryptKey(
            shared_nodes_public_key, file_details['private_key'])

        file_public_key = b""
        if permission == "write":
            file_public_key = cryptography.encryptKey(
                shared_nodes_public_key, file_details['public_key'])
        with grpc.insecure_channel(ip_addr) as channel:
            stub = DistributedFileSystemStub(channel)
            stub.ReplicatePermissions(pb.ReplicatePermissionRequest(
                fileId=file_id,
                filePrivateKey=base64.b64encode(file_private_key),
                filePublicKey=base64.b64encode(file_public_key)
            ))

        constants.DB_INSTANCE.addGrantedPermissionEntry(
            file_id, ip_addr, permission)

        context.set_code(grpc.StatusCode.OK)
        return pb.PermissionResponse(status="Success!")

    def GetFileLock(self, request, context):
        file_id = request.fileId
        ip_address = request.address

        lock_granted = self._getFileLock(file_id, ip_address)

        context.set_code(grpc.StatusCode.OK)
        return pb.FileLockResponse(lockGranted=lock_granted)

    def UpdateFile(self, request, context):
        try:
            file_id = fileIO.getFileId(request.filename)
            file_content = request.filecontent
            overwrite = request.overwrite

            file_details = constants.DB_INSTANCE.getFileDetails(
                file_id)
            if len(file_details) == 0:
                return pb.UpdateResponse(status="File doesn't exist!")

            is_file_owner = False
            owned_files = constants.DB_INSTANCE.getOwnedFiles()
            if file_id in owned_files:
                is_file_owner = True

            # Only host with permission can edit the file.
            if not is_file_owner:
                shared = False
                shared_files = constants.DB_INSTANCE.getSharedFiles()
                for file in shared_files:
                    if file['file_id'] == file_id and file['write'] == 1:
                        shared = True
                        break
                if not shared:
                    return pb.UpdateResponse(status="Permission denied!")

            # Get File Lock.
            if is_file_owner:
                if not self._getFileLock(file_id, constants.ADDRESS):
                    return pb.UpdateResponse(status="Concurrent write not permitted!")
            else:
                # If shared file then get the lock from file owner.
                file_lock_response = pb.FileLockResponse()
                with grpc.insecure_channel(file_details['owner']) as channel:
                    stub = DistributedFileSystemStub(channel)
                    file_lock_response = stub.GetFileLock(pb.FileLockRequest(
                        fileId=file_id,
                        address=constants.ADDRESS
                    ))
                if not file_lock_response.lockGranted:
                    return pb.UpdateResponse(status="Concurrent write not permitted!")

            # Encrypt the content.
            en_file_content = b""
            if overwrite:
                en_file_content = cryptography.encryptData(
                    file_details['public_key'], file_content)
            else:
                encrypted_data = fileIO.readBinaryFile(
                    file_details['file_path'])
                decrypted_data = cryptography.decryptData(
                    file_details['private_key'], encrypted_data)
                new_file_content = decrypted_data + file_content
                en_file_content = cryptography.encryptData(
                    file_details['public_key'], new_file_content)
            if is_file_owner:
                # If the current node is file owner then store on local server
                # and send update to other nodes.
                fileIO.writeBinaryFile(
                    file_details['file_path'], en_file_content)

                nodes_in_network = getNodesExcept(
                    constants.ADDRESS)
                for node in nodes_in_network:
                    with grpc.insecure_channel(node) as channel:
                        stub = DistributedFileSystemStub(channel)
                        stub.ReplicateFile(pb.ReplicateFileRequest(
                            fileId=file_id,
                            fileName=base64.b64encode(
                                file_details['en_file_name']),
                            owner=constants.ADDRESS,
                            fileContent=base64.b64encode(en_file_content)
                        ))

                # Drop the file lock.
                constants.DB_INSTANCE.releaseFileLock(file_id)
            else:
                # If the current node is not owner and has right to edit file
                # then, send the udpate request to file owner for replication.
                with grpc.insecure_channel(file_details['owner']) as channel:
                    stub = DistributedFileSystemStub(channel)
                    stub.ReplicateUpdateFile(pb.ReplicateUpdateRequest(
                        fileId=file_id,
                        fileContent=base64.b64encode(en_file_content),
                        address=constants.ADDRESS
                    ))
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(e)

        context.set_code(grpc.StatusCode.OK)
        return pb.UpdateResponse(status="Success!")

    def ReplicateUpdateFile(self, request, context):
        file_id = request.fileId
        en_file_content = base64.b64decode(request.fileContent)
        request_ip_address = request.address

        file_lock_owner_ip = constants.DB_INSTANCE.getFileLockOwnerIp(
            file_id)

        if file_lock_owner_ip != request_ip_address:
            return pb.ReplicateUpdateResponse(status="Permission Denied!")

        # Drop the file lock.
        constants.DB_INSTANCE.releaseFileLock(file_id)

        file_details = constants.DB_INSTANCE.getFileDetails(file_id)
        fileIO.writeBinaryFile(file_details['file_path'], en_file_content)

        nodes_in_network = getNodesExcept(constants.ADDRESS)
        for node in nodes_in_network:
            self.logger.info(f"Replicating file '{file_id}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateFile(pb.ReplicateFileRequest(
                    fileId=file_id,
                    fileName=base64.b64encode(file_details['en_file_name']),
                    owner=constants.ADDRESS,
                    fileContent=base64.b64encode(en_file_content)
                ))
        return pb.ReplicateUpdateResponse(status="Success!")

    def RestoreFile(self, request, context):
        try:
            file_name = request.filename
            # Use UUID for the file as we will be encrypting file name as well.
            file_id = fileIO.getFileId(file_name)
            file_path = self._getFilePathById(file_id)
            owner = constants.ADDRESS

            public_key, private_key = constants.DB_INSTANCE.getDeletedFileKeys(
                file_id)
            en_file_name = cryptography.encryptData(public_key, file_name)
            encryptedFileContent = fileIO.readBinaryFile(
                os.path.join(self.trashstore, os.path.basename(file_path)))
            constants.DB_INSTANCE.saveNewFileInfo(
                file_id, file_path, en_file_name, owner, public_key, private_key)
            trashedFilePath = os.path.join(self.trashstore,
                                           os.path.basename(file_path))
            fileIO.moveFile(trashedFilePath, file_path)

            nodes_in_network = getNodesExcept(constants.ADDRESS)
            for node in nodes_in_network:
                self.logger.info(
                    f"Replicating file '{file_id}' on server: {node}")
                with grpc.insecure_channel(node) as channel:
                    stub = DistributedFileSystemStub(channel)
                    stub.ReplicateRestore(
                        pb.ReplicateRestoreRequest(filePath=trashedFilePath))
                    stub.ReplicateFile(pb.ReplicateFileRequest(
                        fileId=file_id,
                        fileName=base64.b64encode(en_file_name),
                        owner=constants.ADDRESS,
                        fileContent=base64.b64encode(encryptedFileContent)
                    ))
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(e)

        context.set_code(grpc.StatusCode.OK)
        context.set_details('File Restored on Server!')
        return pb.RestoreResponse()

    def ReplicateRestore(self, request, context):
        fileIO.deleteFile(os.path.join(self.trashstore,
                                       os.path.basename(request.filePath)))
        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateRestoreResponse()

    def _get_file_name(self, file_id):
        file_details = constants.DB_INSTANCE.getFileDetails(file_id)
        return cryptography.decryptData(file_details['private_key'],
                                        file_details['en_file_name'])

    def _getFileLock(self, file_id, ip_address):
        lock_granted = False
        if constants.DB_INSTANCE.isFileLocked(file_id):
            lock_granted = False
        else:
            constants.DB_INSTANCE.getFileLock(ip_address, file_id)
            lock_granted = True
        return lock_granted

    def _getFilePathById(self, fileId):
        return os.path.join(self.root, fileId)
