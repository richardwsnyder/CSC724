import asyncio
import logging
import os
import toml
import requests
from kademlia.network import Server
from kademlia.crawling import *
import socket

# timeout after a quarter of a second
TIMEOUT=0.25

# helper for getting the content at a URL
# returns a string
def http_get_url(url):
    print('Making http request to: {}', url)
    print('---------')
    ret = {}
    try:
        response = requests.get(url, timeout=TIMEOUT)
        ret['status'] = response.status_code
        ret['body'] = response.text
    except:
        ret['status'] = 404
        ret['body'] = ''
    print(ret)
    print('---------')
    return ret

def get_config():
    path = os.environ['SAD_CONFIG_FILE']
    config = ''
    with open(path, 'r') as content_file:
        config = toml.load(content_file)

    return config

async def get_url_from_username(kad,username):
    return await kad.get(username)

async def get_user_profile(kad, username):
    # get the value associated with "my-key" from the network
    result = await get_url_from_username(kad, username)
    print("Client: " + str(result))
    if str(result) == 'None':
        temp = {}
        temp['status'] = 404
        return temp

    # Now that we have gotten the users address from the network,
    # lets get their json profile
    response = http_get_url(str(result) + "/api/profile")
    print(response)
    return response

async def get_user_posts(kad, username, num):
    # get the value associated with "my-key" from the network
    result = await get_url_from_username(kad, username)
    print("Client: " + str(result))
    if str(result) == 'None':
        temp = {}
        temp['status'] = 404
        return temp

    response = http_get_url(str(result) + "/api/posts?page=" + str(num))
    return response

async def get_user_directory(aio, kad):
    print('get_user_directory:')
    us = kad.protocol.router.node
    print('  node - ' + str(us))
    nearest = kad.protocol.router.find_neighbors(us)
    print('  nearest - ' + str(nearest))
    spider = ValueSpiderCrawl(kad.protocol, us, nearest, kad.ksize, kad.alpha)

    nodes = await spider.find()
    for k in nodes:
        print(k)

    return 'placeholder'

async def add_follower(kad, username, my_username):
    result = await get_url_from_username(kad, username)
    print("Client: " + str(result))
    if str(result) == 'None':
        return '<html><h>User ' + username + ' not found</h></html>'
    response = http_get_url(str(result) + "/followers/" + my_username + "/addFollower")
    print("response in add_follower: " + str(response))
    return response

async def remove_follower(kad, username, my_username):
    result = await get_url_from_username(kad, username)
    print("Client: " + str(result))
    if str(result) == 'None':
        return '<html><h>User ' + username + ' not found</h></html>'
    response = http_get_url(str(result) + "/followers/" + my_username + "/removeFollower")
    print("response in remove_follower: " + str(response))
    return response

# this should be a pipe
pipe = ''

async def get_single_pipe_input(aio, kad):
    print('kad_server: waiting for input')
    # we need to wrap any sync blocking calls in this
    # so that the async engine still runs
    work_order = await aio.run_in_executor(None, pipe.recv)
    print('kad_server got work order: ' + str(work_order))

    profile = 'Unknown request ' +  work_order['request']
    if work_order['request'] == 'get_profile':
        profile = await get_user_profile(kad, work_order['username'])
    elif work_order['request'] == 'get_posts':
        profile = await get_user_posts(kad, work_order['username'], work_order['page_num'])
    elif work_order['request'] == 'get_directory':
        profile = await get_user_directory(aio, kad)
    elif work_order['request'] == 'add_follower':
        profile = await add_follower(kad, work_order['username'], work_order['my_username'])
    elif work_order['request'] == 'remove_follower':
        profile = await remove_follower(kad, work_order['username'], work_order['my_username'])

    pipe.send(profile)

def main_loop(aio, kad):
    while 1:
        aio.run_until_complete(get_single_pipe_input(aio, kad))

# entrypoint from sad.py
def kad_server_worker_thread(p):
    global pipe
    pipe = p
    config = get_config()
    print('kad_server: ' + str(config))
    cf_conn = config['connection']
    verb = cf_conn['action']
    if verb == "bootstrap":
        kad_server_bootstrap(
            cf_conn['network_port'],
            cf_conn['profile_port'],
            config['account']['username']
        )
    elif verb == "join":
        kad_server_join(
            cf_conn['network_port'],
            cf_conn['profile_port'],
            cf_conn['neighbor_ip'],
            cf_conn['neighbor_port'],
            config['account']['username']
        )
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

    aio = asyncio.new_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen(network_port))
    aio.set_debug(True)

    while len(kad.bootstrappable_neighbors()) == 0:
        aio.run_until_complete(asyncio.sleep(1))

    # set a value for the key "my-key" on the network
    aio.run_until_complete(kad.set(username, 'http://' + socket.gethostname() + ':' + str(profile_port)))
    aio.run_until_complete(asyncio.sleep(2))

    # run forever since we are the first node
    try:
        main_loop(aio, kad)
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

    aio = asyncio.new_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen(network_port))
    aio.run_until_complete(kad.bootstrap([(neighbor_ip, neighbor_port)]))
    aio.run_until_complete(asyncio.sleep(1))

    # set a value for the key "my-key" on the network
    aio.run_until_complete(kad.set(username, 'http://' + socket.gethostname() + ':' + str(profile_port)))
    aio.run_until_complete(asyncio.sleep(2))

    # run forever since we are the first node
    try:
        main_loop(aio, kad)
    except KeyboardInterrupt:
        pass
    finally:
        kad.stop()
        aio.close()
