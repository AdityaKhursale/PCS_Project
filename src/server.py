import argparse
import base64
import distributed_fs.distributed_fs_pb2 as pb
import grpc
import utils.constants as constants


from concurrent import futures
from distributed_fs.distributed_fs_pb2_grpc import (
    add_DistributedFileSystemServicer_to_server, DistributedFileSystemServicer)


class DfsServer(DistributedFileSystemServicer):

    def UpdateNodePublicKey(self, request, context):
        ip_address = request.address
        hostname = request.hostname
        public_key = base64.b64decode((request.publicKey))
        constants.db_instance.add_or_update_node_public_key(
            ip_address, hostname, public_key)

        return pb.UpdateKeyResponse(status="Success!")


def serve(ip_address):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DistributedFileSystemServicer_to_server(
        DistributedFileSystemServicer(), server
    )
    server.add_insecure_port(ip_address)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", help="IP Address")
    parser.add_argument("--hostname", help="Host name")
    args = parser.parse_args()

    # Set up the enviornment variables.
    constants.init_env(args.address, args.hostname)

    serve(args.address)
