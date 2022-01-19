# Kubernetes

## 1. `minikube` and `kubctl`

For running a local kubernetes development cluster you will need to install `minikube`. Please follow the instructions [here](https://kubernetes.io/docs/tasks/tools/install-minikube/).

You will also need to install Kubernetes command line tool as shown [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/).

## 2. Starting a Kubernetes cluster

You can either run a local cluster with minikube (ideal for development) or deploy your containers on the cloud (eg. Google Compute Platform).

**a) minikube**

To start `minikube` run:
```bash
minikube start --vm=true
```
Enable ingress:
```bash
minikube addons enable ingress
```
and control that your ingress pod is running:
```bash
kubectl get pods -n kube-system
```
If you need to stop and delete minikube run:
```bash
minikube stop && minikube delete
```

**Changing between clusters and contexts**

List clusters:
```
kubectl config get-clusters
```

List contexts:
```
kubectl config get-contexts
```

Check current context:
```
kubectl config current-context
```

Change context:
```
kubectl config use-context <context name>
```

Change namespace:
```
kubectl config set-context --current --namespace=<namespace>
```

## 3. Deploy your App

If you need to get registry authorization to pull containers you will need to create a matching secret. eg.:
```bash
kubectl create secret docker-registry <secret name> --docker-server=<registry address> --docker-username=<registry user name> --docker-password=<registry password> --docker-email=<your associated email>
```
More info on: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

Create a secret for flaskis' mail account:
```bash
kubectl create secret generic gmailpass --from-literal=pass='<password>'
```
Edit `secrets.yaml` and create required flaski secrets:
```bash
kubectl apply -f secrets.yaml
```
You can use `openssl` to generate safe keys `openssl rand -base64 <desired_length>`.

If working with cephs, start by starting the file system:
```
kubectl apply -f ceph-filesystem.yaml
```
Followed by the storage class and volume claims:
```
kubectl apply -f ceph-storageclass.yaml
kubectl apply -f ceph-users-volume-claim.yaml
kubectl apply -f ceph-db-volume-claim.yaml
kubectl apply -f ceph-backup-volume-claim.yaml
```
Inline:
```
kubectl apply -f ceph-storageclass.yaml ceph-users-volume-claim.yaml ceph-db-volume-claim.yaml ceph-backup-volume-claim.yaml
```

Other generage the volumes and persistent volume claims for your local machine with:
```bash
kubectl apply -f users-volume.yaml
kubectl apply -f users-volume-claim.yaml
kubectl apply -f db-volume.yaml
kubectl apply -f db-volume-claim.yaml
kubectl apply -f backup-volume.yaml
kubectl apply -f backup-volume-claim.yaml
```
Use deployments to start your pods:
```bash
kubectl apply -f mariadb-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f rsync-pod.yaml
```
Inline:
```
kubectl apply -f mariadb-deployment.yaml redis-deployment.yaml rsync-pod.yaml
```
At this point, if you have data to be restored, you can bring it
to the backup volume by 
```
kubectl cp ~/myapp_backup/* rsync:/backup/
```
Afterwards, you can keep on launching your services:
```
kubectl apply -f init-pod.yaml
kubectl apply -f backup-cron.yaml
kubectl apply -f server-deployment.yaml
```
Inline:
```
kubectl apply -f init-pod.yaml backup-cron.yaml server-deployment.yaml
```
For traefik ingress use:
```
kubectl apply -f traefik-ingress.yaml
```

This will start respective deployments and services. Services make sure that in case pod dies and a new one starts the address in use to contact the pod is not IP dependent.

Check that your pods and services are running:
```bash
kubectl get pods
kubectl get services
```
If you have problems starting a pod you can investigate a failing pod with:
```bash
kubectl describe pods <pod name>
```
To check the `stdout` of a running pod:
```bash
kubectl logs <pod name>
```
To enter a shell in a container:
```bash
kubectl exec -it <pod name> -- /bin/bash
```
To delete a pod:
```bash
kubectl delete pod <pod name>
```
To delete a deployment:
```bash
kubectl delete deployment <deployment name>
```
To delete a service:
```bash
kubectl delete service <service name>
```