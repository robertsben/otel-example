# otel-example

Example comparing the linking between `follows_from` referenced traces
between Jaeger and opentelemetry, using the opentracing shim.

## Running

To run the services (run once):

    $ docker-compose up -d rabbitmq elastic_apm jaeger kibana

to run the app:

    $ docker-compose up --build publisher subscriber


The publisher will trace a RabbitMQ message publish, inject the trace
into the message headers, and the subscriber will read the message, extract
the trace, and use the [`follows_from`](https://opentracing.io/specification/#references-between-spans)
relationship to connect the two.

You can see the traces in [Jaeger](http://localhost:16686/search), and for
opentelemetry also in [Elastic APM](http://localhost:5601/app/apm).

The traces will be under app name `otel.publisher` and `otel.subscriber`.

## Opentelemetry vs Opentracing

To run the app using Jaeger, set the environment variable `JAEGER_MODE: 1` in the 
publisher and subscriber apps in the [docker-compose.yml](docker-compose.yml).

To run without, comment out the `JAEGER_MODE` variable (or set it to 0).

You can compare how the traces are linked in the Jaeger UI.
