# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build dependencies (if any) and then requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend ./backend

# Expose FastAPI default port
EXPOSE 8000

# Command to run the server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
