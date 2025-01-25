import requests
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from PIL import Image
from tasks.phase_a import is_valid_path
from bs4 import BeautifulSoup
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

def run_sql_query(db_path, query, output_file):
    """
    Executes a SQL query on the given database and writes the results to a file.
    """
    try:
        # Validate paths
        if not is_valid_path(db_path) or not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Ensure the database file exists
        if not os.path.exists(db_path):
            return {"error": "Database file not found"}, 404

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(query)
        results = cursor.fetchall()

        # Write the results to the output file
        with open(output_file, 'w') as f:
            for row in results:
                f.write(", ".join(map(str, row)) + "\n")

        # Close the database connection
        conn.close()

        return {"message": f"Query executed successfully. Results saved to {output_file}"}, 200

    except sqlite3.Error as e:
        return {"error": f"SQL error: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500



def extract_data_from_website(url, output_file):
    """
    Extracts data from a website and saves it to a file.
    """
    try:
        # Step 1: Validate the output file path
        if not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Step 2: Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Step 3: Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Step 4: Extract useful data (e.g., title, meta tags)
        data = {
            "title": soup.title.string if soup.title else "No title found",
            "meta": [
                {"name": tag.get("name"), "content": tag.get("content")}
                for tag in soup.find_all("meta") if tag.get("name")
            ]
        }

        # Step 5: Save the extracted data to the output file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

        return {"message": f"Data extracted from {url} and saved to {output_file}"}, 200

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch the URL: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
    
def compress_or_resize_image(input_image, output_image, width=None, height=None, quality=85):
    """
    Compresses or resizes the input image and saves it to the output file.
    """
    try:
        # Validate paths
        if not is_valid_path(input_image) or not is_valid_path(output_image):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Ensure the input image exists
        if not os.path.exists(input_image):
            return {"error": "Input image file not found"}, 404

        # Open the image
        with Image.open(input_image) as img:
            # Convert RGBA or P mode images to RGB for JPEG compatibility
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize the image if width and height are provided
            if width and height:
                img = img.resize((width, height))

            # Save the image with specified quality
            img.save(output_image, "JPEG", optimize=True, quality=quality)

        return {"message": f"Image processed and saved to {output_image}"}, 200

    except Exception as e:
        return {"error": str(e)}, 500



