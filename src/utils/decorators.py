import functools


def useDistributedFileSystemStub(server):
    import grpc
    from distributed_fs.distributed_fs_pb2_grpc import \
        DistributedFileSystemStub

    def _decorator(func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            with grpc.insecure_channel(server) as channel:
                stub = DistributedFileSystemStub(channel)
                kwargs['stub'] = stub
                func(**kwargs)
        return wrapper
    return _decorator
