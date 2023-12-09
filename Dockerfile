# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the source code to the working directory
COPY . /app

# install dependencies
RUN pip install -r requirements.txt

# Run the Python script and keep the container running
CMD ["python", "-m", "http.server", "8000"]
