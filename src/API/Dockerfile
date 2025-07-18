# Use a slim Python base image for smaller image size
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port your Flask application will run on (default is 5000)
EXPOSE 5000

 CMD ["python", "main.py", "--host", "0.0.0.0"]