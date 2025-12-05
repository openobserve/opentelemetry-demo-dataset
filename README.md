# OpenTelemetry Demo Dataset

Production-like sample data for testing observability backends. Based on the [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo) with streamlined configuration for dual platform testing.

## What This Generates

A 16-service e-commerce application (Astronomy Shop) producing real telemetry data:

**Services:** Frontend, Cart, Checkout, Payment, Shipping, Product Catalog, Recommendation, Email, Ad Service, Currency, Fraud Detection, Accounting, Product Reviews, Quote Service, Image Provider, Load Generator

**Infrastructure:** Kafka, PostgreSQL, Redis (Valkey), LLM Service

**Telemetry Data:**
- **Logs:** 20 sources (application + infrastructure)
- **Metrics:** Host, container, application, database, cache, web server metrics
- **Traces:** 7 distributed flows (checkout, payment, recommendations, etc.)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ available memory

### Run the Demo

```bash
# Clone the repo
git clone https://github.com/openobserve/opentelemetry-demo-dataset.git
cd opentelemetry-demo-dataset

# Start all services
docker compose up -d

# Access the demo app
open http://localhost:8080
```

Data starts flowing immediately through the OpenTelemetry Collector.

## Configure for Your Backend

Edit `src/otel-collector/otelcol-config.yml` to add your observability platform:

```yaml
exporters:
  otlphttp/your-backend:
    endpoint: https://your-backend-url/api/default
    headers:
      Authorization: Basic <your-auth-token>

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [resourcedetection, memory_limiter, transform]
      exporters: [debug, otlphttp/your-backend]
    metrics:
      receivers: [docker_stats, httpcheck/frontend-proxy, hostmetrics, nginx, otlp, postgresql, redis, spanmetrics]
      processors: [resourcedetection, memory_limiter]
      exporters: [debug, otlphttp/your-backend]
    logs:
      receivers: [otlp]
      processors: [resourcedetection, memory_limiter]
      exporters: [debug, otlphttp/your-backend]
```

Add your credentials to `.env`:
```bash
YOUR_BACKEND_API_KEY=your-key-here
```

## Architecture

```
Application Services (16) → OpenTelemetry Collector → Your Backend(s)
                ↓
Infrastructure (Kafka, PostgreSQL, Redis, LLM)
```

All services are auto-instrumented using OpenTelemetry SDKs.

## Stop Services

```bash
docker compose stop
```

Restart with `docker compose start` to preserve data.

## License

Apache License 2.0
