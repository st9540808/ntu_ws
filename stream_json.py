import subprocess
import json
import re
import concurrent.futures
import json_stream


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


def process_dictionary(dictionary):
  # Process the dictionary as needed
  print(dictionary)


def process_json_object(obj):
  # This is a placeholder. Replace this with your actual processing code.
  print("Processing JSON object:")
  print(obj)


# Run your command
process = execute_tshark()

while True:
  data = json_stream.load(process.stdout)
  print(data)

# # Accumulate lines until a complete JSON object is formed
# json_lines = []
# for line in process.stdout:
#   # Strip any leading/trailing whitespace
#   line = line.strip()

#   # Accumulate lines until a complete JSON object is formed
#   json_lines.append(line)

#   # Check if the lines accumulated so far form a complete JSON object
#   try:
#     dictionaries = json.loads(''.join(line.decode('utf-8')
#                               for line in json_lines))
#     for dictionary in dictionaries:
#       process_dictionary(dictionary)
#     json_lines = []  # Reset the accumulated lines
#   except json.JSONDecodeError:
#     continue

# # Wait for the subprocess to finish
# process.wait()
