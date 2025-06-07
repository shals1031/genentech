# Use the official Python 3.13 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads
RUN mkdir -p /app/flask_session

# Set environment variables
ENV PORT=8080
# Make sure the app knows it's running in Google Cloud
ENV GOOGLE_CLOUD_PROJECT=poc-projects-462113


# Make the container listen on port 8080
EXPOSE 8080

# Command to run the application using Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 wsgi:app