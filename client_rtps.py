from prometheus_client import start_http_server, Gauge
import random
import time

# Create a metric to track a random value.
g = Gauge('my_random_value', 'Description of gauge')


def process_request():
  """A dummy function that updates our gauge with a random value."""
  g.set(random.random())


if __name__ == '__main__':
  # Start up the server to expose the metrics.
  start_http_server(8090)
  # Update the metric every 5 seconds.
  while True:
    process_request()
    time.sleep(5)
