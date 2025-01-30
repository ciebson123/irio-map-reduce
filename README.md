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

## Ruff
To run the linter, use
```shell
ruff check
```
It will propose changes if any problems found. To apply, use 
```shell
ruff check --fix
```

Similarly, for the formatter:
```shell
ruff format --check
```
and 
```shell
ruff format
```

These will be run in github actions and the pipeline will fail if any checks or tests fail.

## Build docker

First, [install docker](https://docs.docker.com/engine/install/ubuntu/)
Then, run `sudo docker compose build`

## How to deploy

### One time things

Install `docker`, `gcloud` and `kubectl`.

To deploy, you must be in the `docker` group (as otherwise gcloud auth won't work)
Run `sudo usermod -a -G docker ${USER}` and restart your machine

Create the .env file that exports the id of your project as `PROJECT_ID`

Enable the filestore API in gcloud.

### Deployment

Run `setup_app.sh`. This should 
1. Build docker images.
2. Start a cluster.
3. Start the registry for docker.
4. Configure docker with google auth and push the images to registry.
5. Deploy `master` and `worker` to the cluster.

### Updating the image

If you already set up the cluster and registry, you can run `update_image.sh` to build new docker image and roll it out to the cluster.

### Deletion

To delete your cluster and registry, run `delete_all.sh`. You will have to confirm both deletions.

### Troubleshooting

If the images don't want to build or don't run on GCE, try using gcloud console. 
There might be an issue with building docker on ARM architecture.

## Usage
After successful deployment, retrieve the external IP of `upload-service` using 
```
kubectl get services
```
### Upload implementation of mapper and reducer

Use the `/mapper-reducer/` endpoint.
```
curl -X POST "http://<external-ip>:8082/mapper-reducer/" \
-H "Content-Type: multipart/form-data" \
-F "mapper_file=@src/worker/example_mapper.py" \
-F "reducer_file=@src/worker/example_reducer.py"

```

### Upload input file and start computation
Send a request to the / endpoint to upload your file. Once uploaded successfully, the computation starts automatically, and the result is returned in the response.

You need to provide: 
- `file` - a ZIP file containing input data
- `num_partitions` - number of partitions for MapReduce
```
curl -X 'POST' 'http://<external-ip>:8082/' \
-H 'accept: application/octet-stream' \
-H 'Content-Type: multipart/form-data' \
-F 'file=@data.zip' \
-F 'num_partitions=5' -o result.zip
```
