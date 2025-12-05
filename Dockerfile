# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your application listens on (e.g., 80 for web apps)
EXPOSE 80

# Command to run your application (adjust as needed for your framework)
CMD ["python", "app.py"]