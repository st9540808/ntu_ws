from scapy.all import *
import scapy.contrib.rtps as rtps
import sys

conf.iface = "eno2"

# cap = sniff(filter="udp", store=False)
cap = sniff(filter="udp", store=False, prn=lambda p: print(p.time))
