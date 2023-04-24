import base64
import distributed_fs.distributed_fs_pb2 as pb
import grpc
import utils.constants as constants
import utils.file
import utils.encryption

from distributed_fs.distributed_fs_pb2_grpc import DistributedFileSystemServicer


class DistributedFileSystemService(DistributedFileSystemServicer):
    def CreateFile(self, request, context):
        print(request.filename)
        context.set_code(grpc.StatusCode.OK)
        context.set_details('File Created on Server!')

    def UpdateNodePublicKey(self, request, context):
        ip_address = request.address
        hostname = request.hostname
        public_key = base64.b64decode((request.publicKey))
        constants.db_instance.add_or_update_node_public_key(
            ip_address, hostname, public_key)

        context.set_code(grpc.StatusCode.OK)
        return pb.UpdateKeyResponse(status="Success!")

    def DeleteFile(self, request, context):
        file_id = request.fileId
        file_details = constants.db_instance.get_file_details(file_id)

        # @TODO: Check if the request is from the file owner.

        # Delete the file and clear relevant entries from the database.
        utils.file.delete_file(file_details['file_path'])
        constants.db_instance.delete_file_entry(file_id)

        context.set_code(grpc.StatusCode.OK)
        return pb.DeleteResponse(status="Success!")

    def GrantPermisions(self, request, context):
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
        return pb.PermissionResponse(status="Success!")
