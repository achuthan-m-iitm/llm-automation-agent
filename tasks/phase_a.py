from datetime import datetime
import subprocess
import sys
import os
import requests
import json
from pathlib import Path

def count_wednesdays(input_file, output_file):
    """
    Counts the number of Wednesdays in the given input file
    and writes the count to the output file.
    """
    try:
        # Read the dates from the input file
        with open(input_file, 'r') as f:
            dates = [datetime.strptime(line.strip(), '%Y-%m-%d') for line in f]
        
        # Count the Wednesdays
        wednesday_count = sum(1 for date in dates if date.weekday() == 2)
        
        # Write the result to the output file
        with open(output_file, 'w') as f:
            f.write(str(wednesday_count))
        
        return {"message": f"Wednesdays counted: {wednesday_count}"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def install_uv_and_run_datagen(user_email):
    """
    Installs 'uv' and 'faker' (if needed), downloads 'datagen.py',
    modifies it to use a writable directory, and runs it.
    """
    try:
        # Step 1: Install required packages
        for package in ["uv", "faker"]:
            try:
                __import__(package)  # noqa
            except ImportError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        # Step 2: Download datagen.py
        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/datagen.py"
        script_path = "./data/datagen.py"
        os.makedirs("./data", exist_ok=True)  # Ensure the 'data' directory exists

        response = requests.get(url)
        if response.status_code == 200:
            with open(script_path, "wb") as file:
                file.write(response.content)
        else:
            return {"error": f"Failed to download datagen.py. HTTP Status: {response.status_code}"}, 500

        # Step 3: Modify datagen.py to use './data' as the root
        with open(script_path, "r") as file:
            content = file.read()
        modified_content = content.replace('"/data"', '"./data"')  # Replace hardcoded '/data' with './data'
        with open(script_path, "w") as file:
            file.write(modified_content)

        # Step 4: Run datagen.py with the user's email
        subprocess.check_call([sys.executable, script_path, user_email])

        return {"message": "datagen.py executed successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def format_file_with_prettier(file_path):
    """
    Formats the given file using Prettier, updating the file in place.
    """
    try:
        # Step 1: Check if Prettier is installed
        prettier_check = subprocess.run(["prettier", "--version"], capture_output=True, text=True)
        if prettier_check.returncode != 0:
            # Install Prettier globally using npm if not installed
            subprocess.check_call(["npm", "install", "-g", "prettier"])

        # Step 2: Format the file using Prettier
        subprocess.check_call(["prettier", "--write", file_path])

        return {"message": f"File {file_path} formatted successfully"}, 200

    except subprocess.CalledProcessError as e:
        return {"error": f"Prettier execution failed: {e}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
    
def sort_contacts(input_file, output_file):
    """
    Sorts contacts in the input JSON file by last_name and first_name,
    then writes the sorted contacts to the output JSON file.
    """
    try:
        # Read the input JSON file
        with open(input_file, 'r') as f:
            contacts = json.load(f)

        # Sort contacts by last_name, then by first_name
        sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

        # Write the sorted contacts to the output JSON file
        with open(output_file, 'w') as f:
            json.dump(sorted_contacts, f, indent=4)

        return {"message": f"Contacts sorted and saved to {output_file}"}, 200

    except Exception as e:
        return {"error": str(e)}, 500
    
def extract_recent_logs(input_dir, output_file, count=10):
    """
    Finds the most recent `.log` files in the specified directory,
    extracts the first line from each, and writes them to the output file.
    """
    try:
        # Step 1: List all `.log` files in the directory
        log_dir = Path(input_dir)
        log_files = [file for file in log_dir.glob("*.log") if file.is_file()]

        # Step 2: Sort files by modification time (newest first)
        sorted_files = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)

        # Step 3: Extract the first line from the top `count` files
        first_lines = []
        for file in sorted_files[:count]:
            with open(file, 'r') as f:
                first_line = f.readline().strip()
                first_lines.append(first_line)

        # Step 4: Write the collected first lines to the output file
        with open(output_file, 'w') as f:
            f.write("\n".join(first_lines))

        return {"message": f"Extracted first lines from {len(first_lines)} log files"}, 200

    except Exception as e:
        return {"error": str(e)}, 500
    
def extract_markdown_titles_recursive(input_dir, output_file):
    """
    Recursively extracts the first header line from each Markdown file in the input directory
    (including subdirectories) and creates an index JSON file mapping filenames to titles.
    """
    try:
        # Step 1: Find all `.md` files in the directory and subdirectories
        docs_dir = Path(input_dir)
        md_files = list(docs_dir.rglob("*.md"))  # rglob() searches recursively

        # Step 2: Extract the first header line from each file
        index = {}
        for file in md_files:
            with open(file, 'r') as f:
                for line in f:
                    if line.startswith("#"):
                        index[str(file.relative_to(docs_dir))] = line.strip("#").strip()
                        break

        # Step 3: Write the index to the output JSON file
        with open(output_file, 'w') as f:
            json.dump(index, f, indent=4)

        return {"message": f"Index created with {len(index)} entries"}, 200

    except Exception as e:
        return {"error": str(e)}, 500
