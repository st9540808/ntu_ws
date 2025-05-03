#!/usr/bin/python
#
# tc_perf_event.py  Output skb and meta data through perf event
#
# Copyright (c) 2016-present, Facebook, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

from time import sleep
from bcc import BPF
import ctypes as ct
import pyroute2
import socket

bpf_txt = """
#include <uapi/linux/if_ether.h>
#include <uapi/linux/in6.h>
#include <uapi/linux/ipv6.h>
#include <uapi/linux/pkt_cls.h>
#include <uapi/linux/bpf.h>

BPF_PERF_OUTPUT(skb_events);

struct eth_hdr {
	unsigned char   h_dest[ETH_ALEN];
	unsigned char   h_source[ETH_ALEN];
	unsigned short  h_proto;
};

static int handle_egress(struct __sk_buff *skb)
{
	void *data = (void *)(long)skb->data;
	void *data_end = (void *)(long)skb->data_end;
	struct eth_hdr *eth = data;
	struct ipv6hdr *ip6h = data + sizeof(*eth);
	u32 magic = 0xfaceb00c;
  u32 prio = 1;


  // skb->priority = 3;

	/* single length check */
	if (data + sizeof(*eth) + sizeof(*ip6h) > data_end)
		return TC_ACT_PIPE;

	return TC_ACT_PIPE;
}

int handle_egress_dev(struct __sk_buff *skb)
{
	bpf_trace_printk("(dev) vlan_tci: %d, priority: %d", skb->vlan_tci, skb->priority);
	handle_egress(skb);
}

int handle_egress_dev_vlan(struct __sk_buff *skb)
{
	bpf_trace_printk("(dev.vlan) vlan_tci: %d, priority: %d", skb->vlan_tci, skb->priority);
	handle_egress(skb);
}
"""

DEVICE = 'eno2.11'
DEVICE2 = 'eno2'

b = BPF(text=bpf_txt)

fn_egress = b.load_func("handle_egress_dev_vlan", BPF.SCHED_CLS)
fn2_egress = b.load_func("handle_egress_dev", BPF.SCHED_CLS)

ip = pyroute2.IPRoute()
ipdb = pyroute2.IPDB(nl=ip)

idx = ipdb.interfaces[DEVICE].index
idx2 = ipdb.interfaces[DEVICE2].index

ip.tc("add", "clsact", idx)
ip.tc("add", "clsact", idx2)

# add egress clsact
ip.tc("add-filter", "bpf", idx, ":1", fd=fn_egress.fd, name=fn_egress.name,
      parent="ffff:fff3", classid=1, direct_action=True)
ip.tc("add-filter", "bpf", idx2, ":1", fd=fn2_egress.fd, name=fn2_egress.name,
      parent="ffff:fff3", classid=1, direct_action=True)

# header
print("Tracing... Ctrl-C to end.")

try:
  b.trace_print()
  while True:
    sleep(1)
except KeyboardInterrupt:
  print('Exiting')

ip.tc("del", "clsact", idx)
ip.tc("del", "clsact", idx2)

ipdb.release()
