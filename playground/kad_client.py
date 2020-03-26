import asyncio
import logging
import requests
from kademlia.network import Server

# entrypoint from sad.py
def kad_client_worker(args):
    kad_client(args['neighbor_ip'], args['neighbor_port'], args['username'])

def kad_client(neighbor_ip, neighbor_port, username):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    aio = asyncio.get_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen(8889))
    aio.run_until_complete(kad.bootstrap([(neighbor_ip, neighbor_port)]))
    aio.run_until_complete(asyncio.sleep(1))

    # get the value associated with "my-key" from the network
    result = aio.run_until_complete(kad.get(username))
    print("Client: " + str(result))

    # Now that we have gotten the users address from the network,
    # lets get their json profile
    response = requests.get(str(result) + "/")
    print(response.json())

    kad.stop()
    aio.close()
