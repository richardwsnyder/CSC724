import asyncio
import logging
import requests
from kademlia.network import Server

# entrypoint from sad.py
def kad_client_worker(args):
    kad_client(args['neighbor_ip'], args['neighbor_port'], args['username'])

async def get_user_profile(kad, username):
    # get the value associated with "my-key" from the network
    result = await kad.get(username)
    print("Client: " + str(result))
    if str(result) == 'None':
        return '<html><h>User ' + username + ' not found</h></html>'

    # Now that we have gotten the users address from the network,
    # lets get their json profile
    response = requests.get(str(result) + "/")
    print(response.text)
    return response.text


def kad_client(neighbor_ip, neighbor_port, username):
    #handler = logging.StreamHandler()
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #handler.setFormatter(formatter)
    #log = logging.getLogger('kademlia')
    #log.addHandler(handler)
    #log.setLevel(logging.DEBUG)

    aio = asyncio.get_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen())
    aio.run_until_complete(kad.bootstrap([(neighbor_ip, neighbor_port)]))

    resp = aio.run_until_complete(get_user_profile(kad, username))
    print(resp.json())

    kad.stop()
    aio.close()
