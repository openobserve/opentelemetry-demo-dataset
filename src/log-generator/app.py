#!/usr/bin/env python3
# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import time
import random
import logging
import json
from datetime import datetime
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Configure resource
resource = Resource.create({
    "service.name": "log-generator",
    "service.version": "1.0.0",
})

# Setup tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Setup metrics
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Setup logging
logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Configure logger
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Create metrics
log_counter = meter.create_counter(
    "log_generator.logs_generated",
    description="Number of logs generated",
)

error_counter = meter.create_counter(
    "log_generator.errors_generated",
    description="Number of error logs generated",
)

# Sample log patterns
LOG_PATTERNS = [
    {"level": "INFO", "message": "User login successful", "user_id": lambda: f"user_{random.randint(1000, 9999)}"},
    {"level": "INFO", "message": "API request processed", "endpoint": lambda: random.choice(["/api/users", "/api/products", "/api/orders"]), "response_time_ms": lambda: random.randint(10, 500)},
    {"level": "WARN", "message": "Slow query detected", "query_time_ms": lambda: random.randint(1000, 3000)},
    {"level": "ERROR", "message": "Database connection failed", "retry_count": lambda: random.randint(1, 5)},
    {"level": "ERROR", "message": "Payment processing failed", "error_code": lambda: random.choice(["INSUFFICIENT_FUNDS", "CARD_DECLINED", "TIMEOUT"])},
    {"level": "INFO", "message": "Cache hit", "cache_key": lambda: f"key_{random.randint(1, 100)}"},
    {"level": "WARN", "message": "Rate limit approaching", "current_rate": lambda: random.randint(80, 95), "limit": 100},
    {"level": "INFO", "message": "Order placed", "order_id": lambda: f"ORD-{random.randint(10000, 99999)}", "amount": lambda: round(random.uniform(10.0, 500.0), 2)},
]

def generate_logs():
    """Generate diverse log patterns continuously"""
    iteration = 0
    while True:
        with tracer.start_as_current_span("generate_log_batch") as span:
            iteration += 1
            pattern = random.choice(LOG_PATTERNS)

            # Build log message with dynamic values
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": pattern["message"],
            }

            # Add dynamic fields
            for key, value_func in pattern.items():
                if key not in ["level", "message"] and callable(value_func):
                    log_data[key] = value_func()

            # Log based on level
            if pattern["level"] == "INFO":
                logger.info(json.dumps(log_data))
                log_counter.add(1, {"level": "info"})
            elif pattern["level"] == "WARN":
                logger.warning(json.dumps(log_data))
                log_counter.add(1, {"level": "warn"})
            elif pattern["level"] == "ERROR":
                logger.error(json.dumps(log_data))
                log_counter.add(1, {"level": "error"})
                error_counter.add(1)

            span.set_attribute("log.level", pattern["level"])
            span.set_attribute("iteration", iteration)

        # Sleep between logs (generate a log every 2-5 seconds)
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    logger.info("Log generator service starting...")
    print("Log generator service started. Generating logs...")
    try:
        generate_logs()
    except KeyboardInterrupt:
        logger.info("Log generator service stopping...")
        print("Log generator service stopped.")
