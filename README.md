# flask App - Python Flask with OpenTelemetry

A simple Python Flask application that generates logs and sends traces via OTLP protocol.

## Features

- **Logging**: Structured logging for all operations
- **Tracing**: OpenTelemetry traces sent via OTLP HTTP protocol
- **Multiple Endpoints**: Various endpoints to demonstrate different tracing scenarios

## Environment Variables

- `PORT`: Application port (default: 8000)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP endpoint URL (default: http://localhost:4318)
- `SERVICE_NAME`: Service name for traces (default: flask-app)

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/data` - Get simulated data with processing time
- `POST /api/process` - Process data with nested spans
- `GET /api/error` - Trigger an intentional error
- `GET /api/chain` - Chain multiple operations with nested spans

## Building and Running

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export SERVICE_NAME=flask-app
python app.py
```

### Docker

```bash
# Build the image
docker build -t flask-app:latest .

# Run the container
docker run -p 8000:8000 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
  -e SERVICE_NAME=flask-app \
  flask-app:latest
```

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Get data
curl http://localhost:8000/api/data

# Process data
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# Chain operations
curl http://localhost:8000/api/chain
```

## Traces

All HTTP requests are automatically instrumented and traced. The application sends traces to the configured OTLP endpoint using HTTP protocol on the `/v1/traces` path.

Traces include:
- HTTP request details (method, path, status code)
- Custom spans for business logic
- Processing times and attributes
- Exception recording for errors
