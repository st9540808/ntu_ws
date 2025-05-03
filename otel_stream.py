from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import socket
import time
import subprocess
import re


"""
Tshark command to capture RTPS traffic
"""


def execute_tshark() -> subprocess.Popen:
  # Run your command
  # process = subprocess.Popen(
  #     ['tshark', '-i', 'eno2', '-f', 'udp[8:4] = 0x52545053', '-Y', 'rtps',
  #      '--buffer-size', '1024', '-V'],
  #     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
  process = subprocess.Popen(
      ['tshark', '-i', 'eno2', '-f', 'ip', '-Y', 'rtps',
       '--buffer-size', '1024', '-V'],
      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
  return process


def check_substring_in_list(substring, string_list):
  for string in string_list:
    if substring in string:
      return True
  return False


def parse_data(data_string):
  parsed_data = {}
  lines = data_string.strip().split('\n')
  path = [parsed_data]
  for line in lines:
    # Count the leading spaces to determine the indentation level
    spaces = len(line) - len(line.lstrip())
    tabs = spaces // 4  # Convert leading spaces to equivalent tab level
    line = line.strip()
    # Go up in the dictionary hierarchy if necessary
    while len(path) > tabs + 1:
      path.pop()
    if 'submessageId' in line:
      if 'submessageId' not in path[-1]:
        path[-1]['submessageId'] = {}
      key, value = line.split(': ', 1) if ': ' in line else (line[:-1], '')
      if value not in path[-1]['submessageId']:
        path[-1]['submessageId'][value] = [{}]
      else:
        path[-1]['submessageId'][value].append({})
      path.append(path[-1]['submessageId'][value][-1])
    elif ':' in line:
      key, value = line.split(': ', 1) if ': ' in line else (line[:-1], '')
      path[-1][key] = value
    else:
      path[-1][line] = {}
      path.append(path[-1][line])
  return parsed_data


def process_section(section):
  global tracer
  # This is a placeholder. Replace this with your actual processing code.
  # print("--------------------------------------------------------------")
  # print(section)
  # print("--------------------------------------------------------------")

  packet = parse_data(section)
  # print("--------------------------------------------------------------")
  # print(packet)
  # print("--------------------------------------------------------------")

  try:
    epoch_time = packet['Epoch Time']
    frame_num = packet['Frame Number']

    guid_prefix = packet['Real-Time Publish-Subscribe Wire Protocol']['guidPrefix']

    submsg = packet['Real-Time Publish-Subscribe Wire Protocol']['submessageId']
    submsg_id = submsg.keys()

    frame_len = packet['Frame Length']

    topic = ''
    if check_substring_in_list('DATA (0x15)', submsg_id):
      topic = submsg['DATA (0x15)'][0]['[Topic Information (from Discovery)]']
    elif check_substring_in_list('DATA_FRAG (0x16)', submsg_id):
      topic = submsg['DATA_FRAG (0x16)'][0]['[Topic Information (from Discovery)]']

    if topic == '':
      return

    epoch_time = epoch_time.split(' ')[0]
    epoch_time = int(float(epoch_time) * 1e9)

    frame_len = frame_len.split(' ')[0]
    frame_len = int(frame_len)

    with tracer.start_as_current_span(topic['[topic'],
                                      start_time=epoch_time,
                                      attributes={"hostname": hostname, "frame_len": frame_len},):
      print(frame_num, epoch_time, topic['[topic'], frame_len)
  except KeyError:
    return


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

"""
Execute tshark command and process output
"""
process = execute_tshark()

# Buffer to hold the current section
buffer = []

# Process output in real time
for line in iter(process.stdout.readline, b''):
  # Decode bytes to string (if necessary)
  line = line.decode('utf-8').rstrip()

  # If the line is blank, we've reached the end of a section
  if line == '':
    # Join the buffer into a single string
    section = '\n'.join(buffer)

    # Process the section
    process_section(section)

    # Clear the buffer for the next section
    buffer = []
  else:
    # Add the line to the buffer
    buffer.append(line)

# Don't forget to check the buffer one last time in case
# the output didn't end with a blank line
if buffer:
  section = '\n'.join(buffer)
  process_section(section)

# Close the stdout stream
process.stdout.close()

# Wait for the process to terminate
process.wait()
