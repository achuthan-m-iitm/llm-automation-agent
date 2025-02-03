from flask import Flask, request, jsonify
import os
from datetime import datetime
from tasks.phase_a import (
    count_wednesdays,
    install_uv_and_run_datagen,
    format_file_with_prettier,
    extract_credit_card_number,
    find_most_similar_comments,
    calculate_gold_ticket_sales,
    sort_contacts,
    extract_recent_logs,
    extract_markdown_titles_recursive,
    extract_email_from_file,

    
)
from tasks.phase_b import fetch_api_data,clone_and_commit,run_sql_query,extract_data_from_website,compress_or_resize_image,transcribe_audio,convert_markdown_to_html,filter_csv_data

app = Flask(__name__)
DATA_DIRECTORY = os.path.abspath("./data")

def is_valid_path(path):
    data_dir = os.path.abspath(DATA_DIRECTORY)
    absolute_path = os.path.abspath(path)
    print(f"DEBUG: Checking path - {absolute_path} starts with {data_dir}")  # Log for debugging
    return absolute_path.startswith(data_dir)


@app.route('/run', methods=['POST'])
def run_task():
    task_description = request.args.get('task', '')
    print(f"Received task description: {task_description}")  # Debugging line
    if not task_description:
        return jsonify({"error": "Task description missing"}), 400

    # Task A1: Install 'uv' and run 'datagen.py'
    if "install uv and run datagen" in task_description.lower():
        user_email = "22f3002867@ds.study.iitm.ac.in"
        return jsonify(*install_uv_and_run_datagen(user_email))

    # Task A2: Format file with Prettier
    if "format file with prettier" in task_description.lower():
        file_path = os.path.join(DATA_DIRECTORY, "format.md")
        if not is_valid_path(file_path):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*format_file_with_prettier(file_path))

    
    # Task A3: Count Wednesdays
    if "wednesdays" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "dates.txt")
        output_file = os.path.join(DATA_DIRECTORY, "dates-wednesdays.txt")

        if not is_valid_path(input_file) or not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403

        return jsonify(*count_wednesdays(input_file, output_file))


    # Task A4: Sort contacts
    if "sort contacts" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "contacts.json")
        output_file = os.path.join(DATA_DIRECTORY, "contacts-sorted.json")
        if not is_valid_path(input_file) or not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*sort_contacts(input_file, output_file))

    # Task A5: Extract recent logs
    if "extract recent logs" in task_description.lower():
        input_dir = os.path.join(DATA_DIRECTORY, "logs")
        output_file = os.path.join(DATA_DIRECTORY, "logs-recent.txt")
        if not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*extract_recent_logs(input_dir, output_file))

    # Task A6: Extract markdown titles
    if "extract markdown titles" in task_description.lower():
        input_dir = os.path.join(DATA_DIRECTORY, "docs")
        output_file = os.path.join(DATA_DIRECTORY, "docs/index.json")
        if not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*extract_markdown_titles_recursive(input_dir, output_file))

    # Task A7: Extract email
    if "extract email" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "email.txt")
        output_file = os.path.join(DATA_DIRECTORY, "email-sender.txt")
        if not is_valid_path(input_file) or not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*extract_email_from_file(input_file, output_file))

    # Task A8: Extract credit card
    if "extract credit card" in task_description.lower():
        input_image = os.path.join(DATA_DIRECTORY, "credit_card.png")
        output_file = os.path.join(DATA_DIRECTORY, "credit-card.txt")
        if not is_valid_path(input_image) or not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*extract_credit_card_number(input_image, output_file))

    # Task A9: Find most similar comments
    if "comments similar" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "comments.txt")
        output_file = os.path.join(DATA_DIRECTORY, "comments-similar.txt")
        if not is_valid_path(input_file) or not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*find_most_similar_comments(input_file, output_file))

    # Task A10: Calculate gold ticket sales
    if "gold ticket sales" in task_description.lower():
        db_path = os.path.join(DATA_DIRECTORY, "ticket-sales.db")
        output_file = os.path.join(DATA_DIRECTORY, "ticket-sales-gold.txt")
        if not is_valid_path(db_path) or not is_valid_path(output_file):
            return jsonify({"error": "Access to the specified path is not allowed"}), 403
        return jsonify(*calculate_gold_ticket_sales(db_path, output_file))
    
    # Task B3: Fetch data from an API
    if "fetch api data" in task_description:
        api_url = "https://jsonplaceholder.typicode.com/todos"  # Example API URL
        output_file = os.path.join(DATA_DIRECTORY, "api-data.json")
        return jsonify(*fetch_api_data(api_url, output_file))

    if "clone repo" in task_description.lower():
        repo_url = request.args.get('repo_url', '')
        file_name = request.args.get('file_name', 'README.md')
        commit_message = request.args.get('commit_message', 'Automated commit')
        return jsonify(*clone_and_commit(repo_url, file_name, commit_message))
    
    if "run sql query" in task_description.lower():
        db_path = os.path.join(DATA_DIRECTORY, "database.db")
        query = request.args.get('query', '')
        output_file = os.path.join(DATA_DIRECTORY, "query_results.txt")

        print(f"DEBUG: Received SQL request - Query: {query}, DB Path: {db_path}")

        return jsonify(*run_sql_query(db_path, query, output_file))
    
     # Task B6: Extract Data from a Website
    if "extract data from website" in task_description.lower():
        url = request.args.get('url', '')
        output_file = os.path.join(DATA_DIRECTORY, "website_data.json")
        return jsonify(*extract_data_from_website(url, output_file))

    # Task B7: Compress or Resize an Image
    if "compress or resize image" in task_description.lower():
        input_image = os.path.join(DATA_DIRECTORY, "input_image.jpg")
        output_image = os.path.join(DATA_DIRECTORY, "output_image.jpg")
        width = int(request.args.get('width', 0)) or None
        height = int(request.args.get('height', 0)) or None
        quality = int(request.args.get('quality', 85))
        return jsonify(*compress_or_resize_image(input_image, output_image, width, height, quality))
    
    # Task B8: Transcribe Audio from an MP3 File
    if "transcribe audio" in task_description.lower():
        input_audio = os.path.join(DATA_DIRECTORY, "input_audio.mp3")
        output_file = os.path.join(DATA_DIRECTORY, "audio_transcription.txt")
        return jsonify(*transcribe_audio(input_audio, output_file))
    
    if "convert markdown" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "docs/sample.md")
        output_file = os.path.join(DATA_DIRECTORY, "docs/sample.html")
        return jsonify(*convert_markdown_to_html(input_file, output_file))
    
    if "filter csv" in task_description.lower():
        column_name = request.args.get('column', '')
        filter_value = request.args.get('value', '')
        input_file = os.path.join(DATA_DIRECTORY, "sample.csv")

        if not column_name or not filter_value:
            return jsonify({"error": "Missing column or value parameters"}), 400
        return jsonify(*filter_csv_data(input_file, column_name, filter_value))

    return jsonify({"error": "Task not recognized"}), 400

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
