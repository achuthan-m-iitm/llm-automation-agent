from flask import Flask, request, jsonify
import os
from datetime import datetime
from tasks.phase_a import install_uv_and_run_datagen  # Import for Task A1
from tasks.phase_a import format_file_with_prettier
from tasks.phase_a import sort_contacts,extract_recent_logs
app = Flask(__name__)
DATA_DIRECTORY = "./data"

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
        return jsonify(*format_file_with_prettier(file_path))

    # Task A3: Count Wednesdays
    if "wednesdays" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "dates.txt")
        output_file = os.path.join(DATA_DIRECTORY, "dates-wednesdays.txt")
        try:
            with open(input_file, 'r') as f:
                dates = [datetime.strptime(line.strip(), '%Y-%m-%d') for line in f]
            wednesday_count = sum(1 for date in dates if date.weekday() == 2)
            with open(output_file, 'w') as f:
                f.write(str(wednesday_count))
            return jsonify({"message": f"Wednesdays counted: {wednesday_count}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        #A4
    if "sort contacts" in task_description.lower():
        input_file = os.path.join(DATA_DIRECTORY, "contacts.json")
        output_file = os.path.join(DATA_DIRECTORY, "contacts-sorted.json")
        return jsonify(*sort_contacts(input_file, output_file))
        #A5
    if "extract recent logs" in task_description.lower():
        input_dir = os.path.join(DATA_DIRECTORY, "logs")
        output_file = os.path.join(DATA_DIRECTORY, "logs-recent.txt")
        return jsonify(*extract_recent_logs(input_dir, output_file))

    return jsonify({"error": "Task not recognized"}), 400

    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
