mkdir -p protos_out


python -m grpc_tools.protoc -I./protos --python_out=./protos_out --pyi_out=./protos_out/ --grpc_python_out=./protos_out ./protos/mapper.proto
python -m grpc_tools.protoc -I./protos --python_out=./protos_out --pyi_out=./protos_out/ --grpc_python_out=./protos_out ./protos/reducer.proto
python -m grpc_tools.protoc -I./protos --python_out=./protos_out --pyi_out=./protos_out/ --grpc_python_out=./protos_out ./protos/master.proto