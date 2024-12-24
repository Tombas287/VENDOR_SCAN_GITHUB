import json
def extract_cred():
    cred = {}
    docker_user = '7002370412'
    docker_password = '7002370412'
    cred['username'] = docker_user
    cred['password'] = docker_password
    with open('cred.env', 'w') as f:
        f.write(f"DOCKER_USERNAME={docker_user}\n")
        f.write(f"DOCKER_PASSWORD={docker_password}\n")

    print("Environment variables written to cred.env")

extract_cred()
