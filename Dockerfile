# Use the official Python 3.11 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# install dependencies
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Copy the source code to the working directory
COPY . /app


# Run the Python script and keep the container running
CMD ["python", "-m", "http.server", "8000"]
