#!/bin/sh

git clone https://github.com/richardwsnyder/CSC724
apt install python3-pip
python3 -m pip install kademlia toml django
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -p tcp --sport 80 -m conntrack --ctstate ESTABLISHED -j ACCEPT
