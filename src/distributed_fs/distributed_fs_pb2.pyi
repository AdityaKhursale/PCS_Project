from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateRequest(_message.Message):
    __slots__ = ["filename"]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    filename: str
    def __init__(self, filename: _Optional[str] = ...) -> None: ...

class CreateResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ["filename"]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    filename: str
    def __init__(self, filename: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class FileLockRequest(_message.Message):
    __slots__ = ["fileId"]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    fileId: str
    def __init__(self, fileId: _Optional[str] = ...) -> None: ...

class FileLockResponse(_message.Message):
    __slots__ = ["lockGranted"]
    LOCKGRANTED_FIELD_NUMBER: _ClassVar[int]
    lockGranted: bool
    def __init__(self, lockGranted: bool = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ["files"]
    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, files: _Optional[_Iterable[str]] = ...) -> None: ...

class PermissionRequest(_message.Message):
    __slots__ = ["filename", "hostname", "permission"]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    filename: str
    hostname: str
    permission: str
    def __init__(self, filename: _Optional[str] = ..., hostname: _Optional[str] = ..., permission: _Optional[str] = ...) -> None: ...

class PermissionResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ["filename"]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    filename: str
    def __init__(self, filename: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ["filecontent"]
    FILECONTENT_FIELD_NUMBER: _ClassVar[int]
    filecontent: str
    def __init__(self, filecontent: _Optional[str] = ...) -> None: ...

class ReplicateDeleteRequest(_message.Message):
    __slots__ = ["fileId"]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    fileId: str
    def __init__(self, fileId: _Optional[str] = ...) -> None: ...

class ReplicateDeleteResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ReplicateFileRequest(_message.Message):
    __slots__ = ["fileContent", "fileId", "fileName", "owner"]
    FILECONTENT_FIELD_NUMBER: _ClassVar[int]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    fileContent: str
    fileId: str
    fileName: str
    owner: str
    def __init__(self, fileId: _Optional[str] = ..., fileName: _Optional[str] = ..., owner: _Optional[str] = ..., fileContent: _Optional[str] = ...) -> None: ...

class ReplicateFileResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ReplicatePermissionRequest(_message.Message):
    __slots__ = ["fileId", "filePrivateKey", "filePublicKey"]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    FILEPRIVATEKEY_FIELD_NUMBER: _ClassVar[int]
    FILEPUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    fileId: str
    filePrivateKey: str
    filePublicKey: str
    def __init__(self, fileId: _Optional[str] = ..., filePublicKey: _Optional[str] = ..., filePrivateKey: _Optional[str] = ...) -> None: ...

class ReplicatePermissionResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class RestoreRequest(_message.Message):
    __slots__ = ["filename"]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    filename: str
    def __init__(self, filename: _Optional[str] = ...) -> None: ...

class RestoreResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UpdateKeyRequest(_message.Message):
    __slots__ = ["address", "hostname", "publicKey"]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    address: str
    hostname: str
    publicKey: str
    def __init__(self, hostname: _Optional[str] = ..., address: _Optional[str] = ..., publicKey: _Optional[str] = ...) -> None: ...

class UpdateKeyResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ["filecontent", "filename", "overwrite"]
    FILECONTENT_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    filecontent: str
    filename: str
    overwrite: bool
    def __init__(self, filename: _Optional[str] = ..., filecontent: _Optional[str] = ..., overwrite: bool = ...) -> None: ...

class UpdateResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
