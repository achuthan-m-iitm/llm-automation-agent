# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies including tesseract and ffmpeg
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    npm \
    git && \
    rm -rf /var/lib/apt/lists/*

# Install Prettier globally using npm
RUN npm install -g prettier

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies from PyPI
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the Flask API
EXPOSE 8000

# Cleanup any existing repository directory before cloning
RUN rm -rf /app/data/repo

# Set PYTHONPATH explicitly to /app without referencing $PYTHONPATH
ENV PYTHONPATH=/app

# Command to run the Flask application
CMD ["python", "app/main.py"]
