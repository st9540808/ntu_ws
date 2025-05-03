from bcc import BPF
from time import sleep
import ctypes

# Define BPF program
BPF_PROGRAM = """
#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf.h>

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

BPF_HASH(counts, data_t);
// BPF_TABLE(avali_devs, dev_t);
BPF_TABLE("hash", dev_t, u32, avali_devs, 12);

#define TP_DATA_LOC_READ_STR(dst, field, length)                                \
        do {                                                                    \
            unsigned short __offset = args->data_loc_##field & 0xFFFF;          \
            bpf_probe_read_str((void *)dst, length, (char *)args + __offset);   \
        } while (0)

static int compare_devname(char *devname) {
  char tgt[] = "eno2";
  int size = IFNAMSIZ;

  for (int i = 0; i < (size & 0xff); i++) {
    if (devname[i] == 0 || tgt[i] == 0) {
      break;
    }
    if (devname[i] != tgt[i]) {
      return 1;
    }
  }

  return 0;
}

TRACEPOINT_PROBE(net, net_dev_queue) {
    char eno2[] = "eno2";
    data_t data = {};
    u32 prio = 1;

    struct sk_buff* skb = (struct sk_buff*)args->skbaddr;

    // int name_offset = args->data_loc_name;
    // read string from __data_loc area
    // bpf_probe_read_kernel(&data.devname, sizeof(data.devname), (void *)args->data_loc_name);
    TP_DATA_LOC_READ_STR(&data.devname, name, sizeof(data.devname));

    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    if (skb != NULL) {
      // bpf_probe_read_kernel_str(data.devname, sizeof(data.devname), name);

      //bpf_skb_store_bytes(skb, offsetof(struct sk_buff, priority), &prio,
      //                    sizeof(prio), BPF_F_INVALIDATE_HASH);
      //skb->priority = 1;

      if (compare_devname(data.devname) == 0) {
        bpf_trace_printk("dev: %s, %d", data.devname, skb->vlan_tci);
        return 0;
      }

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

func_sock_ops = b.load_func("bpf_sockhash", bpf.SOCK_OPS)
b.attach_func(func_sock_ops, fd, BPFAttachType.CGROUP_SOCK_OPS)

# header
print("Tracing... Ctrl-C to end.")

# Sleep loop
try:
  while True:
    sleep(1)
except KeyboardInterrupt:
  for k, v in b["counts"].items():
    print("Process %s sent %d packet(s) through %s" %
          (k.comm.decode('utf-8'), v.value, k.devname.decode('utf-8')))
