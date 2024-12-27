# irio-map-reduce

## Set up
First, install all required dependencies 
```shell
pip install -r requirements.txt
```
## Unit tests
To run all tests, run
```shell
pytest
```
To run all tests in a module, you can provide a path. For example:
```shell
pytest tests/service
```

## Build docker

First, [install docker](https://docs.docker.com/engine/install/ubuntu/)
Then, run `sudo docker compose build`