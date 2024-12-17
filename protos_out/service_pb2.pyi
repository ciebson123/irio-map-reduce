from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MapTask(_message.Message):
    __slots__ = ("file_path", "num_partitions")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    NUM_PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    num_partitions: int
    def __init__(
        self, file_path: _Optional[str] = ..., num_partitions: _Optional[int] = ...
    ) -> None: ...

class MapResponse(_message.Message):
    __slots__ = ("partition_paths",)
    PARTITION_PATHS_FIELD_NUMBER: _ClassVar[int]
    partition_paths: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, partition_paths: _Optional[_Iterable[str]] = ...) -> None: ...

class ReduceTask(_message.Message):
    __slots__ = ("num_mappers", "partition_paths", "output_path")
    NUM_MAPPERS_FIELD_NUMBER: _ClassVar[int]
    PARTITION_PATHS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_PATH_FIELD_NUMBER: _ClassVar[int]
    num_mappers: int
    partition_paths: _containers.RepeatedScalarFieldContainer[str]
    output_path: str
    def __init__(
        self,
        num_mappers: _Optional[int] = ...,
        partition_paths: _Optional[_Iterable[str]] = ...,
        output_path: _Optional[str] = ...,
    ) -> None: ...

class ReduceResponse(_message.Message):
    __slots__ = ("output_path",)
    OUTPUT_PATH_FIELD_NUMBER: _ClassVar[int]
    output_path: str
    def __init__(self, output_path: _Optional[str] = ...) -> None: ...

class ReduceChangePathMes(_message.Message):
    __slots__ = ("mapper_id", "new_partition_path")
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_PARTITION_PATH_FIELD_NUMBER: _ClassVar[int]
    mapper_id: int
    new_partition_path: str
    def __init__(
        self, mapper_id: _Optional[int] = ..., new_partition_path: _Optional[str] = ...
    ) -> None: ...
