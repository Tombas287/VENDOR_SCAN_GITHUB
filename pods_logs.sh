#!/bin/bash

# Get the desired pod name (replace with your dynamic logic)
pod_name=$(kubectl get pods -l app=your-app | awk '{print $1}' | head -n 1) 

# Check if pod name is found
if [ -z "$pod_name" ]; then
  echo "No pod found for app=your-app"
  exit 1
fi

# Describe the pod
kubectl describe pod "$pod_name"

# Get pod events
kubectl describe events --namespace=$(kubectl config current-context | cut -d '/' -f 1) | grep "$pod_name"

# Get pod logs
kubectl logs "$pod_name"
