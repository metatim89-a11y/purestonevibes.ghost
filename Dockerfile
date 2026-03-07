# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirement first for faster caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Ensure the database file is writable if it exists
RUN touch inquiries.db && chmod 666 inquiries.db

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "8000"]
