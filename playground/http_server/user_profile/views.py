from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render

from user_profile.models import *

import json
import asyncio
import toml
import os
import multiprocessing

import kad_server
from kademlia.network import Server
from datetime import datetime
from .forms import NewPostForm

import global_config
global_config.init()
        
def get_our_profile():
    path = os.path.dirname(os.path.realpath(__file__))
    profile = ''
    with open(path + '/../../profile/profile.html', 'r') as content_file:
        profile = content_file.read()
    return profile

def get_user_remote(username):
    work_order = {}
    work_order['request'] = 'get_profile'
    work_order['username'] = username

    # ask kad_server to complete our request
    print('get_user_remote: sending work order: ' + str(work_order))
    global_config.pipe.send(work_order)

    # now wait for an answer
    profile = global_config.pipe.recv()
    
    return profile

def get_user(request, username):
    profile = {}
    if username == global_config.config['account']['username']:
        profile = get_our_profile()
    else:
        profile = get_user_remote(username)

    print(profile)
    return HttpResponse(profile)

# TODO use a template
def get_posts(request):

    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            p = Post(date=datetime.now(), text=form.cleaned_data['text'])
            p.save()
            return HttpResponseRedirect('/posts')
    else:
        # get date range
        num = int(request.GET.get('page', 1))

        # do pagination
        posts = Post.objects.order_by('-date')
        # 10 posts per page
        paginator = Paginator(posts, 4)

        if num not in paginator.page_range:
            return HttpResponse('')
    
        page = paginator.get_page(num)

        temp = {}
        temp['username'] = global_config.config['account']['username']
        temp['form'] = NewPostForm()
        temp['nextpage'] = num + 1
        temp['posts'] = page.object_list

        return render(request, 'posts.html', temp)

def index(request):
    return HttpResponse(get_our_profile())
