# Use an official Python image with a specific platform
FROM --platform=linux/amd64 python:3.10-alpine

# Install build dependencies33
RUN apk add --no-cache gcc musl-dev mariadb-dev

# Create a virtual environment
RUN python3 -m venv /venv

# Install Python packages into the virtual environment
RUN /venv/bin/pip install flask mysql-connector-python

# Copy the Flask app into the container
COPY app.py /app/app.py
COPY cert.pem /app/cert.pem
COPY key.pem /app/key.pem

# Set the working directory
WORKDIR /app

# Expose port 5001 for Flask
EXPOSE 443

# Start the Flask app
CMD ["/venv/bin/python3", "app.py"]

