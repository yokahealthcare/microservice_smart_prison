# Use the official Python image as the base image
FROM ubuntu:22.04

# Install software required for Python3
RUN apt update && apt install python3 python3-pip -y
# Install software required for OpenCV to work
RUN apt update && apt install ffmpeg libsm6 libxext6  -y
# Install software curl for YOLO can download video as input (if the input is URL)
RUN apt update && apt install curl -y
# Install software ping
RUN apt update && apt install inetutils-ping -y

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code to the container
COPY . .

# Command to run the FastAPI application using Uvicorn
CMD ["python3", "main.py"]
