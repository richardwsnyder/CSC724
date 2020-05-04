#!/bin/sh

apt install python3-pip
# install python deps
python3 -m pip install kademlia toml django
# flush the rules so we can host at port 80
iptables -F
