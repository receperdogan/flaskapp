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

### Kubernetes

Deploy the Flask application to Kubernetes using the provided YAML configuration:

```bash
# Apply the Kubernetes configuration
kubectl apply -f flaskapp.yaml

# Check deployment status
kubectl get pods -n flask-app
kubectl get services -n flask-app
kubectl get ingress -n flask-app

# View logs
kubectl logs -f deployment/flask-app -n flask-app

# Port forward for local testing (if not using ingress)
kubectl port-forward service/flask-app 8000:8000 -n flask-app
```

The Kubernetes deployment includes:

- **Namespace**: `flask-app` - isolated namespace for the application
- **Deployment**: Flask application with configurable replicas
- **Service**: ClusterIP service exposing port 8000
- **Ingress**: NGINX ingress for external access at `flask-app.local`

#### Environment Variables in Kubernetes

The deployment configures the following environment variables:

- `SERVICE_NAME`: "flask-app"
- `PORT`: "8000"
- `AUTO_TRACE_ENABLED`: "true" - enables automatic trace generation
- `AUTO_TRACE_INTERVAL`: "30" - interval in seconds for auto-traces
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Configure your OTLP collector endpoint

#### Accessing the Application

1. **Via Ingress**: Add `flask-app.local` to your `/etc/hosts` file pointing to your ingress IP
2. **Via Port Forward**: Use `kubectl port-forward` as shown above
3. **Via Service**: Access directly from within the cluster

#### Customizing the Deployment

Edit `flaskapp.yaml` to modify:
- Replica count
- Resource limits/requests
- Environment variables
- Ingress hostname
- OTLP collector endpoint

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
