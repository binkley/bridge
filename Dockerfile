# Use the official Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables to prevent Python from writing .pyc and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for C++ DDS compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project configuration first to leverage Docker cache
COPY pyproject.toml .
RUN pip install --upgrade pip && pip install .

# Copy the rest of the application and the test runner
COPY . .
RUN chmod +x test.sh

# The default command runs the 90% coverage audit
CMD ["./docker-test.sh"]
