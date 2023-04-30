import os

from concurrent import futures

import grpc

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

    @property
    def root(self):
        return os.path.join(constants.ASSETS, self.host)

    @property
    def trashstore(self):
        return os.path.join(self.root, ".trash")

    def run(self, maxWorkers=10):
        # TODO: Handle this globals better
        constants.setupGlobalConstants(self.address, self.host)
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=maxWorkers))
        add_DistributedFileSystemServicer_to_server(
            DistributedFileSystemService(self.root, self.trashstore), server
        )
        server.add_insecure_port(self.address)
        server.start()
        server.wait_for_termination()
