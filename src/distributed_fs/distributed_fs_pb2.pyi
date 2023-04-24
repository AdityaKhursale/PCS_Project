from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor


class CreateRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class CreateResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class DeleteRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class DeleteResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class ListRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class ListResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class PermissionRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


class PermissionResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...


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
