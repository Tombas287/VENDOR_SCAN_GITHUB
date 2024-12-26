import json
import subprocess
import yaml

# Function to get the resourcequota YAML for the given namespace

# Alert thresholds for resources (in percentage)
alert_thresholds = {
    'cpu': 80,  # percentage
    'memory': 80,  # percentage
    'pods': 80,  # percentage
    'services': 80  # percentage
}

def get_resourcequota_yaml(namespace='default'):
    try:
        cmd = ["kubectl", "get", "resourcequota", "-n", namespace, "-o", "yaml"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout.decode()
        else:
            print(f"Error running kubectl: {result.stderr.decode()}")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Helper function to parse memory (e.g., '2Gi' -> 2Gi -> 2 * 1024 Mi)
def parse_memory(memory_str):
    if memory_str.endswith("Gi"):
        return int(memory_str[:-2]) * 1024  # Convert Gi to Mi
    elif memory_str.endswith("Mi"):
        return int(memory_str[:-2])  # Already in Mi
    elif memory_str.endswith("Ki"):
        return int(memory_str[:-2]) / 1024  # Convert Ki to Mi (smaller units)
    elif memory_str.endswith("Ti"):
        return int(memory_str[:-2]) * 1024 * 1024  # Convert Ti to Mi
    else:
        raise ValueError(f"Unsupported memory format: {memory_str}")

# Helper function to parse CPU (e.g., '100m' -> 0.1 cores)
def parse_cpu(cpu_str):
    if cpu_str.endswith("m"):
        return int(cpu_str[:-1]) / 1000  # Convert millicores to cores
    elif cpu_str.endswith("") or cpu_str.endswith("c"):  # Assume core units
        return float(cpu_str)
    else:
        raise ValueError(f"Unsupported CPU format: {cpu_str}")

# Function to check CPU and Memory usage percentages based on hard limits and actual usage
def check_resource_usage(resourcequota):
    # Print the structure of the resource quota for debugging
    print("ResourceQuota structure:")

    # Check if 'status.used' exists
    if 'status' not in resourcequota or 'used' not in resourcequota['status']:
        print(f"No resource usage info found for {resourcequota['metadata']['name']}")
        return None

    # Access the 'used' section inside 'status'
    used = resourcequota['status']['used']
    hard_limits = resourcequota['spec']['hard']

    usage_percentages = []

    # pod Usage
    if 'pods' in used and 'pods' in hard_limits:
        used_pod = int(used['pods'])
        limit_pod = int(hard_limits['pods'])
        pod_percent = (used_pod/limit_pod) * 100
        print(f"Pod percentage has increased by: {pod_percent:.2f}%") if pod_percent > alert_thresholds['pods'] \
            else "Not increased"
        usage_percentages.append(f"pod usage: {pod_percent:.2f}%")

    # CPU Usage
    if 'limits.cpu' in used and 'limits.cpu' in hard_limits:
        used_cpu = parse_cpu(used['limits.cpu'])
        limit_cpu = parse_cpu(hard_limits['limits.cpu'])
        cpu_usage_percent = (used_cpu / limit_cpu) * 100
        print(f"Pod percentage has increased by: {cpu_usage_percent:.2f}%") if cpu_usage_percent > alert_thresholds['pods'] \
            else "Not increased"
        usage_percentages.append(f"CPU usage: {cpu_usage_percent:.2f}%")

    # Memory Usage
    if 'limits.memory' in used and 'limits.memory' in hard_limits:
        used_memory = parse_memory(used['limits.memory'])
        limit_memory = parse_memory(hard_limits['limits.memory'])
        memory_usage_percent = (used_memory / limit_memory) * 100
        print(f"Pod percentage has increased by: {memory_usage_percent:.2f}%") if memory_usage_percent > alert_thresholds[
            'pods'] \
            else "Not increased"
        usage_percentages.append(f"Memory usage: {memory_usage_percent:.2f}%")

    # Return the usage percentages
    return usage_percentages if usage_percentages else None

def get_json_data(resourcequota):
    data = {
        "resourcequota":{
            "name": resourcequota['metadata']['name'],
            "namespace": resourcequota['metadata']['namespace'],
            "usage": resourcequota['status']['used'],
            "limits": resourcequota['spec']['hard']

        },

    }
    return json.dumps(data, indent=3)




if __name__ == "__main__":
    # Get the ResourceQuota YAML for the default namespace
    output = get_resourcequota_yaml()
    if output:
        # Parse the YAML
        resourceQuotas = yaml.safe_load(output)

        # Loop through each resource quota and calculate the usage
        for resourceQuota in resourceQuotas['items']:
            usage_info = check_resource_usage(resourceQuota)
            if usage_info:
                print("\n".join(usage_info))
            else:
                print(f"No resource usage info found for {resourceQuota['metadata']['name']}")
            json_data = get_json_data(resourceQuota)
            print(json_data)

