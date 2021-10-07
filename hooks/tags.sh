#!/bin/bash

set -e

# Parse image name for repo name
tagStart=$(expr index "$IMAGE_NAME" :)
repoName=${IMAGE_NAME:0:tagStart-1}

echo ":: Additional tagging"
echo ":: Current tag: ${tagStart}"

# Tag and push image for each additional tag
if [ "${tagStart}" == "latest" ] ; then
    if [ $(git describe --abbrev=0 --tags) ] ; 
        then 
            tag=$(git describe --abbrev=0 --tags)
            docker tag $IMAGE_NAME ${repoName}:${tag}-latest
            docker push ${repoName}:${tag}-latest
            echo ":: Added ${tag}-latest tag"
    fi
elif [ "${tagStart}" == "nightly" ] ;
    if [ $(git describe --abbrev=0 --tags) ] ; 
        then 
            tag=$(git describe --abbrev=0 --tags)
            docker tag $IMAGE_NAME ${repoName}:${tag}-nightly
            docker push ${repoName}:${tag}-nightly
            docker tag $IMAGE_NAME ${repoName}:latest
            docker push ${repoName}:latest
            echo ":: Added ${tag}-nightly tag"
            echo ":: Added latest tag"
    fi
else ;
    if [ $(git describe --abbrev=0 --tags) ] ; 
        then 
            tag=$(git describe --abbrev=0 --tags)
            docker tag $IMAGE_NAME ${repoName}:latest
            docker push ${repoName}:latest
            echo ":: Added latest tag"
    fi
fi