from django.shortcuts import render
from django.http import HttpResponse

import json
import asyncio
import kad_client
import os
from aiohttp import web
from kademlia.network import Server
import toml

config = -1
kad_port = -1
our_username = ""

def get_config():
    global config
    if config == -1:
        path = os.environ['SAD_CONFIG_FILE']
        print('getting config from ' + path)
        with open(path, 'r') as content_file:
            global kad_port
            config = toml.load(content_file)
            kad_port = config['connection']['network_port']
        
def get_our_profile():
    get_config()
    path = os.path.dirname(os.path.realpath(__file__))
    profile = ''
    with open(path + '/../../profile/profile.html', 'r') as content_file:
        profile = content_file.read()
    return profile

def get_user(request, username):
    global config
    get_config()
    profile = {}
    if username == config['account']['username']:
        profile = get_our_profile()
    else:
        loop = asyncio.new_event_loop()
        kad = Server()
        loop.run_until_complete(kad.listen(8889))
        print('querying network at {}:{}', 'localhost', kad_port)
        loop.run_until_complete(kad.bootstrap([('localhost', kad_port)]))
        profile = loop.run_until_complete(kad_client.get_user_profile(kad, username))
        kad.stop()
        loop.close()

    print(profile)
    return HttpResponse(profile)

def index(request):
    get_config()
    return HttpResponse(get_our_profile())
