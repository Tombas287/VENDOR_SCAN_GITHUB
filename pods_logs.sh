#!/bin/bash

# Get the desired pod name (replace with your dynamic logic)
# pod_name=$(kubectl get pods -o jsonpath='{.items[*].metadata.name}') 

# # Check if pod name is found
# if [ -z "$pod_name" ]; then
#   echo "No pod found for app=your-app"
#   exit 1
# fi

# Describe the pod
# kubectl describe pod "$pod_name"

# Get pod events
kubectl get events 
# Get pod logs
# kubectl logs "$pod_name"
