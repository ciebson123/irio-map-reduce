mkdir -p protos_out


python -m grpc_tools.protoc -Isrc/generated_files=./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/mapper.proto
python -m grpc_tools.protoc -Isrc/generated_files=./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/reducer.proto
python -m grpc_tools.protoc -Isrc/generated_files=./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/master.proto
python -m grpc_tools.protoc -Isrc/generated_files=./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/upload.proto