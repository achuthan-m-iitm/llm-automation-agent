from datetime import datetime

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
