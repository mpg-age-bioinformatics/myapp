# myapp

myapp is a universal backbone for flask-dash based apps with user level authentication. myapp can be deployed using the `docker-compose.yml` or on a [kubernetes](https://github.com/jorgeboucas/myapp/tree/master/kubernetes#kubernetes) cluster.

## Building for flaski2

```
MYAPP_VERSION=$(git rev-parse --short HEAD)
repoName=mpgagebioinformatics/myapp-flaski2:{MYAPP_VERSION}
docker build --build-arg BUILD_NAME=flaski --build-arg MYAPP_VERSION=${MYAPP_VERSION} --no-cache -t ${repoName} -f services/server/Dockerfile .
docker push ${repoName}
```