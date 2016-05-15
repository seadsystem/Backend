#!/bin/sh
# Finish deploying the SEAD API and landing zone

set -e

# Get source directory, current working directory by default
SRC="`pwd`"
test -n "$1" && SRC="$1"
if ! test -d "$SRC"; then
    echo "Fatal: failed to locate source directory ${SRC}"
    exit 1
fi

# Set target directories
LZ='/home/landingzone/go/src/github.com/seadsystem/Backend/DB/landingzone'
APIDB='/home/seadapi/DB'

# Copy server code and set ownership
mkdir -p ${LZ}
mkdir -p ${APIDB}
rsync -avc ${SRC}/landingzone/ ${LZ}/
cp ${SRC}/__init__.py ${APIDB}/
rsync -avc ${SRC}/api/ ${APIDB}/api
rsync -avc ${SRC}/classification/ ${APIDB}/classification
chown -R seadapi:seadapi ${APIDB}
chown -R landingzone:landingzone /home/landingzone
su -c "cd ${LZ} && env GOPATH='/home/landingzone/go' go install" - landingzone 

# Start each server
service seadapi start
service landingzone start
