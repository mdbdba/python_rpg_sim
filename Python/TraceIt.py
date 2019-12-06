from opencensus.trace import samplers
from opencensus.trace.tracer import Tracer
from opencensus.ext.jaeger.trace_exporter import JaegerExporter


class TraceIt(object):
    def __init__(self, trace_name):
        sampler = samplers.AlwaysOnSampler()

        je = JaegerExporter(
            service_name=trace_name,
            host_name="localhost",
            agent_port=6831,
            endpoint="/api/traces")

        self.tracer = Tracer(sampler=sampler, exporter=je)
