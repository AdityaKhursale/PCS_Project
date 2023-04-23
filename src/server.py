import grpc

from concurrent import futures
from distributed_fs.distributed_fs_pb2_grpc import (
    add_DistributedFileSystemServicer_to_server, DistributedFileSystemServicer)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DistributedFileSystemServicer_to_server(
        DistributedFileSystemServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
