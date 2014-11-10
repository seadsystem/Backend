#!/bin/sh
# Deploy the SEAD API and landing zone
# Prerequisites: puppet modules have been executed

# Get source directory, current working directory by default
SRC="`pwd`"
test -n "$1" && SRC="$1"
if ! test -d "$SRC"; then
    echo "Fatal: failed to locate source directory ${SRC}"
    exit 1
fi

# Set target directories
LZ='/home/landingzone/landingzone'
API='/home/seadapi/api'

# Copy server code and set ownership
rsync -avc ${SRC}/landingzone/ ${LZ}/
chown -R landingzone:landingzone $LZ
rsync -avc ${SRC}/api/ ${API}/
chown -R seadapi:seadapi ${API}
for module in constants database decoders handlers; do
    mkdir -p /home/landingzone/go/src/github.com/seadsystem/Backend/DB/landingzone/$module
    rsync -avc ${LZ}/$module/ /home/landingzone/go/src/github.com/seadsystem/Backend/DB/landingzone/$module/
done
chown -R landingzone:db /home/landingzone
su -c "env GOPATH='/home/landingzone/go' go build -o ${LZ}/landingzone ${LZ}/main.go" - landingzone 

# Start each server
service seadapi start
service landingzone start
