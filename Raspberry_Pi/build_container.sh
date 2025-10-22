#!/bin/bash
# This script builds the container using the Dockerfile in this directory
# 1.0.0 new build
# 1.0.2 add logging

currentDir=$(pwd)
VERSION=1.0.1
NAME=pi_brain

set -e

mkdir -p /opt/scripts/csv_files

echo "Build container $NAME:$VERSION"
podman build -f Dockerfile -t $NAME:$VERSION .
echo "Finished building container"
podman rmi python:3.11-slim
podman images


echo "Create tar"
podman save -o $NAME-$VERSION.tar $NAME:$VERSION
ls | grep .tar