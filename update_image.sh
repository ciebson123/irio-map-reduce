export CLUSTER_NAME=map-reduce-cluster
export REGION=us-central1
export REPOSITORY_NAME=map-reduce-repo
export IMAGE1_NAME=irio-map-reduce-master
export IMAGE2_NAME=irio-map-reduce-worker
export IMAGE1_VERSION=latest
export IMAGE2_VERSION=latest
source .env
set -e
#Build the images
docker compose build

# Tag the images

docker tag $IMAGE1_NAME:$IMAGE1_VERSION $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE1_NAME:$IMAGE1_VERSION
docker tag $IMAGE2_NAME:$IMAGE2_VERSION $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE2_NAME:$IMAGE2_VERSION

# Push the images to the registry

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE1_NAME:$IMAGE1_VERSION
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE2_NAME:$IMAGE2_VERSION

# Deploy the images to the cluster

envsubst <k8s-deployment/master-deployment.yaml | kubectl apply -f -
envsubst <k8s-deployment/worker-deployment.yaml | kubectl apply -f -