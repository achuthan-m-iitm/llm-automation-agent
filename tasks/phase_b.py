import requests
import json
import os
import subprocess
from pathlib import Path
from tasks.phase_a import is_valid_path

def fetch_api_data(api_url, output_file):
    """
    Fetches data from the given API URL and saves it to a file in JSON format.
    """
    try:
        # Step 1: Validate the output file path
        if not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Step 2: Fetch data from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Step 3: Parse the JSON response
        data = response.json()

        # Step 4: Save the data to the output file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

        return {"message": f"Data fetched from {api_url} and saved to {output_file}"}, 200

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
    
def clone_and_commit(repo_url, file_name, commit_message):
    """
    Clones a git repository, creates/modifies a file, and makes a commit.
    """
    try:
        # Step 1: Validate paths
        clone_dir = os.path.join("./data", "repo")
        if not is_valid_path(clone_dir):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Step 2: Ensure the /data/repo directory doesn't already exist
        if os.path.exists(clone_dir):
            return {"error": "Repository directory already exists. Please clean up before retrying."}, 400

        # Step 3: Clone the repository
        subprocess.check_call(["git", "clone", repo_url, clone_dir])

        # Step 4: Create or modify the file in the cloned repository
        file_path = os.path.join(clone_dir, file_name)
        with open(file_path, "a") as f:
            f.write("\n# This is an automated change.\n")

        # Step 5: Commit the change
        subprocess.check_call(["git", "-C", clone_dir, "add", file_name])
        subprocess.check_call(["git", "-C", clone_dir, "commit", "-m", commit_message])

        return {"message": f"Committed changes to {file_name} in the repository"}, 200

    except subprocess.CalledProcessError as e:
        return {"error": f"Git operation failed: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
