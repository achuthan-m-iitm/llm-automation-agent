from datetime import datetime
import subprocess
import sys
import os
import requests
import json
import openai
import re
from pathlib import Path
import pytesseract
from PIL import Image
import re
import numpy as np
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import os
# Set your AIPROXY token
openai.api_key = os.environ.get("AIPROXY_TOKEN")
DATA_DIRECTORY = "./data"
# Configure the OpenAI client to use the AIPROXY server
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
def is_valid_path(path):
    """
    Checks if the given path is within the allowed directory for access.
    Also checks if the file exists and can be accessed.
    """
    data_dir_internal = os.path.abspath(DATA_DIRECTORY)  # Internal data directory
    data_dir_external = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))  # External data directory
    absolute_path = os.path.abspath(path)

    # Check if the file or directory exists
    if not os.path.exists(absolute_path):
        print(f"DEBUG: Path does not exist: {absolute_path}")
        return False

    # Allow access to paths within the internal or external data directories
    if absolute_path.startswith(data_dir_internal) or absolute_path.startswith(data_dir_external):
        return True
    else:
        print(f"DEBUG: Access denied for path {absolute_path}")
        return False

# Define possible date formats
DATE_FORMATS = [
    "%Y-%m-%d",         # 2011-06-13
    "%d-%b-%Y",         # 03-Aug-2024
    "%b %d, %Y",        # Aug 03, 2024
    "%Y/%m/%d %H:%M:%S",  # 2017/05/09 09:07:55
    "%Y/%m/%d",         # 2022/03/06
]

def parse_date(date_str):
    """Tries different formats to parse a date string."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None  # Return None if no format matched

def count_wednesdays(input_file, output_file):
    """
    Cleans the dates, standardizes formats, counts Wednesdays, and saves the cleaned data.
    """
    try:
        if not os.path.exists(input_file):
            return {"error": f"File {input_file} not found"}, 404

        # Read and clean dates
        cleaned_dates = []
        with open(input_file, "r") as f:
            for line in f:
                date_str = line.strip()
                standardized_date = parse_date(date_str)
                if standardized_date:
                    cleaned_dates.append(standardized_date)

        if not cleaned_dates:
            return {"error": "No valid dates found in the input file"}, 400

        # Count Wednesdays
        wednesday_count = sum(1 for date in cleaned_dates if datetime.strptime(date, "%Y-%m-%d").weekday() == 2)

        # Save cleaned dates for debugging
        cleaned_dates_file = "data/dates_cleaned.txt"
        with open(cleaned_dates_file, "w") as f:
            f.write("\n".join(cleaned_dates))

        # Write Wednesday count to output file
        with open(output_file, "w") as f:
            f.write(str(wednesday_count))

        return {
            "message": f"Wednesdays counted: {wednesday_count}",
            "cleaned_dates_saved_to": cleaned_dates_file
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500

def install_uv_and_run_datagen(user_email):
    try:
        if not is_valid_path(DATA_DIRECTORY):
            return {"error": "Access to the specified path is not allowed"}, 403

        os.makedirs(DATA_DIRECTORY, exist_ok=True)

        for package in ["uv", "faker"]:
            try:
                __import__(package)
            except ImportError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        script_path = os.path.join(DATA_DIRECTORY, "datagen.py")

        response = requests.get(url)
        if response.status_code == 200:
            with open(script_path, "wb") as file:
                file.write(response.content)
        else:
            return {"error": f"Failed to download datagen.py. HTTP Status: {response.status_code}"}, 500

        with open(script_path, "r") as file:
            content = file.read()

        modified_content = content.replace('"/data"', '"./data"')
        with open(script_path, "w") as file:
            file.write(modified_content)

        subprocess.check_call([sys.executable, script_path, user_email])

        return {"message": "datagen.py executed successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def format_file_with_prettier(file_path):
    try:
        if not is_valid_path(file_path):
            return {"error": "Access to the specified path is not allowed"}, 403

        prettier_check = subprocess.run(["prettier", "--version"], capture_output=True, text=True)
        if prettier_check.returncode != 0:
            subprocess.check_call(["npm", "install", "-g", "prettier"])

        subprocess.check_call(["prettier", "--write", file_path])

        return {"message": f"File {file_path} formatted successfully"}, 200

    except subprocess.CalledProcessError as e:
        return {"error": f"Prettier execution failed: {e}"}, 500
    except Exception as e:
        return {"error": str(e)}, 500

def sort_contacts(input_file, output_file):
    try:
        if not is_valid_path(input_file) or not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        with open(input_file, 'r') as f:
            contacts = json.load(f)

        sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

        with open(output_file, 'w') as f:
            json.dump(sorted_contacts, f, indent=4)

        return {"message": f"Contacts sorted and saved to {output_file}"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def extract_recent_logs(input_dir, output_file, count=10):
    try:
        if not is_valid_path(input_dir) or not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        log_dir = Path(input_dir)
        log_files = [file for file in log_dir.glob("*.log") if file.is_file()]

        sorted_files = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)

        first_lines = []
        for file in sorted_files[:count]:
            with open(file, 'r') as f:
                first_line = f.readline().strip()
                first_lines.append(first_line)

        with open(output_file, 'w') as f:
            f.write("\n".join(first_lines))

        return {"message": f"Extracted first lines from {len(first_lines)} log files"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def extract_markdown_titles_recursive(input_dir, output_file):
    try:
        if not is_valid_path(input_dir) or not is_valid_path(output_file):
            return {"error": "Access to the specified path is not allowed"}, 403

        docs_dir = Path(input_dir)
        md_files = list(docs_dir.rglob("*.md"))

        index = {}
        for file in md_files:
            with open(file, 'r') as f:
                for line in f:
                    if line.startswith("#"):
                        index[str(file.relative_to(docs_dir))] = line.strip("#").strip()
                        break

        with open(output_file, 'w') as f:
            json.dump(index, f, indent=4)

        return {"message": f"Index created with {len(index)} entries"}, 200

    except Exception as e:
        return {"error": str(e)}, 500



def extract_email_from_file(input_file, output_file):
    """
    Extracts the sender's email address from a file using an LLM.
    """
    try:
        # Ensure the AI proxy token is set
        api_token = os.environ.get("AIPROXY_TOKEN")
        if not api_token:
            return {"error": "AIPROXY_TOKEN not set"}, 500

        openai.api_key = api_token

        # Step 1: Read the content of the input file
        with open(input_file, 'r') as f:
            email_content = f.read()

        # Step 2: Use the LLM to extract the email address
        messages = [
            {"role": "system", "content": "You are an assistant that extracts only the sender's email address."},
            {"role": "user", "content": f"Extract the sender's email address from the following content:\n\n{email_content}\n\nReturn only the email address, nothing else."}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=50,
            temperature=0  # Deterministic behavior
        )

        # Extract the response content
        response_text = response['choices'][0]['message']['content'].strip()

        # Step 3: Use regex to extract only the email address
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response_text)
        if email_match:
            extracted_email = email_match.group(0)
        else:
            extracted_email = "No email address found."

        # Step 4: Write the extracted email to the output file
        with open(output_file, 'w') as f:
            f.write(extracted_email)

        return {"message": "Email address extracted successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def extract_credit_card_number(input_image, output_file):
    """
    Extracts the credit card number from an image using OCR and LLM.
    """
    try:
        # Step 1: Use OCR to extract text from the image
        text_from_image = pytesseract.image_to_string(Image.open(input_image))
        print("OCR Result:", text_from_image)  # Debugging print

        if not text_from_image.strip():
            return {"error": "No text found in the image"}, 400

        # Step 2: Use the LLM to extract the credit card number
        messages = [
            {"role": "system", "content": "You are an assistant that extracts credit card numbers from text."},
            {"role": "user", "content": f"Extract the credit card number from this text:\n\n{text_from_image}\n\nOnly return the 15 or 16-digit credit card number, without any extra text."}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=50,
            temperature=0
        )

        # Extract the AI response
        response_text = response['choices'][0]['message']['content'].strip()
        print("AI Response Text:", response_text)  # Debugging print

        # Step 3: Use regex to extract the credit card number
        card_number_match = re.search(r'\b\d{13,16}\b', response_text)

        print("Regex Match Object:", card_number_match)  # Debugging print
        if card_number_match:
            # Clean the credit card number (remove spaces or dashes)
            card_number = card_number_match.group(0).replace(" ", "").replace("-", "")
            print("Extracted Credit Card Number:", card_number)  # Debugging print
        else:
            card_number = "No valid credit card number found."

        # Step 4: Write the extracted credit card number to the output file
        print("Output file path:", output_file)  # Debugging print
        with open(output_file, 'w') as f:
            print("Writing to file:", card_number)  # Debugging print
            f.write(card_number)

        return {"message": "Credit card number extracted successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

def get_embeddings(texts):
    """
    Get embeddings for a list of texts using the supported embedding model.
    """
    response = openai.Embedding.create(
        model="text-embedding-3-small",  # Correct model
        input=texts
    )
    embeddings = [embedding['embedding'] for embedding in response['data']]
    return embeddings

def find_most_similar_comments(input_file, output_file):
    """
    Finds the most similar pair of comments using embeddings and writes to the output file.
    """
    try:
        # Step 1: Read the comments from the input file
        with open(input_file, 'r') as f:
            comments = f.readlines()

        comments = [comment.strip() for comment in comments if comment.strip()]

        if len(comments) < 2:
            return {"error": "Not enough comments to compare."}, 400

        # Step 2: Get embeddings for each comment
        embeddings = get_embeddings(comments)

        # Step 3: Calculate cosine similarity between all pairs of comments
        similarity_matrix = cosine_similarity(embeddings)

        # Step 4: Find the most similar pair (excluding diagonal)
        max_similarity = -1
        most_similar_pair = None

        for i in range(len(comments)):
            for j in range(i + 1, len(comments)):
                similarity = similarity_matrix[i][j]
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_pair = (comments[i], comments[j], similarity)

        # Step 5: Write the most similar pair to the output file
        if most_similar_pair:
            with open(output_file, 'w') as f:
                f.write(f"Comment 1: {most_similar_pair[0]}\n")
                f.write(f"Comment 2: {most_similar_pair[1]}\n")
                f.write(f"Similarity: {most_similar_pair[2]:.4f}\n")

            return {"message": "Most similar comments found and written successfully"}, 200
        else:
            return {"error": "No similar comments found."}, 500

    except Exception as e:
        return {"error": str(e)}, 500

def calculate_gold_ticket_sales(db_path, output_file):
    """
    Calculates the total sales for the "Gold" ticket type and writes the result to a file.
    """
    try:
        # Step 1: Connect to the SQLite database
        if not os.path.exists(db_path):
            return {"error": "Database file not found"}, 404

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Step 2: Query the total sales for the "Gold" ticket type
        query = """
        SELECT SUM(units * price) AS total_sales
        FROM tickets
        WHERE type = 'Gold';
        """
        cursor.execute(query)
        result = cursor.fetchone()

        # Step 3: Check the result
        if result and result[0] is not None:
            total_sales = result[0]
        else:
            total_sales = 0

        # Step 4: Write the total sales to the output file
        with open(output_file, 'w') as f:
            f.write(str(total_sales))

        # Step 5: Close the database connection
        conn.close()

        return {"message": "Gold ticket sales calculated successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500
    
