FROM python:3.9

COPY --from=otel/opentelemetry-collector-contrib:0.26.0 /otelcontribcol /go/bin/otelcol

WORKDIR /app

ENV PYTHONPATH .

RUN apt-get update && \
    apt-get install --no-install-recommends -y supervisor && \
    apt-get clean

COPY docker-config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker-config/otel_config.yaml /etc/otel/config.yaml

COPY opentelemetry-opentracing-shim opentelemetry-opentracing-shim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src src

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
