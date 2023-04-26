import grpc

from concurrent import futures
from distributed_fs.distributed_fs_pb2_grpc import (
    add_DistributedFileSystemServicer_to_server)
from distributed_fs.distributed_fs_service import DistributedFileSystemService
from utils import constants
from utils.misc import getLogger


class Server:
    def __init__(self, ip, port, host):
        self.ip = ip
        self.port = port
        self.host = host
        self.logger = getLogger("server", {"$HOSTNAME": host})

    @property
    def address(self):
        return ":".join((self.ip, self.port))

    def run(self, maxWorkers=10):
        # TODO: Handle this globals better
        constants.setupGlobalConstants(self.address, self.host)
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=maxWorkers))
        add_DistributedFileSystemServicer_to_server(
            DistributedFileSystemService(), server
        )
        server.add_insecure_port(self.address)
        server.start()
        server.wait_for_termination()
