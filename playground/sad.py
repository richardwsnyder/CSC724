import sys
import multiprocessing
import argparse

import kad_server
import kad_client
import http_server

# Parse arguments
# use the -h flag to get a nice summary of the options
# eg: python3.7 sad.py server join -h
parser = argparse.ArgumentParser(description='sad: social and decentralized')
parser.print_help(sys.stderr)
subparsers = parser.add_subparsers(help="server subcommand")
parse_server = subparsers.add_parser("server", help="commands for operating in server mode")

ps_subparsers = parse_server.add_subparsers(help="bootstrap a new network")
ps_bootstrap = ps_subparsers.add_parser("bootstrap", help="bootstrap a new network")
ps_bootstrap.add_argument("network_port", type=int, help="the port to listen on for the kademlia network")
ps_bootstrap.add_argument("profile_port", type=int, help="the port to host the user profile's http server at")
ps_bootstrap.add_argument("username", help="the username to host a profile for")

ps_join = ps_subparsers.add_parser("join", help="join an existing network")
ps_join.add_argument("network_port", type=int, help="the port to listen on for the kademlia network")
ps_join.add_argument("profile_port", type=int, help="the port to host the user profile's http server at")
ps_join.add_argument("neighbor_ip", help="the ip address of a node already part of a network")
ps_join.add_argument("neighbor_port", type=int, help="the port of the machine we should join")
ps_join.add_argument("username", help="the username to host a profile for")

parse_client = subparsers.add_parser("client", help="commands for operating in server mode")
parse_client.add_argument("neighbor_ip", help="the ip address of a node already part of a network")
parse_client.add_argument("neighbor_port", type=int, help="the kademlia port of the machine we should connect with")
parse_client.add_argument("username", help="the username to get a profile for")


args = vars(parser.parse_args())
print(args)

if sys.argv[1] == 'server':
    # Launch processes for the kademlia network and the http server

    # The kademlia network replaces the central servers of a system like naptser,
    # it is used by clients to find out where the user profiles are hosted.
    kad_proc = multiprocessing.Process(target=kad_server.kad_server_worker_thread, args=(args, sys.argv[2],))
    kad_proc.start()

    # once their ip:port address is looked up in the kademlia network, the
    # user profile needs to answer http requests so that clients can get
    # data. This http server does just that.
    http_proc = multiprocessing.Process(target=http_server.http_server_worker_thread, args=(args,))
    http_proc.start()
else:
    # we are acting as a trivial client, which is going to grab some json
    kad_client.kad_client_worker(args)
