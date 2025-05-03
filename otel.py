from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import socket
import time

# Set the tracer provider
trace.set_tracer_provider(TracerProvider(
    resource=Resource.create({
        "service.name": "dds.traffic"
    })
))

# Create an OTLP exporter
exporter = OTLPSpanExporter(
    # replace with your collector endpoint
    endpoint="http://192.168.50.214:5555",
    # endpoint="http://localhost:4317",
    insecure=True,
)

# Add the exporter to a span processor
span_processor = BatchSpanProcessor(exporter)

# Add the span processor to the tracer provider
trace.get_tracer_provider().add_span_processor(span_processor)

# Get the hostname of the machine
hostname = socket.gethostname()
print(hostname)

# Get a tracer
tracer = trace.get_tracer("network-tracing")

for i in range(10):
  # Create a span, with the hostname as an attribute
  with tracer.start_as_current_span("foo",
                                    start_time=1684000000000000000,
                                    attributes={"hostname": hostname},):
    print(i)

  time.sleep(0.1)
