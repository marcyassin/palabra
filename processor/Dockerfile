# Use official Python 3.11 image as base
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose a port if you plan to serve HTTP requests (optional)
# EXPOSE 8000

# Set environment variables (optional, can also use .env)
ENV PYTHONUNBUFFERED=1

# Command to run the processor
CMD ["python", "main.py"]
