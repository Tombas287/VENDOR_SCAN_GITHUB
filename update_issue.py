import requests
import json
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')
GIT_TOKEN = os.getenv('GIT_TOKEN')


def fetch_deployments():
    """Fetch the list of deployments using kubectl."""
    commands = 'kubectl get deployments -o jsonpath="{.items[*].metadata.name}"'
    result = subprocess.run(commands, check=True, stdout=subprocess.PIPE)
    deployments = result.stdout.decode('utf-8').split()
    return deployments


def get_current_replica_count(deployment):
    """Get the current replica count for a given deployment."""
    command = f"kubectl get deployment {deployment} -o=jsonpath='{{.spec.replicas}}'"
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    return int(result.stdout.decode('utf-8'))


def task_to_perform(deployment):
    """Map the task to kubectl commands."""

    # Get current replica count for scaling down by 1
    current_replicas = get_current_replica_count(deployment)

    # Define kubectl tasks
    task = {
        'rollback': f'kubectl rollout undo deployment/{deployment}',
        'scale_down': f'kubectl scale deployment/{deployment} --replicas={max(1, current_replicas - 1)}',
        # Scale down by 1, but not less than 1
        'scale_up': f'kubectl scale deployment/{deployment} --replicas={current_replicas + 1}'  # Scale up by 1
    }
    return task


def get_issue_and_update(repo_owner, repo_name):
    """Fetch GitHub issues and determine the completed task."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    response = requests.get(url, headers={"Authorization": f"token {GIT_TOKEN}", timeout=20})

    if response.status_code == 200:
        issues = response.json()

        if not issues:
            print("No issues found.")
            return None

        completed_tasks = []
        issue_to_update = None  # Variable to hold the issue to be updated after task completion

        for issue in issues:
            issue_body = issue['body']  # Get the issue body

            # Store completed tasks in a list
            if '- [x] rollback' in issue_body:
                completed_tasks.append('rollback')
            if '- [x] scale_down' in issue_body:
                completed_tasks.append('scale_down')
            if '- [x] scale_up' in issue_body:
                completed_tasks.append('scale_up')

            if len(completed_tasks) == 0:
                print(f"No task is completed in issue: {issue['html_url']}")

            if len(completed_tasks) > 1:
                print("Multiple options are selected. Choose only one option to proceed.")
                print(f"Issue: {issue['html_url']}")

            else:
                task_completed = completed_tasks[0]
                issue_to_update = issue  # Save the issue to close later
                return task_completed, issue_to_update

    else:
        print(f"Failed to fetch issues. Status Code: {response.status_code}")
        # Uncomment to debug
        # print(response.text)
    return None, None


def execute_task(task_name, deployment):
    """Execute the kubectl command based on the task name."""
    task_commands = task_to_perform(deployment)

    if task_name in task_commands:
        command = task_commands[task_name]

        if task_name == 'rollback':
            try:
                print(f"Executing task: {task_name}")
                print(f"Command: {command}")
                # Check for the rollout history before attempting undo
                rollout_history_check_command = f"kubectl rollout history deployment/{deployment} --revision=1"
                history_result = subprocess.run(rollout_history_check_command, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)

                if history_result.returncode != 0:
                    print(f"No rollout history found for deployment {deployment}. Skipping rollback.")
                else:
                    subprocess.run(command, check=True)
                    print(f"Task {task_name} completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error executing the command: {e}")
        else:
            # For scale and other tasks, execute normally
            try:
                print(f"Executing task: {task_name}")
                print(f"Command: {command}")
                subprocess.run(command, shell=True, check=True)
                print(f"Task {task_name} completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error executing the command: {e}")

    else:
        print(f"Invalid task: {task_name}")


def close_issue(issue_number):
    """Close the GitHub issue by updating its state to 'closed'."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
    data = {'state': 'closed'}
    response = requests.patch(url, headers={"Authorization": f"token {GIT_TOKEN}"}, json=data)

    if response.status_code == 200:
        print(f"Issue #{issue_number} closed successfully.")
    else:
        print(f"Failed to close issue #{issue_number}. Status Code: {response.status_code}")
        # Uncomment to debug
        # print(response.text)


# Main flow
def main():
    # Fetch deployment names
    deployments = fetch_deployments()

    if not deployments:
        print("No deployments found.")
        return

    # Fetch the task to perform from GitHub issues and the issue to update
    task_name, issue_to_update = get_issue_and_update(repo_owner, repo_name)

    if task_name:
        # Use the first deployment if available
        deployment = deployments[0]  # Select the first deployment
        execute_task(task_name, deployment)

        # If an issue was fetched, close it after completing the task
        if issue_to_update:
            issue_number = issue_to_update['number']  # Get the issue number
            close_issue(issue_number)
    else:
        print("No valid task found to perform.")


# Run the script
if __name__ == "__main__":
    main()
