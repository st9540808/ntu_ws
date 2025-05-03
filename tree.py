import json
from functools import reduce
from collections import defaultdict


def check_substring_in_list(substring, string_list):
  for string in string_list:
    if substring in string:
      return True
  return False


def parse_indented_data(data_string):
  lines = data_string.split('\n')
  stack = []
  root = {}
  submessage_list = []
  for line in lines:
    indent_level = len(line) - len(line.lstrip())
    while len(stack) > indent_level:
      stack.pop()
    line_data = line.strip()
    if line_data:
      key_value = line_data.split(':', 1)
      if len(key_value) == 2:
        key, value = key_value
        key, value = key.strip(), value.strip()
        current_level = root if not stack else stack[-1][1]
        current_level[key] = value
      else:
        key = line_data
        if key == "submessageId":
          new_dict = {}
          submessage_list.append(new_dict)
          stack.append((key, new_dict))
        else:
          new_dict = {}
          if stack:
            stack[-1][1][key] = new_dict
          else:
            root[key] = new_dict
          stack.append((key, new_dict))
  root['submessageId'] = submessage_list
  return root


def get_by_path(root, items):
  """Get a dictionary item by path."""
  return reduce(lambda d, key: d[key], items, root)


def set_by_path(root, items, value):
  """Set a dictionary item by path."""
  get_by_path(root, items[:-1])[items[-1]] = value


def convert_text_to_json(data_string):
  lines = data_string.strip().split('\n')

  root = {}
  path = []

  for line in lines:
    depth = line.count('\t')
    key = line.strip()

    if ': ' in key:
      key, value = key.split(': ', 1)
      path = path[:depth] + [key]
      if key not in get_by_path(root, path[:-1]):
        set_by_path(root, path, {})
      set_by_path(root, path, {"value": value})
    else:
      path = path[:depth] + [key]
      if key not in get_by_path(root, path[:-1]):
        set_by_path(root, path, {})
      if key == 'submessageId':
        submessages = get_by_path(root, path[:-1]).get(key, [])
        submessages.append({})
        get_by_path(root, path[:-1])[key] = submessages
        path.append(len(submessages) - 1)
  return json.dumps(root, indent=4)


def parse_nested_data(data_string):
  def nested_dict():
    return defaultdict(nested_dict)
  # Create a stack to track the current level of nesting.
  stack = [nested_dict()]

  for line in data_string.split('\n'):
    if line.strip():
        # Count the number of leading tabs to determine the level of indentation.
      level = line.count('\t')

      # Remove leading tabs and split the line into key and value.
      key, *value = line.lstrip('\t').split(':')

      # Join value parts split by ':' back together.
      value = ':'.join(value).strip()

      # If the key is 'submessageId', append a new dictionary to its list.
      if key == 'submessageId':
        if key not in stack[level-1]:
          stack[level-1][key] = [nested_dict()]
        else:
          stack[level-1][key].append(nested_dict())

      # If the key is at a deeper level of indentation than the current level,
      # push a new dictionary onto the stack.
      if level >= len(stack):
        stack.append(nested_dict())
      stack[level][key] = value

      # If the key is at a shallower level of indentation than the current level,
      # pop dictionaries off the stack until we reach the correct level.
      while level < len(stack) - 1:
        stack.pop()

  return stack[0]


data_string1 = """
Frame 138: 170 bytes on wire (1360 bits), 170 bytes captured (1360 bits) on interface eno2, id 0
\tInterface id: 0 (eno2)
\t\tInterface name: eno2
\tEncapsulation type: Ethernet (1)
\tArrival Time: May 17, 2023 20:59:21.594738254 CST
\t[Time shift for this packet: 0.000000000 seconds]
\tEpoch Time: 1684328361.594738254 seconds
\t[Time delta from previous captured frame: 0.000000072 seconds]
\t[Time delta from previous displayed frame: 0.000000072 seconds]
\t[Time since reference or first frame: 2.343364020 seconds]
\tFrame Number: 138
\tFrame Length: 170 bytes (1360 bits)
\tCapture Length: 170 bytes (1360 bits)
\t[Frame is marked: False]
\t[Frame is ignored: False]
\t[Protocols in frame: eth:ethertype:vlan:ethertype:ip:icmp:ip:udp:rtps]
Ethernet II, Src: Shenzhen_05:03:23 (88:c9:b3:b5:03:23), Dst: c8:7f:54:68:75:6e (c8:7f:54:68:75:6e)
\tDestination: c8:7f:54:68:75:6e (c8:7f:54:68:75:6e)
\t\tAddress: c8:7f:54:68:75:6e (c8:7f:54:68:75:6e)
\t\t.... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
\t\t.... ...0 .... .... .... .... = IG bit: Individual address (unicast)
\tSource: Shenzhen_05:03:23 (88:c9:b3:b5:03:23)
\t\tAddress: Shenzhen_05:03:23 (88:c9:b3:b5:03:23)
\t\t.... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
\t\t.... ...0 .... .... .... .... = IG bit: Individual address (unicast)
\tType: 802.1Q Virtual LAN (0x8100)
802.1Q Virtual LAN, PRI: 0, DEI: 0, ID: 1
\t000. .... .... .... = Priority: Best Effort (default) (0)
\t...0 .... .... .... = DEI: Ineligible
\t.... 0000 0000 0001 = ID: 1
\tType: IPv4 (0x0800)
Internet Protocol Version 4, Src: 192.168.10.2, Dst: 192.168.10.3
\t0100 .... = Version: 4
\t.... 0101 = Header Length: 20 bytes (5)
\tDifferentiated Services Field: 0xc0 (DSCP: CS6, ECN: Not-ECT)
\t\t1100 00.. = Differentiated Services Codepoint: Class Selector 6 (48)
\t\t.... ..00 = Explicit Congestion Notification: Not ECN-Capable Transport (0)
\tTotal Length: 152
\tIdentification: 0x99ca (39370)
\tFlags: 0x00
\t\t0... .... = Reserved bit: Not set
\t\t.0.. .... = Don't fragment: Not set
\t\t..0. .... = More fragments: Not set
\t...0 0000 0000 0000 = Fragment Offset: 0
\tTime to Live: 64
\tProtocol: ICMP (1)
\tHeader Checksum: 0x4a85 [validation disabled]
\t[Header checksum status: Unverified]
\tSource Address: 192.168.10.2
\tDestination Address: 192.168.10.3
Internet Control Message Protocol
\tType: 3 (Destination unreachable)
\tCode: 3 (Port unreachable)
\tChecksum: 0x92cc [correct]
\t[Checksum Status: Good]
\tUnused: 00000000
\tInternet Protocol Version 4, Src: 192.168.10.3, Dst: 192.168.10.2
\t\t0100 .... = Version: 4
\t\t.... 0101 = Header Length: 20 bytes (5)
\t\tDifferentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)
\t\t\t0000 00.. = Differentiated Services Codepoint: Default (0)
\t\t\t.... ..00 = Explicit Congestion Notification: Not ECN-Capable Transport (0)
\t\tTotal Length: 124
\t\tIdentification: 0x14a9 (5289)
\t\tFlags: 0x40, Don't fragment
\t\t\t0... .... = Reserved bit: Not set
\t\t\t.1.. .... = Don't fragment: Set
\t\t\t..0. .... = More fragments: Not set
\t\t...0 0000 0000 0000 = Fragment Offset: 0
\t\tTime to Live: 64
\t\tProtocol: UDP (17)
\t\tHeader Checksum: 0x9072 [validation disabled]
\t\t[Header checksum status: Unverified]
\t\tSource Address: 192.168.10.3
\t\tDestination Address: 192.168.10.2
\tUser Datagram Protocol, Src Port: 60947, Dst Port: 46450
\t\tSource Port: 60947
\t\tDestination Port: 46450
\t\tLength: 104
\t\tChecksum: 0x743e [unverified]
\t\t[Checksum Status: Unverified]
\t\t[Stream index: 2]
\t\tUDP payload (96 bytes)
Real-Time Publish-Subscribe Wire Protocol
\tMagic: RTPS
\tProtocol version: 2.1
\t\tmajor: 2
\t\tminor: 1
\tvendorId: 01.16 (Eclipse Foundation - Cyclone DDS)
\tguidPrefix: 0110b4b424a84b62cd34867d
\t\thostId: 0x0110b4b4
\t\tappId: 0x24a84b62
\t\tinstanceId: 0xcd34867d
\tDefault port mapping: domainId=156, participantIdx=20, nature=UNICAST_METATRAFFIC
\t\t[domain_id: 156]
\t\t[participant_idx: 20]
\t\t[traffic_nature: UNICAST_METATRAFFIC (0)]
\tsubmessageId: INFO_TS (0x09)
\t\tFlags: 0x01, Endianness bit
\t\t\t0... .... = Reserved: Not set
\t\t\t.0.. .... = Reserved: Not set
\t\t\t..0. .... = Reserved: Not set
\t\t\t...0 .... = Reserved: Not set
\t\t\t.... 0... = Reserved: Not set
\t\t\t.... .0.. = Reserved: Not set
\t\t\t.... ..0. = Timestamp flag: Not set
\t\t\t.... ...1 = Endianness bit: Set
\t\toctetsToNextHeader: 8
\t\tTimestamp: May 17, 2023 12:59:21.594598889 UTC
\tsubmessageId: DATA (0x15)
\t\tFlags: 0x0b, Serialized Key, Inline QoS, Endianness bit
\t\t\t0... .... = Reserved: Not set
\t\t\t.0.. .... = Reserved: Not set
\t\t\t..0. .... = Reserved: Not set
\t\t\t...0 .... = Reserved: Not set
\t\t\t.... 1... = Serialized Key: Set
\t\t\t.... .0.. = Data present: Not set
\t\t\t.... ..1. = Inline QoS: Set
\t\t\t.... ...1 = Endianness bit: Set
\t\toctetsToNextHeader: 60
\t\t0000 0000 0000 0000 = Extra flags: 0x0000
\t\tOctets to inline QoS: 16
\t\treaderEntityId: ENTITYID_UNKNOWN (0x00000000)
\t\t\treaderEntityKey: 0x000000
\t\t\treaderEntityKind: Application-defined unknown kind (0x00)
\t\twriterEntityId: ENTITYID_BUILTIN_SUBSCRIPTIONS_WRITER (0x000004c2)
\t\t\twriterEntityKey: 0x000004
\t\t\twriterEntityKind: Built-in writer (with key) (0xc2)
\t\twriterSeqNumber: 9
\t\tinlineQos:
\t\t\tPID_STATUS_INFO
\t\t\t\tparameterId: PID_STATUS_INFO (0x0071)
\t\t\t\tparameterLength: 4
\t\t\t\tFlags: 0x00000003, Unregistered, Disposed
\t\t\t\t\t0... .... = Reserved: Not set
\t\t\t\t\t.0.. .... = Reserved: Not set
\t\t\t\t\t..0. .... = Reserved: Not set
\t\t\t\t\t...0 .... = Reserved: Not set
\t\t\t\t\t.... 0... = Reserved: Not set
\t\t\t\t\t.... .0.. = Reserved: Not set
\t\t\t\t\t.... ..1. = Unregistered: Set
\t\t\t\t\t.... ...1 = Disposed: Set
\t\t\tPID_SENTINEL
\t\t\t\tparameterId: PID_SENTINEL (0x0001)
\t\tserializedKey
\t\t\tencapsulation kind: PL_CDR_LE (0x0003)
\t\t\tencapsulation options: 0x0000
\t\t\tserializedData:
\t\t\t\tPID_ENDPOINT_GUID
\t\t\t\t\tparameterId: PID_ENDPOINT_GUID (0x005a)
\t\t\t\t\tparameterLength: 16
\t\t\t\t\tEndpoint GUID: 0110b4b4 24a84b62 cd34867d 00001304
\t\t\t\t\t\thostId: 0x0110b4b4
\t\t\t\t\t\tappId: 0x24a84b62
\t\t\t\t\t\tinstanceId: 0xcd34867d
\t\t\t\t\t\tentityId: Unknown (0x00001304)
\t\t\t\t\t\t\tentityKey: 0x000013
\t\t\t\t\t\t\tentityKind: Application-defined reader (no key) (0x04)
\t\t\tPID_SENTINEL
\t\t\t\tparameterId: PID_SENTINEL (0x0001)
"""

data_string = """
Frame 5: 382 bytes on wire (3056 bits), 382 bytes captured (3056 bits) on interface eno2, id 0
\tInterface id: 0 (eno2)
\t\tInterface name: eno2
\tEncapsulation type: Ethernet (1)
\tArrival Time: May 17, 2023 21:25:33.649932219 CST
\t[Time shift for this packet: 0.000000000 seconds]
\tEpoch Time: 1684329933.649932219 seconds
\t[Time delta from previous captured frame: 0.001276625 seconds]
\t[Time delta from previous displayed frame: 0.001276625 seconds]
\t[Time since reference or first frame: 0.101464962 seconds]
\tFrame Number: 5
\tFrame Length: 382 bytes (3056 bits)
\tCapture Length: 382 bytes (3056 bits)
\t[Frame is marked: False]
\t[Frame is ignored: False]
\t[Protocols in frame: eth:ethertype:vlan:ethertype:ip:udp:rtps]
Ethernet II, Src: Shenzhen_05:03:23 (88:c9:b3:b5:03:23), Dst: IPv4mcast_7f:00:01 (01:00:5e:7f:00:01)
\tDestination: IPv4mcast_7f:00:01 (01:00:5e:7f:00:01)
\t\tAddress: IPv4mcast_7f:00:01 (01:00:5e:7f:00:01)
\t\t.... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
\t\t.... ...1 .... .... .... .... = IG bit: Group address (multicast/broadcast)
\tSource: Shenzhen_05:03:23 (88:c9:b3:b5:03:23)
\t\tAddress: Shenzhen_05:03:23 (88:c9:b3:b5:03:23)
\t\t.... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
\t\t.... ...0 .... .... .... .... = IG bit: Individual address (unicast)
\tType: 802.1Q Virtual LAN (0x8100)
802.1Q Virtual LAN, PRI: 0, DEI: 0, ID: 1
\t000. .... .... .... = Priority: Best Effort (default) (0)
\t...0 .... .... .... = DEI: Ineligible
\t.... 0000 0000 0001 = ID: 1
\tType: IPv4 (0x0800)
Internet Protocol Version 4, Src: 192.168.10.2, Dst: 239.255.0.1
\t0100 .... = Version: 4
\t.... 0101 = Header Length: 20 bytes (5)
\tDifferentiated Services Field: 0x00 (DSCP: CS0, ECN: Not-ECT)
\t\t0000 00.. = Differentiated Services Codepoint: Default (0)
\t\t.... ..00 = Explicit Congestion Notification: Not ECN-Capable Transport (0)
\tTotal Length: 364
\tIdentification: 0x1f90 (8080)
\tFlags: 0x40, Don't fragment
\t\t0... .... = Reserved bit: Not set
\t\t.1.. .... = Don't fragment: Set
\t\t..0. .... = More fragments: Not set
\t...0 0000 0000 0000 = Fragment Offset: 0
\tTime to Live: 32
\tProtocol: UDP (17)
\tHeader Checksum: 0x7f46 [validation disabled]
\t[Header checksum status: Unverified]
\tSource Address: 192.168.10.2
\tDestination Address: 239.255.0.1
User Datagram Protocol, Src Port: 37593, Dst Port: 7400
\tSource Port: 37593
\tDestination Port: 7400
\tLength: 344
\tChecksum: 0xc740 [unverified]
\t[Checksum Status: Unverified]
\t[Stream index: 0]
\t[Timestamps]
\t\t[Time since first frame: 0.101464962 seconds]
\t\t[Time since previous frame: 0.001276625 seconds]
\tUDP payload (336 bytes)
Real-Time Publish-Subscribe Wire Protocol
\tMagic: RTPS
\tProtocol version: 2.1
\t\tmajor: 2
\t\tminor: 1
\tvendorId: 01.16 (Eclipse Foundation - Cyclone DDS)
\tguidPrefix: 01109c1896dc23769b422bd9
\t\thostId: 0x01109c18
\t\tappId: 0x96dc2376
\t\tinstanceId: 0x9b422bd9
\tDefault port mapping: MULTICAST_METATRAFFIC, domainId=0
\t\t[domain_id: 0]
\t\t[traffic_nature: MULTICAST_METATRAFFIC (2)]
\tsubmessageId: INFO_TS (0x09)
\t\tFlags: 0x01, Endianness bit
\t\t\t0... .... = Reserved: Not set
\t\t\t.0.. .... = Reserved: Not set
\t\t\t..0. .... = Reserved: Not set
\t\t\t...0 .... = Reserved: Not set
\t\t\t.... 0... = Reserved: Not set
\t\t\t.... .0.. = Reserved: Not set
\t\t\t.... ..0. = Timestamp flag: Not set
\t\t\t.... ...1 = Endianness bit: Set
\t\toctetsToNextHeader: 8
\t\tTimestamp: May 17, 2023 13:25:33.643197206 UTC
\tsubmessageId: DATA (0x15)
\t\tFlags: 0x05, Data present, Endianness bit
\t\t\t0... .... = Reserved: Not set
\t\t\t.0.. .... = Reserved: Not set
\t\t\t..0. .... = Reserved: Not set
\t\t\t...0 .... = Reserved: Not set
\t\t\t.... 0... = Serialized Key: Not set
\t\t\t.... .1.. = Data present: Set
\t\t\t.... ..0. = Inline QoS: Not set
\t\t\t.... ...1 = Endianness bit: Set
\t\toctetsToNextHeader: 300
\t\t0000 0000 0000 0000 = Extra flags: 0x0000
\t\tOctets to inline QoS: 16
\t\treaderEntityId: ENTITYID_UNKNOWN (0x00000000)
\t\t\treaderEntityKey: 0x000000
\t\t\treaderEntityKind: Application-defined unknown kind (0x00)
\t\twriterEntityId: ENTITYID_BUILTIN_PARTICIPANT_WRITER (0x000100c2)
\t\t\twriterEntityKey: 0x000100
\t\t\twriterEntityKind: Built-in writer (with key) (0xc2)
\t\twriterSeqNumber: 1
\t\tserializedData
\t\t\tencapsulation kind: PL_CDR_LE (0x0003)
\t\t\tencapsulation options: 0x0000
\t\t\tserializedData:
\t\t\t\tPID_USER_DATA
\t\t\t\t\tparameterId: PID_USER_DATA (0x002c)
\t\t\t\t\tparameterLength: 16
\t\t\t\t\tsequenceSize: 10 octets
\t\t\t\t\tuserData: 656e636c6176653d2f3b
\t\t\t\tPID_PROTOCOL_VERSION
\t\t\t\t\tparameterId: PID_PROTOCOL_VERSION (0x0015)
\t\t\t\t\tparameterLength: 4
\t\t\t\t\tProtocol version: 2.1
\t\t\t\t\t\tmajor: 2
\t\t\t\t\t\tminor: 1
\t\t\t\tPID_VENDOR_ID
\t\t\t\t\tparameterId: PID_VENDOR_ID (0x0016)
\t\t\t\t\tparameterLength: 4
\t\t\t\t\tvendorId: 01.16 (Eclipse Foundation - Cyclone DDS)
\t\t\t\tPID_PARTICIPANT_LEASE_DURATION
\t\t\t\t\tparameterId: PID_PARTICIPANT_LEASE_DURATION (0x0002)
\t\t\t\t\tparameterLength: 8
\t\t\t\t\tlease_duration: 10.000000 sec (10s + 0x00000000)
\t\t\t\t\t\tseconds: 10
\t\t\t\t\t\tfraction: 0
\t\t\t\tPID_PARTICIPANT_GUID
\t\t\t\t\tparameterId: PID_PARTICIPANT_GUID (0x0050)
\t\t\t\t\tparameterLength: 16
\t\t\t\t\tParticipant GUID: 01109c18 96dc2376 9b422bd9 000001c1
\t\t\t\t\t\thostId: 0x01109c18
\t\t\t\t\t\tappId: 0x96dc2376
\t\t\t\t\t\tinstanceId: 0x9b422bd9
\t\t\t\t\t\tentityId: ENTITYID_PARTICIPANT (0x000001c1)
\t\t\t\t\t\t\tentityKey: 0x000001
\t\t\t\t\t\t\tentityKind: Built-in participant (0xc1)
\t\t\t\tPID_BUILTIN_ENDPOINT_SET
\t\t\t\t\tparameterId: PID_BUILTIN_ENDPOINT_SET (0x0058)
\t\t\t\t\tparameterLength: 4
\t\t\t\t\tFlags: 0x00000c3f, Participant Message DataReader, Participant Message DataWriter, Subscription Detector, Subscription Announcer, Publication Detector, Publication Announcer, Participant Detector, Participant Announcer
\t\t\t\t\t\t.... 0... .... .... .... .... .... .... = Participant Secure Reader: Not set
\t\t\t\t\t\t.... .0.. .... .... .... .... .... .... = Participant Secure Writer: Not set
\t\t\t\t\t\t.... ..0. .... .... .... .... .... .... = Secure Participant Volatile Message Reader: Not set
\t\t\t\t\t\t.... ...0 .... .... .... .... .... .... = Secure Participant Volatile Message Writer: Not set
\t\t\t\t\t\t.... .... .... 0... .... .... .... .... .... .... = Participant Stateless Message Reader: Not set
\t\t\t\t\t\t.... .... .0.. .... .... .... .... .... = Participant Stateless Message Writer: Not set
\t\t\t\t\t\t.... .... ..0. .... .... .... .... .... = Secure Participant Message Reader: Not set
\t\t\t\t\t\t.... .... ...0 .... .... .... .... .... = Secure Participant Message Writer: Not set
\t\t\t\t\t\t.... .... .... 0... .... .... .... .... = Secure Subscription Reader: Not set
\t\t\t\t\t\t.... .... .... .0.. .... .... .... .... = Secure Subscription Writer: Not set
\t\t\t\t\t\t.... .... .... ..0. .... .... .... .... = Secure Publication Reader: Not set
\t\t\t\t\t\t.... .... .... ...0 .... .... .... .... = Secure Publication Writer: Not set
\t\t\t\t\t\t.... .... .... .... 0000 .... .... .... = Reserved: Not set
\t\t\t\t\t\t.... .... .... .... .... 1... .... .... = Participant Message DataReader: Set
\t\t\t\t\t\t.... .... .... .... .... .1.. .... .... = Participant Message DataWriter: Set
\t\t\t\t\t\t.... .... .... .... .... ..0. .... .... = Participant State Detector: Not set
\t\t\t\t\t\t.... .... .... .... .... ...0 .... .... = Participant State Announcer: Not set
\t\t\t\t\t\t.... .... .... .... .... .... 0... .... = Participant Proxy Detector: Not set
\t\t\t\t\t\t.... .... .... .... .... .... .0.. .... = Participant Proxy Announcer: Not set
\t\t\t\t\t\t.... .... .... .... .... .... ..1. .... = Subscription Detector: Set
\t\t\t\t\t\t.... .... .... .... .... .... ...1 .... = Subscription Announcer: Set
\t\t\t\t\t\t.... .... .... .... .... .... .... 1... = Publication Detector: Set
\t\t\t\t\t\t.... .... .... .... .... .... .... .1.. = Publication Announcer: Set
\t\t\t\t\t\t.... .... .... .... .... .... .... ..1. = Participant Detector: Set
\t\t\t\t\t\t.... .... .... .... .... .... .... ...1 = Participant Announcer: Set
\t\t\t\tPID_DOMAIN_ID
\t\t\t\t\tparameterId: PID_DOMAIN_ID (0x000f)
\t\t\t\t\tparameterLength: 4
\t\t\t\t\tparameterData: 00000000
\t\t\t\tPID_DEFAULT_UNICAST_LOCATOR (LOCATOR_KIND_UDPV4, 192.168.10.2:37698)
\t\t\t\t\tparameterId: PID_DEFAULT_UNICAST_LOCATOR (0x0031)
\t\t\t\t\tparameterLength: 24
\t\t\t\t\tlocator
\t\t\t\t\t\tKind: LOCATOR_KIND_UDPV4 (0x00000001)
\t\t\t\t\t\tPort: 37698
\t\t\t\tPID_DEFAULT_MULTICAST_LOCATOR
\t\t\t\t\tparameterId: PID_DEFAULT_MULTICAST_LOCATOR (0x0048)
\t\t\t\t\tparameterLength: 24
\t\t\t\t\tparameterData: 01000000e91c0000000000000000000000000000efff0001
\t\t\t\tPID_METATRAFFIC_UNICAST_LOCATOR (LOCATOR_KIND_UDPV4, 192.168.10.2:37698)
\t\t\t\t\tparameterId: PID_METATRAFFIC_UNICAST_LOCATOR (0x0032)
\t\t\t\t\tparameterLength: 24
\t\t\t\t\tlocator
\t\t\t\t\t\tKind: LOCATOR_KIND_UDPV4 (0x00000001)
\t\t\t\t\t\tPort: 37698
\t\t\t\tPID_METATRAFFIC_MULTICAST_LOCATOR (LOCATOR_KIND_UDPV4, 239.255.0.1:7400)
\t\t\t\t\tparameterId: PID_METATRAFFIC_MULTICAST_LOCATOR (0x0033)
\t\t\t\t\tparameterLength: 24
\t\t\t\t\tlocator
\t\t\t\t\t\tKind: LOCATOR_KIND_UDPV4 (0x00000001)
\t\t\t\t\t\tPort: 7400
\t\t\t\tUnknown (0x8007)
\t\t\t\t\tparameterId: Unknown (0x8007)
\t\t\t\t\tparameterLength: 64
\t\t\t\t\tparameterData: 000000002c000000000000000000000000000000250000007374393534303830382d6937...
\t\t\t\tUnknown (0x8019)
\t\t\t\t\tparameterId: Unknown (0x8019)
\t\t\t\t\tparameterLength: 4
\t\t\t\t\tparameterData: 00002000
\t\t\t\tPID_SENTINEL
\t\t\t\t\tparameterId: PID_SENTINEL (0x0001)
"""


def parse_data(data_string):
  parsed_data = {}
  lines = data_string.strip().split('\n')
  path = [parsed_data]
  for line in lines:
      # Count the leading tabs to determine the indentation level
    tabs = len(line) - len(line.lstrip('\t'))
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


# parsed_data = parse_indented_data(data_string)
parsed_data = parse_data(data_string)
# parsed_data = convert_text_to_json(data_string)
# parsed_data = parse_nested_data(data_string)

pretty = json.dumps(parsed_data, indent=4)
print(pretty)
# print(parsed_data)

# print(parsed_data)
print(parsed_data['Real-Time Publish-Subscribe Wire Protocol']
      ['submessageId'].keys())
print(check_substring_in_list('DATA (0x15)',
      parsed_data['Real-Time Publish-Subscribe Wire Protocol']['submessageId'].keys()))
