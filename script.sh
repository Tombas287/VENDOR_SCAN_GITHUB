#!/bin/bash

# Set variables for versioning
HELM_VERSION="v3.12.0"
K3S_VERSION="v1.27.1+k3s1"
KUBECTL_VERSION="v1.27.3"

# Install dependencies
echo "Installing required dependencies..."
sudo apt-get update && sudo apt-get install -y curl wget apt-transport-https gnupg2

# Install Helm
echo "Installing Helm..."
curl https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
rm -rf linux-amd64 helm.tar.gz

# Install K3s
echo "Installing K3s..."
curl -sfL https://get.k3s.io | sh -s -v ${K3S_VERSION}

# Wait for K3s to start and configure kubeconfig
echo "Waiting for K3s to start..."
sleep 120  # Wait for K3s to fully initialize

# Check if K3s is running
if ! systemctl is-active --quiet k3s; then
  echo "K3s is not running! Please check the system logs."
  exit 1
fi

# Set up kubectl
echo "Setting up kubectl..."
curl -LO https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/  # Ensure kubectl is in the system PATH

# Set the kubeconfig
sudo cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config

# Verify installations
echo "Verifying kubectl and Helm installation..."
helm version
kubectl version --client
kubectl cluster-info

# Check K3s status and nodes
kubectl get nodes
