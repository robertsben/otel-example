# otel-example

Example running opentelemetry tracing exporting to
elastic APM and jaeger.

Used to compare opentracing shim and opentelemetry sdk.

## Running

To run the services (run once):

    $ docker-compose up -d elastic_apm jaeger

to run the app:

    $ docker-compose up --build app


The app will emit some traces, including some waits and an 
error.

You can see the traces in [Jaeger](http://localhost:16686/search)
and [Elastic APM](http://localhost:5601/app/apm).

The traces will be under app name `otel_test_app`.

## Opentelemetry vs Opentracing

To run the app using [`opentracing`](https://github.com/opentracing/opentracing-python)
and the [`opentelemetry-opentracing-shim`](https://github.com/open-telemetry/opentelemetry-python/tree/main/shim/opentelemetry-opentracing-shim)
just run the app as above. Look for the operation/transaction `opentracing_main`.

To run the app using 
[`opentelemetry-sdk`](https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-sdk)
comment out (or set to 0) the environment variable `OPENTRACING_MODE`
in [docker-compose.yml](docker-compose.yml). Run the app again, and look for
the operation/transaction `otel_main`.
