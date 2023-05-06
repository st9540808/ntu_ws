import pyshark

# Capture network traffic on eno2 interface
cap = pyshark.LiveCapture(
    interface="eno2", bpf_filter='rtps and rtps.submsg_id == "RTPS Data"'
)

# Filter for RTPS data traffic
cap.sniff(timeout=100)

# Extract GUID field from each captured packet
for packet in cap:
    try:
        guid = packet.rtps.guid_prefix
        print(f"GUID: {guid}")
    except AttributeError:
        # Ignore packets that don't have a GUID field
        pass
