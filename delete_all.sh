#!/bin/bash
CLUSTER_NAME=map-reduce-cluster
REGION=us-central1
REPOSITORY_NAME=map-reduce-repo

source ./.env

kubectl delete service master-service
kubectl delete deployment master-app
kubectl delete deployment worker-app
kubectl delete deployment upload-app

# delete the pvc to delete filestore
kubectl delete pvc fileserver

# Delete the repository

gcloud artifacts repositories delete $REPOSITORY_NAME --location=$REGION --project=$PROJECT_ID

# Delete the cluster

gcloud container clusters delete $CLUSTER_NAME --region $REGION