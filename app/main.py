from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)
DATA_DIRECTORY = "./data"

@app.route('/run', methods=['POST'])
def run_task():
    task_description = request.args.get('task', '')
    if not task_description:
        return jsonify({"error": "Task description missing"}), 400

    # Check if the task is "Count Wednesdays"
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

    return jsonify({"error": "Task not recognized"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
