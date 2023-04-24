import argparse
import base64
import distributed_fs.distributed_fs_pb2 as pb
import grpc
import utils.constants as constants
import utils.file


from concurrent import futures
from distributed_fs.distributed_fs_pb2_grpc import (
    add_DistributedFileSystemServicer_to_server, DistributedFileSystemServicer)
from distributed_fs.distributed_fs_service import DistributedFileSystemService


class DfsServer(DistributedFileSystemServicer):

    def UpdateNodePublicKey(self, request, context):
        ip_address = request.address
        hostname = request.hostname
        public_key = base64.b64decode((request.publicKey))
        constants.db_instance.add_or_update_node_public_key(
            ip_address, hostname, public_key)

        return pb.UpdateKeyResponse(status="Success!")

    def DeleteFile(self, request, context):
        file_id = request.fileId
        file_details = constants.db_instance.get_file_details(file_id)

        # @TODO: Check if the request is from the file owner.

        # Delete the file and clear relevant entries from the database.
        utils.file.delete_file(file_details['file_path'])
        constants.db_instance.delete_file_entry(file_id)

        return pb.DeleteResponse(status="Success!")


def serve(ip_address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DistributedFileSystemServicer_to_server(
        DistributedFileSystemService(), server
    )
    server.add_insecure_port(ip_address)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", help="IP Address", default="[::]:50051")
    parser.add_argument("--hostname", help="Host name", default="localhost")
    args = parser.parse_args()

    # Set up the enviornment variables.
    # constants.init_env(args.address, args.hostname)

    serve(args.address)
