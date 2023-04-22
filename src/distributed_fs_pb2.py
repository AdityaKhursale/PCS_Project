# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: distributed_fs.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x64istributed_fs.proto\"\r\n\x0bReadRequest\"\x0e\n\x0cReadResponse\"\r\n\x0bListRequest\"\x0e\n\x0cListResponse\"\x0f\n\rUpdateRequest\"\x10\n\x0eUpdateResponse\"\x13\n\x11PermissionRequest\"\x14\n\x12PermissionResponse\"\x0f\n\rCreateRequest\"\x10\n\x0e\x43reateResponse\"\x0f\n\rDeleteRequest\"\x10\n\x0e\x44\x65leteResponse2\xbf\x02\n\x15\x44istributedFileSystem\x12)\n\x08ReadFile\x12\x0c.ReadRequest\x1a\r.ReadResponse\"\x00\x12*\n\tListFiles\x12\x0c.ListRequest\x1a\r.ListResponse\"\x00\x12/\n\nUpdateFile\x12\x0e.UpdateRequest\x1a\x0f.UpdateResponse\"\x00\x12<\n\x0fGrantPermisions\x12\x12.PermissionRequest\x1a\x13.PermissionResponse\"\x00\x12/\n\nCreateFile\x12\x0e.CreateRequest\x1a\x0f.CreateResponse\"\x00\x12/\n\nDeleteFile\x12\x0e.DeleteRequest\x1a\x0f.DeleteResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'distributed_fs_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _READREQUEST._serialized_start=24
  _READREQUEST._serialized_end=37
  _READRESPONSE._serialized_start=39
  _READRESPONSE._serialized_end=53
  _LISTREQUEST._serialized_start=55
  _LISTREQUEST._serialized_end=68
  _LISTRESPONSE._serialized_start=70
  _LISTRESPONSE._serialized_end=84
  _UPDATEREQUEST._serialized_start=86
  _UPDATEREQUEST._serialized_end=101
  _UPDATERESPONSE._serialized_start=103
  _UPDATERESPONSE._serialized_end=119
  _PERMISSIONREQUEST._serialized_start=121
  _PERMISSIONREQUEST._serialized_end=140
  _PERMISSIONRESPONSE._serialized_start=142
  _PERMISSIONRESPONSE._serialized_end=162
  _CREATEREQUEST._serialized_start=164
  _CREATEREQUEST._serialized_end=179
  _CREATERESPONSE._serialized_start=181
  _CREATERESPONSE._serialized_end=197
  _DELETEREQUEST._serialized_start=199
  _DELETEREQUEST._serialized_end=214
  _DELETERESPONSE._serialized_start=216
  _DELETERESPONSE._serialized_end=232
  _DISTRIBUTEDFILESYSTEM._serialized_start=235
  _DISTRIBUTEDFILESYSTEM._serialized_end=554
# @@protoc_insertion_point(module_scope)
