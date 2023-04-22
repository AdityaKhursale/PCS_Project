from __future__ import print_function

import logging
import random

import grpc
import distributed_fs_pb2
import distributed_fs_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = distributed_fs_pb2_grpc.DistributedFileSystemStub(channel)
        stub.ReadFile(distributed_fs_pb2.ReadRequest())


if __name__ == '__main__':
    logging.basicConfig()
    run()
