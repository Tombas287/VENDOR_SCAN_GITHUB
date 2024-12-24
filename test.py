import os
def extract_cred():
    cred = {}
    docker_user = ''
    docker_password = ''
    cred['username'] = docker_user
    cred['password'] = docker_password

    github_env_path = os.getenv('GITHUB_ENV')
    with open(github_env_path, 'a') as f:
        f.write(f"DOCKER_USERNAME={docker_user}\n")
        f.write(f"DOCKER_PASSWORD={docker_password}\n")

    print("Environment variables written to $GITHUB_ENV")

extract_cred()
