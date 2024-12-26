#!/bin/bash

# Exit on error
set -e

echo "Starting K3s, kubectl, and Helm setup..."

# Step 1: Install K3s (without systemd)
echo "Installing K3s..."
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
sleep 30
# Wait for K3s to start
echo "Waiting for K3s to be ready..."
sudo k3s kubectl get nodes

# Step 2: Install kubectl
echo "Installing kubectl..."
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.27.3/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# Step 3: Set up kubeconfig for kubectl
echo "Setting up kubeconfig for kubectl..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# Step 4: Verify kubectl installation
echo "Verifying kubectl installation..."
kubectl version --client

# Step 5: Install Helm
echo "Installing Helm..."
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Step 6: Verify Helm installation
echo "Verifying Helm installation..."
helm version

# Step 7: Deploy a sample chart using Helm (nginx-ingress as an example)
echo "Deploying nginx-ingress using Helm..."
helm install tommy myrelease 

# Step 8: Verify the deployment using kubectl
echo "Verifying the deployment..."
kubectl get pods --all-namespaces

echo "K3s, kubectl, and Helm setup completed successfully!"
