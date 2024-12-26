import subprocess
import requests
import json
import os
from dotenv import load_dotenv
from termcolor import colored
load_dotenv()
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')
GIT_TOKEN = os.getenv("GIT_TOKEN")

def create_issue(repo_owner, repo_name):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
    tasks = ["rollback", "scale_down", "scale_up"]
    body = '\n'.join([f'- [ ] {task}' for task in tasks])

    issue = {
        "title": 'Perform following operations task',
        "body": body,
        "assignees": ["maxwell134"],
        "labels": tasks
    }

    response = requests.post(url, headers={"Authorization": f"token {GIT_TOKEN}"},
                             data=json.dumps(issue))

    if response.status_code == 201:
        issue_url = response.json()['html_url']
        # Print the URL in green color
        print(f"Successfully created issue. View it at: {colored(issue_url, 'green')}")
    else:
        print("Failed to create issue.")
        print(response.text)


# Example usage
create_issue(repo_owner, repo_name)

