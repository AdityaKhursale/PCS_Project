import functools


def useDistributedFileSystemStub(server):
    # pylint: disable=import-outside-toplevel

    import grpc
    from distributed_fs.distributed_fs_pb2_grpc import \
        DistributedFileSystemStub

    def _decorator(func):
        @functools.wraps(func)
        def wrapper(**kwargs):
            with grpc.insecure_channel(
                server, options=(('grpc.enable_http_proxy', 0),)
            ) as channel:
                stub = DistributedFileSystemStub(channel)
                kwargs['stub'] = stub
                return func(**kwargs)
        return wrapper
    return _decorator
