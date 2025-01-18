#!/bin/bash
export CLUSTER_NAME=map-reduce-cluster
export REGION=us-central1
export REPOSITORY_NAME=map-reduce-repo
export IMAGE1_NAME=irio-map-reduce-master
export IMAGE2_NAME=irio-map-reduce-worker
export IMAGE_LOCAL_VERSION=latest

#check if .image_version exists
if [ ! -f .image_version ]; then
    echo 0 > .image_version
fi
export IMAGE_REMOTE_VERSION=$(cat .image_version)
export IMAGE_REMOTE_VERSION=$((IMAGE_REMOTE_VERSION+1))
echo $IMAGE_REMOTE_VERSION > .image_version

source .env
set -e
#Build the images
docker compose build

# Tag the images

docker tag $IMAGE1_NAME:$IMAGE_LOCAL_VERSION $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE1_NAME:v$IMAGE_REMOTE_VERSION
docker tag $IMAGE2_NAME:$IMAGE_LOCAL_VERSION $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE2_NAME:v$IMAGE_REMOTE_VERSION
# Push the images to the registry

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE1_NAME:v$IMAGE_REMOTE_VERSION
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE2_NAME:v$IMAGE_REMOTE_VERSION

# Deploy the images to the cluster
envsubst <k8s-deployment/master-deployment.yaml | kubectl apply -f -
envsubst <k8s-deployment/worker-deployment.yaml | kubectl apply -f -
envsubst <k8s-deployment/update-deployment.yaml | kubectl apply -f -