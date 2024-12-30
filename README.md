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

## How to deploy

### One time things

Install `docker`, `gcloud` and `kubectl`.

To deploy, you must be in the `docker` group (as otherwise gcloud auth won't work)
Run `sudo usermod -a -G docker ${USER}` and restart your machine

Create the .env file that exports the id of your project as `PROJECT_ID`

### Deployment

Run `setup_app.sh`. This should 
1. Build docker images.
2. Start a cluster.
3. Start the registry for docker.
4. Configure docker with google auth and push the images to registry.
5. Deploy `master` and `worker` to the cluster.

### Deletion

To delete your cluster and registry, run `delete_all.sh`. You will have to confirm both deletions.


