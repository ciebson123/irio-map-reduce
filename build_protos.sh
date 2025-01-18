mkdir -p protos_out


python -m grpc_tools.protoc -Isrc/generated_files=./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/worker.proto
python -m grpc_tools.protoc -Isrc/generated_files=./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/master.proto