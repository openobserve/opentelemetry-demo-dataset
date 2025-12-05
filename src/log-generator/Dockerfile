# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-slim

WORKDIR /app

COPY src/log-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/log-generator/app.py .

ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otelcol:4317
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=log-generator,service.version=1.0.0"

CMD ["python", "app.py"]
