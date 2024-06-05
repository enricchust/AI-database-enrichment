# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Run Streamlit when the container launches
CMD ["streamlit", "run", "src/main.py", "--server.port=8080", "--server.enableCORS=false"]
