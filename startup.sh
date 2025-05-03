VLAN=11 IP_SUFFIX=3 /home/st9540808/Desktop/autoware_ws/ntu_ws/make_vlan.sh
VLAN=12 IP_SUFFIX=3 /home/st9540808/Desktop/autoware_ws/ntu_ws/make_vlan.sh
if [ ! -e /tmp/cycloneDDS_configured ]; then
    sudo sysctl -w net.core.rmem_max=2147483647
    sudo ip link set lo multicast on
    touch /tmp/cycloneDDS_configured
fi
sudo iptables -t mangle -A POSTROUTING -o eno2.11 -j CLASSIFY --set-class 0:2
sudo iptables -t mangle -A POSTROUTING -o eno2.12 -j CLASSIFY --set-class 0:3
sudo systemctl stop systemd-timesyncd
sudo ethtool -G eno2 rx 1024
sudo ethtool -G eno2 tx 1024
