import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')
GIT_TOKEN = os.getenv('GIT_TOKEN')


def get_issue_and_update(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    response = requests.get(url, headers={"Authorization": f"token {GIT_TOKEN}"})

    if response.status_code == 200:
        issues = response.json()

        if not issues:
            print("No issues found.")
            return
        task_completed = None
        for issue in issues:

            # Check if any task is marked as completed
            if '- [x] rollback' in issue['body']:
                task_completed = 'rollback'
            elif '- [x] scale_down' in issue['body']:
                task_completed = 'scale_down'
            elif '- [x] scale_up' in issue['body']:
                task_completed = 'scale_up'

            else:
                print(f"No task is completed in issue: {issue['html_url']}")
                task_completed = None
            print()
        print(f"Task completed: {task_completed}")

    else:
        print(f"Failed to fetch issues. Status Code: {response.status_code}")
        # Uncomment to debug
        # print(response.text)

get_issue_and_update(repo_owner, repo_name)
