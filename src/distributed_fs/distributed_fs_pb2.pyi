from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

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
    __slots__ = ["fileId"]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    fileId: str
    def __init__(self, fileId: _Optional[str] = ...) -> None: ...


class DeleteResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...


class ListRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class ListResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class PermissionRequest(_message.Message):
    __slots__ = ["fileId", "filePrivateKey", "filePublicKey"]
    FILEID_FIELD_NUMBER: _ClassVar[int]
    FILEPRIVATEKEY_FIELD_NUMBER: _ClassVar[int]
    FILEPUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    fileId: str
    filePrivateKey: str
    filePublicKey: str
    def __init__(self, fileId: _Optional[str] = ..., filePublicKey: _Optional[str]
                 = ..., filePrivateKey: _Optional[str] = ...) -> None: ...


class PermissionResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...


class ReadRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class ReadResponse(_message.Message):
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
    def __init__(self, hostname: _Optional[str] = ..., address: _Optional[str]
                 = ..., publicKey: _Optional[str] = ...) -> None: ...


class UpdateKeyResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...


class UpdateRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class UpdateResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
