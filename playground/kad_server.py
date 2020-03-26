import asyncio
import logging
from kademlia.network import Server

# entrypoint from sad.py
def kad_server_worker_thread(args, verb):
    if verb == "bootstrap":
        kad_server_bootstrap(args['network_port'], args['profile_port'], args['username'])
    elif verb == "join":
        kad_server_join(args['network_port'], args['profile_port'], args['neighbor_ip'], args['neighbor_port'], args['username'])
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

    # run forever since we are the first node
    try:
        aio.run_forever()
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

    # run forever since we are the first node
    try:
        aio.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        kad.stop()
        aio.close()
