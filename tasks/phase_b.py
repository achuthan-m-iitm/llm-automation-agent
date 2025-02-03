import requests
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from PIL import Image
from tasks.phase_a import is_valid_path
from bs4 import BeautifulSoup
import whisper
import markdown
import csv
import shutil
# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Correctly point to the 'data' folder in the project root
DATA_DIRECTORY = os.path.join(PROJECT_ROOT, 'data')
REPO_DIR = os.path.join(DATA_DIRECTORY, "repo")

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


def clone_and_commit(repo_url, file_name="README.md", commit_message="Automated commit"):
    """
    Clones a GitHub repository, modifies a file, and commits & pushes the changes.
    """

    try:
        # ✅ Ensure /data directory exists
        os.makedirs(DATA_DIRECTORY, exist_ok=True)

        # ✅ Check if repo already exists
        if os.path.exists(REPO_DIR):
            return {"error": "Repository directory already exists. Please clean up before retrying."}, 400

        # ✅ Clone the GitHub repository
        subprocess.run(["git", "clone", repo_url, REPO_DIR], check=True)

        # ✅ Change directory to repo
        os.chdir(REPO_DIR)

        # ✅ Modify the file (append a timestamp)
        with open(file_name, "a") as f:
            f.write("\nAutomated update\n")

        # ✅ Add, commit, and push the changes
        subprocess.run(["git", "add", file_name], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)

        return {"message": f"Committed changes to {file_name} in the repository"}, 200

    except subprocess.CalledProcessError as e:
        return {"error": f"Git operation failed: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # ✅ Change back to original directory
        os.chdir(os.path.dirname(__file__))
    

def clone_github_repo():
    """
    Clones a GitHub repository into the /data directory. If the repository already exists, it deletes it first.
    """
    try:
        repo_url = "https://github.com/octocat/Hello-World.git"  # Replace with actual repo
        clone_path = os.path.join(DATA_DIRECTORY, "repo")

        # Ensure the data directory exists
        os.makedirs(DATA_DIRECTORY, exist_ok=True)

        # Remove existing repo before cloning
        if os.path.exists(clone_path):
            shutil.rmtree(clone_path)  # Deletes the entire directory
            print("Existing repository deleted.")

        # Run the git clone command
        subprocess.check_call(["git", "clone", repo_url, clone_path])

        return {"message": "Repository cloned successfully"}, 200

    except subprocess.CalledProcessError as e:
        return {"error": f"Git operation failed: {str(e)}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500

def run_sql_query(db_path, query, output_file):
    """
    Executes a SQL query on the given database and writes the results to a file.
    """
    try:
        print(f"DEBUG: Checking paths - DB: {db_path}, Output: {output_file}")  # Log paths
        if not is_valid_path(db_path) or not is_valid_path(output_file):
            print("DEBUG: Invalid path detected")
            return {"error": "Access to the specified path is not allowed"}, 403

        if not os.path.exists(db_path):
            print("DEBUG: Database file not found")
            return {"error": "Database file not found"}, 404

        print(f"DEBUG: Connecting to database {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"DEBUG: Executing query: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"DEBUG: Query results: {results}")

        print(f"DEBUG: Writing results to {output_file}")
        with open(output_file, 'w') as f:
            for row in results:
                f.write(", ".join(map(str, row)) + "\n")

        conn.close()
        return {"message": f"Query executed successfully. Results saved to {output_file}"}, 200

    except sqlite3.Error as e:
        print(f"DEBUG: SQL Error: {str(e)}")
        return {"error": f"SQL error: {str(e)}"}, 500
    except Exception as e:
        print(f"DEBUG: General Error: {str(e)}")
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
    
def transcribe_audio(input_audio, output_file):
    """
    Transcribes the given MP3 audio file and saves the transcription to a file.
    """
    try:
        # Validate paths
        if not is_valid_path(input_audio) or not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Ensure the input audio file exists
        if not os.path.exists(input_audio):
            return {"error": "Input audio file not found"}, 404

        # Load the Whisper model
        model = whisper.load_model("base")

        # Transcribe the audio file
        result = model.transcribe(input_audio)

        # Extract the transcription text
        transcription = result["text"]

        # Save the transcription to the output file
        with open(output_file, 'w') as f:
            f.write(transcription)

        return {"message": f"Audio transcribed successfully and saved to {output_file}"}, 200

    except Exception as e:
        return {"error": str(e)}, 500
    
def convert_markdown_to_html(input_file, output_file):
    """
    Converts a Markdown (.md) file into an HTML file.
    """
    try:
        # Validate file paths
        if not is_valid_path(input_file) or not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Read the Markdown content
        with open(input_file, 'r', encoding="utf-8") as f:
            md_content = f.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)

        # Save the HTML output
        with open(output_file, 'w', encoding="utf-8") as f:
            f.write(html_content)

        return {"message": f"Converted {input_file} to {output_file} successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500
    

def filter_csv_data(input_file, column_name, filter_value):
    """
    Filters a CSV file based on a given column and value.
    """
    try:
        # Validate file path
        if not is_valid_path(input_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        # Read and filter CSV data
        with open(input_file, 'r', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            filtered_rows = [row for row in reader if row.get(column_name) == filter_value]

        return {"filtered_data": filtered_rows}, 200

    except Exception as e:
        return {"error": str(e)}, 500




