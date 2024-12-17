from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterServiceMes(_message.Message):
    __slots__ = ("service_address", "service_port")
    SERVICE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_PORT_FIELD_NUMBER: _ClassVar[int]
    service_address: str
    service_port: int
    def __init__(
        self, service_address: _Optional[str] = ..., service_port: _Optional[int] = ...
    ) -> None: ...
