import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the Key Vault URL
Key_vault_url = os.getenv("KEY_VAULT_URL")
github_env_path = os.getenv('GITHUB_ENV')


def fetch_secret_values():
    try:
        # Authenticate using ClientSecretCredential
        credentials = ClientSecretCredential(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            tenant_id=os.getenv("TENANT_ID")
        )

        # Connect to SecretClient
        secret_client = SecretClient(credential=credentials, vault_url=Key_vault_url)

        print("Fetching the secrets from the Azure Key Vault...")

        # List all secrets in the Key Vault
        secrets = secret_client.list_properties_of_secrets()

        with open(github_env_path, 'a') as f:
            for secret in secrets:
                # Fetch the actual secret value
                secret_value = secret_client.get_secret(secret.name).value
                # Write each secret to $GITHUB_ENV
                f.write(f"{secret.name}={secret_value}\n")

        print("Secrets successfully written to $GITHUB_ENV")

    except Exception as e:
        print(f"Error fetching secrets: {str(e)}")


# Call the function
fetch_secret_values()
