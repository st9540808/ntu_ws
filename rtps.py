import pyshark
import re

HOST_MAC = 'c8:7f:54:68:75:6e'


def remove_color_code(text):
  pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
  return pattern.sub('', text)


def extract_key_values(text, key):
  pattern = r"\b" + re.escape(key) + r":\s+(.*)"
  matches = re.findall(pattern, text)
  return matches


def check_substring_in_list(substring, string_list):
  for string in string_list:
    if substring in string:
      return True
  return False


def get_guid_entityid(packet):
  '''
  Returns GUID and entity id from a packet
  '''
  try:
    guid_prefix = packet.RTPS.guidPrefix
    sm_rdentityid = packet.RTPS.sm_rdentityid
    sm_wrentityid = packet.RTPS.sm_wrentityid
    return guid_prefix, sm_rdentityid, sm_wrentityid
  except AttributeError:
    # Ignore packets that don't have a GUID field
    return None, None, None


# Capture network traffic on eno2 interface
# capture = pyshark.LiveCapture(interface="eno2", bpf_filter="rtps")
# capture = pyshark.LiveCapture(interface="eno2", display_filter="rtps")
# capture = pyshark.LiveCapture(
#     interface="eno2", bpf_filter="udp", output_file='/home/st9540808/Desktop/autoware_ws/ntu_ws/rtps.pcap')
# capture = pyshark.LiveCapture(interface="eno2", display_filter="rtps")
# capture = pyshark.LiveCapture(
#     interface="eno2", bpf_filter="udp[8:4] = 0x52545053")
# capture.set_debug()
capture = pyshark.LiveRingCapture(
    interface="eno2", only_summaries=True, ring_file_size=2097152)

count = 0
for packet in capture.sniff_continuously():
  print('received packet')
  if packet.highest_layer == 'RTPS':
    count += 1
    # print(packet.frame_info.number, packet.frame_info.time_epoch)
    print(packet)
  # packet_str = remove_color_code(str(packet))

  # topic = extract_key_values(packet_str, 'topic')
  # submessage_id = extract_key_values(packet_str, 'submessageId')
  # # print(submessage_id, topic)

  # if check_substring_in_list('DATA_FRAG', submessage_id):
  #   print(submessage_id, topic)

# # Filter for RTPS data traffic
# capture.sniff(timeout=100)
# # capture.sniff(packet_count=)

# # Extract GUID field from each captured packet
# # print(capture[3])
# for packet in capture:
#   print("ss")
#   try:
#     guid_prefix = packet.RTPS.guidPrefix
#     # entity_id = packet.RTPS.writerEntityId
#     print(f"GUID: {guid_prefix}")
#   except AttributeError:
#     # Ignore packets that don't have a GUID field
#     print("Ignore")
#     continue

# capture packet in for loop
count = 0
for packet in capture.sniff_continuously():
  count += 1
  print(packet)
  # print(count)
  try:
    # get all attributes
    # print(dir(packet))

    # get packet mac address
    # print(packet.eth.src)

    # print("Just arrived:", packet)
    guid_prefix = packet.RTPS.guidPrefix

    # get entity id
    sm_rdentityid = packet.RTPS.sm_rdentityid
    sm_wrentityid = packet.RTPS.sm_wrentityid
    # param_guid_entityid = packet.RTPS.param_guid_entityid

    # pretty print several variables including guid_prefix, and all entity ids in green color
    if packet.eth.src == HOST_MAC:
      print(
          "\033[92megress  " + f"GUID: {guid_prefix}, Entity ID: {sm_rdentityid}, {sm_wrentityid}" + "\033[0m")
    else:
      # print in red color
      print(
          "\033[91mingress " + f"GUID: {guid_prefix}, Entity ID: {sm_rdentityid}, {sm_wrentityid}" + "\033[0m")
  except AttributeError:
    # Ignore packets that don't have guidPrefix field or writerEntityId field
    print("Ignore")
    continue

  # Do something with packet or print it
  # print('Just arrived:', packet)
  # print(packet.RTPS.guidPrefix)
  # print(packet.RTPS.writerEntityId)
  # print(packet.RTPS.readerEntityId)
  # print(packet.RTPS.writerSequenceNumber)
  # print(packet.RTPS.readerSequenceNumber)
  # print(packet.RTPS.count)
  # print(packet.RTPS.data)
  # print(packet.RTPS.submessageLength)
  # print(packet.RTPS.submessageId)
  # print(packet.RTP
