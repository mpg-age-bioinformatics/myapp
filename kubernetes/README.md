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

Creating a namespace:
```
kubectl create namespace myapp
```

Change to the myapp namespace:
```
kubectl config set-context --current --namespace=myapp
```

## 3. Deploy your App

If you need to get registry authorization to pull containers you will need to create a matching secret. eg.:
```bash
kubectl create secret docker-registry dockerlogin --docker-server=https://index.docker.io/v1/ --docker-username=<registry user name> --docker-password=<access_token> --docker-email=<your associated email>
```
More info on: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

Create a secret for mail' mail account:
```bash
kubectl create secret generic emailpass --from-literal=pass='<password>'
```
Edit `secrets.yaml` and create required myapp secrets:
```bash
kubectl apply -f secrets.yaml
```
You can use `openssl` to generate safe keys `openssl rand -base64 <desired_length>`.

```
kubectl apply -f 01_db-volume.yaml 
kubectl apply -f 02_db-volume-claim.yaml
kubectl apply -f 03_backup-volume.yaml 
kubectl apply -f 04_backup-volume-claim.yaml
kubectl apply -f 05_mariadb-deployment.yaml
kubectl apply -f 06_redis-deployment.yaml
kubectl apply -f 07_init-pod.yaml
kubectl apply -f 08_backup-cron.yaml
kubectl apply -f 09_server-deployment.yaml
kubectl apply -f 10.1_traefik-rbac.yaml
kubectl apply -f 10.2_traefik-deployment.yaml 
kubectl apply -f 10.3_traefik-ui.yaml
kubectl apply -f 11_server-ingress.yaml
```
Add minukube's ip to your hosts list:
```
echo "$(minikube ip) minikube" | sudo tee -a /etc/hosts
```

You should now be able to access https://myapp.minikube and https://traefik-ui.minikube.