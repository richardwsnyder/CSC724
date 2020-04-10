from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator

from user_profile.models import *

import json
import asyncio
import toml
import os

import kad_client
from kademlia.network import Server
from datetime import datetime
import config as global_config

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

def get_user_remote(username):
    loop = asyncio.new_event_loop()
    kad = Server()
    loop.run_until_complete(kad.listen(8889))
    print('querying network at {}:{}', 'localhost', kad_port)
    loop.run_until_complete(kad.bootstrap([('localhost', kad_port)]))
    profile = loop.run_until_complete(kad_client.get_user_profile(kad, username))
    kad.stop()
    loop.close()
    return profile

def get_user(request, username):
    global config
    get_config()
    profile = {}
    if username == config['account']['username']:
        profile = get_our_profile()
    else:
        profile = get_user_remote(username)

    print(profile)
    return HttpResponse(profile)

# TODO use a template
def get_posts(request):

    # get date range
    num = int(request.GET.get('page', 1))

    # do pagination
    posts = Post.objects.order_by('-date')
    # 10 posts per page
    paginator = Paginator(posts, 4)

    if num not in paginator.page_range:
        return HttpResponse('')
    
    page = paginator.get_page(num)

    html = '<div>'
    for p in page.object_list:
        html = html + '<p>' + p.text + '</p>'

    html = html + '<div>'
    return HttpResponse(html)

def index(request):
    get_config()
    return HttpResponse(get_our_profile())
