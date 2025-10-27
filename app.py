import os
import time
import logging
import threading
import requests
from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
PORT = int(os.getenv("PORT", "8000"))
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT", 
    "http://localhost:4318"
)
SERVICE_NAME = os.getenv("SERVICE_NAME", "flask-app")
AUTO_TRACE_ENABLED = os.getenv("AUTO_TRACE_ENABLED", "true").lower() == "true"
AUTO_TRACE_INTERVAL = int(os.getenv("AUTO_TRACE_INTERVAL", "30"))  # seconds

# Configure OpenTelemetry
resource = Resource.create({
    "service.name": SERVICE_NAME,
    "service.version": "1.0.0",
})

# Set up the tracer provider
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=f"{OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces"
)

# Add span processor
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# Get tracer
tracer = trace.get_tracer(__name__)

# Create Flask app
app = Flask(__name__)

# Instrument Flask app
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

logger.info(f"Starting {SERVICE_NAME} on port {PORT}")
logger.info(f"OTLP endpoint: {OTEL_EXPORTER_OTLP_ENDPOINT}")
logger.info(f"Auto trace enabled: {AUTO_TRACE_ENABLED}")
if AUTO_TRACE_ENABLED:
    logger.info(f"Auto trace interval: {AUTO_TRACE_INTERVAL} seconds")


def auto_trace_generator():
    """Background thread that automatically generates traces by calling endpoints"""
    # Wait for Flask to start
    time.sleep(5)
    
    base_url = f"http://localhost:{PORT}"
    
    # Define endpoints to call automatically
    endpoints = [
        {"method": "GET", "path": "/", "name": "home"},
        {"method": "GET", "path": "/health", "name": "health"},
        {"method": "GET", "path": "/api/data", "name": "get_data"},
        {"method": "POST", "path": "/api/process", "name": "process_data", "json": {"auto": True, "value": random.randint(1, 100)}},
        {"method": "GET", "path": "/api/chain", "name": "chain_ops"},
    ]
    
    logger.info("Auto trace generator started")
    
    while True:
        try:
            # Randomly select an endpoint to call
            endpoint = random.choice(endpoints)
            
            with tracer.start_as_current_span("auto-trace-call") as span:
                span.set_attribute("auto.generated", True)
                span.set_attribute("target.endpoint", endpoint["path"])
                span.set_attribute("target.method", endpoint["method"])
                
                logger.info(f"Auto-generating trace for {endpoint['method']} {endpoint['path']}")
                
                try:
                    if endpoint["method"] == "GET":
                        response = requests.get(
                            f"{base_url}{endpoint['path']}", 
                            timeout=10
                        )
                    elif endpoint["method"] == "POST":
                        response = requests.post(
                            f"{base_url}{endpoint['path']}", 
                            json=endpoint.get("json", {}),
                            timeout=10
                        )
                    
                    span.set_attribute("http.status_code", response.status_code)
                    logger.info(f"Auto trace completed: {endpoint['name']} - Status {response.status_code}")
                    
                except requests.exceptions.RequestException as e:
                    span.record_exception(e)
                    logger.error(f"Auto trace failed for {endpoint['path']}: {str(e)}")
            
            # Wait before next call
            time.sleep(AUTO_TRACE_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in auto trace generator: {str(e)}")
            time.sleep(AUTO_TRACE_INTERVAL)


@app.route('/')
def home():
    """Root endpoint"""
    logger.info("Root endpoint called")
    
    with tracer.start_as_current_span("home-handler") as span:
        span.set_attribute("endpoint", "/")
        span.set_attribute("method", request.method)
        
        return jsonify({
            "message": "Welcome to Flask App",
            "service": SERVICE_NAME,
            "status": "running"
        })


@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    
    with tracer.start_as_current_span("health-check") as span:
        span.set_attribute("endpoint", "/health")
        span.set_attribute("health.status", "healthy")
        
        return jsonify({
            "status": "healthy",
            "service": SERVICE_NAME
        }), 200


@app.route('/api/data')
def get_data():
    """Simulated data endpoint with processing time"""
    logger.info("Data endpoint called")
    
    with tracer.start_as_current_span("get-data") as span:
        span.set_attribute("endpoint", "/api/data")
        
        # Simulate some processing
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        span.set_attribute("processing.time_seconds", processing_time)
        
        data = {
            "id": random.randint(1, 1000),
            "value": random.uniform(0, 100),
            "timestamp": time.time()
        }
        
        logger.info(f"Generated data: {data}")
        
        return jsonify(data)


@app.route('/api/process', methods=['POST'])
def process_data():
    """Simulated data processing endpoint"""
    logger.info("Process endpoint called")
    
    with tracer.start_as_current_span("process-data") as span:
        span.set_attribute("endpoint", "/api/process")
        span.set_attribute("method", "POST")
        
        data = request.get_json() or {}
        
        # Simulate processing with nested span
        with tracer.start_as_current_span("validate-input") as validate_span:
            validate_span.set_attribute("input.size", len(str(data)))
            logger.info(f"Validating input: {data}")
            time.sleep(0.1)
        
        with tracer.start_as_current_span("transform-data") as transform_span:
            # Simulate transformation
            processing_time = random.uniform(0.2, 0.7)
            time.sleep(processing_time)
            transform_span.set_attribute("transform.time_seconds", processing_time)
            
            result = {
                "processed": True,
                "input": data,
                "result": random.randint(100, 999),
                "processing_time": processing_time
            }
            
            logger.info(f"Processing completed: {result}")
        
        return jsonify(result)


@app.route('/api/error')
def trigger_error():
    """Endpoint that triggers an error for testing"""
    logger.error("Error endpoint called - triggering error")
    
    with tracer.start_as_current_span("error-handler") as span:
        span.set_attribute("endpoint", "/api/error")
        span.set_attribute("error.intentional", True)
        
        # Record exception in span
        try:
            raise Exception("Intentional error for testing")
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            logger.exception("Exception occurred")
            
            return jsonify({
                "error": str(e),
                "message": "This is an intentional error for testing"
            }), 500


@app.route('/api/chain')
def chain_operations():
    """Endpoint with multiple nested operations"""
    logger.info("Chain operations endpoint called")
    
    with tracer.start_as_current_span("chain-operations") as span:
        span.set_attribute("endpoint", "/api/chain")
        
        results = []
        
        for i in range(3):
            with tracer.start_as_current_span(f"operation-{i+1}") as op_span:
                op_span.set_attribute("operation.number", i+1)
                time.sleep(random.uniform(0.05, 0.15))
                
                result = {
                    "step": i+1,
                    "value": random.randint(1, 100)
                }
                results.append(result)
                
                logger.info(f"Operation {i+1} completed: {result}")
        
        return jsonify({
            "operations": results,
            "total_steps": len(results)
        })


if __name__ == '__main__':
    # Start auto trace generator in background thread if enabled
    if AUTO_TRACE_ENABLED:
        trace_thread = threading.Thread(target=auto_trace_generator, daemon=True)
        trace_thread.start()
        logger.info("Auto trace generator thread started")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
