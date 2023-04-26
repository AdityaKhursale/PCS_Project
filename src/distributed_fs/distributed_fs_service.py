import base64
import distributed_fs.distributed_fs_pb2 as pb
import grpc
import utils.constants as constants
import utils.file
import utils.encryption
import utils.network

from distributed_fs.distributed_fs_pb2_grpc import DistributedFileSystemStub

from distributed_fs.distributed_fs_pb2_grpc import DistributedFileSystemServicer


class DistributedFileSystemService(DistributedFileSystemServicer):
    def CreateFile(self, request, context):
        file_name = request.filename
        # Use UUID for the file as we will be encrypting file name as well.
        file_id = utils.file.generate_file_id(file_name)
        file_path = utils.file.form_file_path(file_id)
        owner = utils.constants.ip_addr

        private_key, public_key = utils.encryption.create_rsa_key_pair()
        en_file_name = utils.encryption.encrypt_data(public_key, file_name)
        en_file_content = utils.encryption.encrypt_data(
            public_key, "")

        utils.constants.db_instance.save_new_file_info(
            file_id, file_path, en_file_name, owner, public_key, private_key)
        utils.file.store_file_to_fs(file_path, en_file_content)

        nodes_in_network = utils.network.getNodesExcept(constants.ip_addr)
        for node in nodes_in_network:
            print(f"\nReplicating file '{file_id}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateFile(pb.ReplicateFileRequest(
                    fileId=file_id,
                    fileName=base64.b64encode(en_file_name),
                    owner=constants.ip_addr,
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
        print(f"\nReceived replication request for: {file_id}")
        file_path = utils.file.form_file_path(file_id)
        if not utils.file.is_file_exist(file_path):
            # This is new file, so make entry to database.
            utils.constants.db_instance.save_replication_file_info(
                file_id, file_path, en_file_name, owner)

        # Check if the request is from the owner of file
        resp_msg = ""
        file_details = constants.db_instance.get_file_details(file_id)
        if (owner == file_details['owner']):
            print("\nRequest authentication successful, saving to filesystem!")
            utils.file.store_file_to_fs(file_path, en_file_content)
            resp_msg = "Success!"
        else:
            print("\nRequest authentication failed!")
            resp_msg = "Failed!"
        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateFileResponse(status=resp_msg)

    def ListFiles(self, request, context):
        owned_files = constants.db_instance.get_owned_files()
        shared_files = constants.db_instance.get_shared_files()

        list_response = pb.ListResponse()
        for file_id in owned_files:
            list_response.files.append(self._get_file_name(file_id))

        for file in shared_files:
            list_response.files.append(self._get_file_name(file['file_id']))

        return list_response

    def ReadFile(self, request, context):
        file_id = utils.file.generate_file_id(request.filename)
        file_details = utils.constants.db_instance.get_file_details(file_id)

        if len(file_details) == 0:
            return pb.ReadResponse(status="File doesn't exist!")

        owned_files = constants.db_instance.get_owned_files()
        if file_id not in owned_files and len(file_details['private_key']) == 0:
            return pb.ReadResponse(status="Permission denied!")

        encrypted_data = utils.file.read_file(file_details['file_path'])
        decrypted_data = utils.encryption.decrypt_data(
            file_details['private_key'], encrypted_data)

        return pb.ReadResponse(filecontent=decrypted_data)

    def UpdateNodePublicKey(self, request, context):
        ip_address = request.address
        hostname = request.hostname
        public_key = base64.b64decode((request.publicKey))
        constants.db_instance.add_or_update_node_public_key(
            ip_address, hostname, public_key)

        context.set_code(grpc.StatusCode.OK)
        return pb.UpdateKeyResponse(status="Success!")

    def ReplicateDeleteFile(self, request, context):
        file_id = request.fileId
        file_details = constants.db_instance.get_file_details(file_id)

        # context.peer() outputs as 'ipv4:127.0.0.1:47260', so strip it.
        remote_ip_addr = context.peer()[len("ipv4") + 1:]
        if remote_ip_addr != file_details['owner']:
            return pb.ReplicateDeleteResponse(status="Failed!")

        # Delete the file and clear relevant entries from the database.
        utils.file.delete_file(file_details['file_path'])
        constants.db_instance.delete_file_entry(file_id)

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateDeleteResponse(status="Success!")

    def DeleteFile(self, request, context):
        file_id = utils.file.generate_file_id(request.filename)
        file_details = utils.constants.db_instance.get_file_details(file_id)

        if len(file_details) == 0:
            return pb.DeleteResponse(status="File doesn't exist!")

        # Only file owner can issue delete request.
        owned_files = constants.db_instance.get_owned_files()
        if file_id not in owned_files:
            return pb.DeleteResponse(status="Permission denied!")

        # Delete the file and clear relevant entries from the database.
        utils.file.delete_file(file_details['file_path'])
        constants.db_instance.delete_file_entry(file_id)

        # Delete the file on other nodes.
        nodes_in_network = utils.network.getNodesExcept(constants.ip_addr)
        for node in nodes_in_network:
            print(f"\nDeleting file '{file_id}' on server: {node}")
            with grpc.insecure_channel(node) as channel:
                stub = DistributedFileSystemStub(channel)
                stub.ReplicateDeleteFile(pb.ReplicateDeleteRequest(
                    fileId=file_id
                ))

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicateDeleteResponse(status="Success!")

    def ReplicatePermissions(self, request, context):
        file_id = request.fileId
        en_public_key = base64.b64decode((request.filePublicKey))
        en_private_key = base64.b64decode((request.filePrivateKey))
        file_public_key = b""
        file_private_key = b""

        # Decode the received file keys using node's private key.
        nodes_private_key = utils.encryption.get_node_private_key
        if len(en_public_key) != 0:
            file_public_key = utils.encryption.decrypt_data_binary(
                nodes_private_key, en_public_key)
        if len(en_private_key) != 0:
            file_private_key = utils.encryption.decrypt_data_binary(
                nodes_private_key, en_private_key)

        # Note the granted permission and file keys.
        is_write_permission = 1 if len(file_private_key) != 0 else 0
        constants.db_instance.add_permission_entry(
            file_id, is_write_permission)
        constants.update_file_details(
            file_id, file_private_key, file_public_key)

        context.set_code(grpc.StatusCode.OK)
        return pb.ReplicatePermissionResponse(status="Success!")

    def GrantPermisions(self, request, context):
        file_id = utils.file.generate_file_id(request.filename)
        ip_addr = request.hostname
        permission = request.permission

        file_details = utils.constants.db_instance.get_file_details(file_id)

        if len(file_details) == 0:
            return pb.PermissionResponse(status="File doesn't exist!")

        # Only file owner can grant permissions.
        owned_files = constants.db_instance.get_owned_files()
        if file_id not in owned_files:
            return pb.PermissionResponse(status="Permission denied!")

        repl_permission = pb.ReplicatePermissionRequest()
        repl_permission.fileId = file_id
        repl_permission.filePrivateKey = base64.b64encode(
            file_details['private_key'])

        if permission == "write":
            repl_permission.filePublicKey = base64.b64encode(
                file_details['public_key'])

        with grpc.insecure_channel(ip_addr) as channel:
            stub = DistributedFileSystemStub(channel)
            stub.ReplicatePermissions(repl_permission)

        constants.db_instance.add_granted_permission_entry(
            file_id, ip_addr, permission)

        context.set_code(grpc.StatusCode.OK)
        return pb.PermissionResponse(status="Success!")

    def GetFileLock(self, request, context):
        file_id = request.fileId

        lock_granted = False
        if constants.db_instance.is_file_locked(file_id):
            lock_granted = False
        else:
            constants.db_instance.get_file_lock(file_id)
            lock_granted = True

        context.set_code(grpc.StatusCode.OK)
        return pb.FileLockResponse(lockGranted=lock_granted)

    def _get_file_name(self, file_id):
        file_details = constants.db_instance.get_file_details(file_id)
        return utils.encryption.decrypt_data(file_details['private_key'],
                                             file_details['en_file_name'])
