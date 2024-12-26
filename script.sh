#!/bin/bash

# Set variables for versioning
HELM_VERSION="v3.12.0"
K3S_VERSION="v1.27.1+k3s1"
KUBECTL_VERSION="v1.27.3"

# Update system and install required dependencies
echo "Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget apt-transport-https gnupg2 lsb-release

# 1. Install Helm
echo "Installing Helm..."
curl https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
rm -rf linux-amd64 helm.tar.gz

# 2. Install K3s (Lightweight Kubernetes)
echo "Installing K3s..."
curl -sfL https://get.k3s.io | sh -s -v ${K3S_VERSION}

# Set KUBEVERSION environment variable to access K3s kubeconfig
export KUBEVERSION=$(sudo cat /etc/rancher/k3s/k3s.yaml | tail -n +2 | sed 's/127.0.0.1/localhost/g')

# Export KUBEVERSION to access kubectl
export KUBEVERSION_PATH=/etc/rancher/k3s/k3s.yaml
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config

# Install kubectl
echo "Installing kubectl..."
curl -LO https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# 3. Test Kubernetes and kubectl
echo "Verifying kubectl installation..."
kubectl version --client

# 4. Install ResourceQuota and Helm Chart Example
echo "Creating a Helm chart with ResourceQuota..."

# Create a basic Helm chart to install ResourceQuota
helm create my-release

# Create ResourceQuota file inside templates folder
cat <<EOF > my-release/templates/resourcequota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: resource-quota
  namespace: default
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "6"
    limits.memory: "12Gi"
    pods: "10"
    services: "5"
EOF

# Install Helm chart with ResourceQuota
cd my-release
helm install my-resource-quota .

# 5. Verify ResourceQuota
echo "Checking if ResourceQuota is applied correctly..."
kubectl get resourcequota -o yaml
