import grpc

from distributed_fs.distributed_fs_pb2_grpc import DistributedFileSystemServicer


class DistributedFileSystemService(DistributedFileSystemServicer):
    def CreateFile(self, request, context):
        print(request.filename)
        context.set_code(grpc.StatusCode.OK)
        context.set_details('File Created on Server!')
