import asyncio
import logging
import os
import toml
from kademlia.network import Server

def get_config():
    path = os.environ['SAD_CONFIG_FILE']
    config = ''
    with open(path, 'r') as content_file:
        config = toml.load(content_file)

    return config

# this should be a pipe
pipe = ''

async def get_single_pipe_input():
    print('kad_server: waiting for input')
    work_order = pipe.recv()
    print('kad_server got work order: ' + str(work_order))

def main_loop(aio):
    while 1:
        aio.run_until_complete(get_single_pipe_input())
    
# entrypoint from sad.py
def kad_server_worker_thread(p):
    global pipe
    pipe = p
    config = get_config()
    print('kad_server: ' + str(config))
    cf_conn = config['connection']
    verb = cf_conn['action']
    if verb == "bootstrap":
        kad_server_bootstrap(cf_conn['network_port'], cf_conn['profile_port'], config['account']['username'])
    elif verb == "join":
        kad_server_join(cf_conn['network_port'], cf_conn['profile_port'], cf_conn['neighbor_ip'], cf_conn['neighbor_port'], config['account']['username'])
    else:
        print('did not recognize argument ' + verb)

# bootstrap a new network
# aka we are the first node
def kad_server_bootstrap(network_port, profile_port, username):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    aio = asyncio.get_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen(network_port))
    aio.set_debug(True)

    while len(kad.bootstrappable_neighbors()) == 0:
        aio.run_until_complete(asyncio.sleep(1))

    # set a value for the key "my-key" on the network
    aio.run_until_complete(kad.set(username, "http://127.0.0.1:" + str(profile_port)))
    aio.run_until_complete(asyncio.sleep(2))

    # run forever since we are the first node
    try:
        main_loop(aio)
    except KeyboardInterrupt:
        pass
    finally:
        kad.stop()
        aio.close()

# join an existing network (the neighbor)
def kad_server_join(network_port, profile_port, neighbor_ip, neighbor_port, username):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    aio = asyncio.get_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen(network_port))
    aio.run_until_complete(kad.bootstrap([(neighbor_ip, neighbor_port)]))
    aio.run_until_complete(asyncio.sleep(1))

    # set a value for the key "my-key" on the network
    aio.run_until_complete(kad.set(username, "http://127.0.0.1:" + str(profile_port)))
    aio.run_until_complete(asyncio.sleep(2))

    # run forever since we are the first node
    try:
        main_loop(aio)
    except KeyboardInterrupt:
        pass
    finally:
        kad.stop()
        aio.close()
