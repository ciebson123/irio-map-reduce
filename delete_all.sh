CLUSTER_NAME=map-reduce-cluster
REGION=us-central1
REPOSITORY_NAME=map-reduce-repo
IMAGE1_NAME=irio-map-reduce-master
IMAGE2_NAME=irio-map-reduce-worker
IMAGE1_VERSION=latest
IMAGE2_VERSION=latest
source .env

# Delete the repository

gcloud artifacts repositories delete $REPOSITORY_NAME --location=$REGION --project=$PROJECT_ID

# Delete the cluster

gcloud container clusters delete $CLUSTER_NAME --region $REGION