FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose the port
EXPOSE 8000

# Set default environment variables
ENV PORT=8000
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
ENV SERVICE_NAME=dummy-app

# Run the application
CMD ["python", "app.py"]
