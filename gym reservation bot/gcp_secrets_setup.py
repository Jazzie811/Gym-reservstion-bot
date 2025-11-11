#!/usr/bin/env python3
"""
Helper script to set up secrets in GCP Secret Manager.
Run this once to store your credentials securely in GCP.
"""

import os
from google.cloud import secretmanager
from google.auth.exceptions import GoogleAuthError

def create_secret(project_id, secret_id, secret_value):
    """Create or update a secret in GCP Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}"
        
        # Check if secret exists
        secret_path = f"{parent}/secrets/{secret_id}"
        try:
            client.get_secret(request={"name": secret_path})
            print(f"Secret '{secret_id}' already exists. Updating...")
        except Exception:
            # Secret doesn't exist, create it
            print(f"Creating secret '{secret_id}'...")
            client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
        
        # Add a new version with the secret value
        parent_secret = f"{parent}/secrets/{secret_id}"
        response = client.add_secret_version(
            request={
                "parent": parent_secret,
                "payload": {"data": secret_value.encode("UTF-8")},
            }
        )
        print(f"Successfully created/updated secret '{secret_id}'")
        return response
        
    except GoogleAuthError as e:
        print(f"GCP authentication error: {e}")
        print("Make sure you have authenticated with: gcloud auth application-default login")
        raise
    except Exception as e:
        print(f"Error creating secret '{secret_id}': {e}")
        raise

def main():
    """Main function to set up all secrets."""
    project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        project_id = input("Enter your GCP Project ID: ").strip()
        if not project_id:
            print("Error: GCP Project ID is required")
            return
    
    print(f"Setting up secrets for project: {project_id}")
    print("=" * 60)
    
    # Get credentials from user
    username = input("Enter your gym username: ").strip()
    password = input("Enter your gym password: ").strip()
    reservation_url = input("Enter the gym reservation URL: ").strip()
    
    if not all([username, password, reservation_url]):
        print("Error: All fields are required")
        return
    
    try:
        # Create secrets
        create_secret(project_id, "gym-username", username)
        create_secret(project_id, "gym-password", password)
        create_secret(project_id, "gym-reservation-url", reservation_url)
        
        print("=" * 60)
        print("All secrets have been successfully stored in GCP Secret Manager!")
        print("\nNext steps:")
        print("1. Set USE_GCP_SECRETS=true in your environment")
        print(f"2. Set GCP_PROJECT_ID={project_id} in your environment")
        print("3. Make sure your VM has the Secret Manager Secret Accessor role")
        
    except Exception as e:
        print(f"Error setting up secrets: {e}")

if __name__ == "__main__":
    main()

