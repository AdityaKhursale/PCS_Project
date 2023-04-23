import logging
import grpc

from distributed_fs import distributed_fs_pb2
from distributed_fs import distributed_fs_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = distributed_fs_pb2_grpc.DistributedFileSystemStub(channel)
        stub.ReadFile(distributed_fs_pb2.ReadRequest())


if __name__ == '__main__':
    logging.basicConfig()
    run()
