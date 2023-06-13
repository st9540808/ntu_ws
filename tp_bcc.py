from bcc import BPF
from time import sleep
import ctypes

# Define BPF program
BPF_PROGRAM = """
#include <uapi/linux/ptrace.h>

#include <linux/sched.h>
#include <linux/types.h>
#include <linux/netdevice.h>
#include <linux/ethtool.h>
#include <net/sock.h>

#include <bcc/proto.h>
#include <bcc/helpers.h>

typedef struct avali_dev {
    char devname[IFNAMSIZ];
} avali_dev_t;

typedef struct data {
    char comm[16];
    char devname[IFNAMSIZ];
} data_t;

char eno2[] = "eno2";
BPF_HASH(counts, data_t);
// BPF_TABLE(avali_devs, dev_t);
BPF_TABLE("hash", dev_t, u32, avali_devs, 12);

#define TP_DATA_LOC_READ_STR(dst, field, length)                                \
        do {                                                                    \
            unsigned short __offset = args->data_loc_##field & 0xFFFF;          \
            bpf_probe_read_str((void *)dst, length, (char *)args + __offset);   \
        } while (0)

TRACEPOINT_PROBE(net, net_dev_queue) {
    data_t data = {};

    struct sk_buff* skb = (struct sk_buff*)args->skbaddr;

    // int name_offset = args->data_loc_name;
    // read string from __data_loc area
    // bpf_probe_read_kernel(&data.devname, sizeof(data.devname), (void *)args->data_loc_name);
    TP_DATA_LOC_READ_STR(&data.devname, name, sizeof(data.devname));

    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    if (skb != NULL) {
      bpf_trace_printk("dev: %s, %d", data.devname, skb->vlan_tci);
        // bpf_probe_read_kernel_str(data.devname, sizeof(data.devname), name);

        // if (__builtin_memcmp(data.devname, eno2, sizeof(eno2)) != 0) {
        //   return 0;
        // }

        counts.increment(data);
    }
    return 0;
}
"""


# Define a Python class that mirrors the struct dev_t in C
class dev_t(ctypes.Structure):
  _fields_ = [("devname", ctypes.c_char * 16)]


# Initialize BPF
b = BPF(text=BPF_PROGRAM)

# Create a list of dev_t instances
# devnames = [dev_t(), dev_t()]
# # Assuming "eth0" is the name of the first device
# devnames[0].devname = b"eth0"
# # Assuming "eth1" is the name of the second device
# devnames[1].devname = b"eth1"

# # Cast them to a ctypes.c_void_p to be compatible with BPF_HASH
# devnames_p = [ctypes.cast(ctypes.pointer(devname), ctypes.c_void_p)
#               for devname in devnames]

# # Create a list of initial values
# initial_values = [ctypes.c_ulonglong(1) for _ in devnames]

# # Update the map
# b["avali_devs"].items_update_batch(devnames_p, initial_values)

# # Verify they were correctly added
# for k, v in b["avali_devs"].items():
#   print("Device name: {}, Value: {}".format(k.devname, v.value))

# Sleep loop
try:
  while True:
    sleep(1)
except KeyboardInterrupt:
  for k, v in b["counts"].items():
    print("Process %s sent %d packet(s) through %s" %
          (k.comm.decode('utf-8'), v.value, k.devname.decode('utf-8')))
