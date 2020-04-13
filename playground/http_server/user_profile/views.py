"""
Functions to hit different routes of data
"""
import os
import time
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
import global_config
from user_profile.models import *
from .forms import NewPostForm
# import json
# import asyncio
# import toml
# import multiprocessing
# import kad_server
# from kademlia.network import Server

global_config.init()

def get_our_profile():
    """Get local profile"""
    path = os.path.dirname(os.path.realpath(__file__))
    profile = ''
    with open(path + '/../../profile/profile.html', 'r') as content_file:
        profile = content_file.read()
    return profile

def get_user_remote(username):
    """Get somebody else's (username's) profile"""
    work_order = {}
    work_order['request'] = 'get_profile'
    work_order['username'] = username

    # ask kad_server to complete our request
    print('get_user_remote: sending work order: ' + str(work_order))
    global_config.pipe.send(work_order)

    # now wait for an answer
    profile = global_config.pipe.recv()

    return profile

def get_posts_remote(request, username):
    """Get somebody else's (username's) posts"""
    work_order = {}
    work_order['request'] = 'get_posts'
    work_order['username'] = username

    # ask kad_server to complete our request
    print('get_user_posts_remote: sending work order: ' + str(work_order))
    global_config.pipe.send(work_order)

    # now wait for an answer
    posts = global_config.pipe.recv()

    return HttpResponse(posts)

def get_profile_directory(request):
    """Get a list of all profiles in the network"""
    work_order = {}
    work_order['request'] = 'get_directory'

    # ask kad_server to complete our request
    print('get_user_posts_remote: sending work order: ' + str(work_order))
    global_config.pipe.send(work_order)

    # now wait for an answer
    directory = global_config.pipe.recv()

    return HttpResponse(directory)
    
# unused argument request
def get_user(request, username):
    """Function that maps to one of the above calls"""
    profile = {}
    if username == global_config.config['account']['username']:
        start = time.time()
        profile = get_our_profile()
        end = time.time()
        print("time to get our profile: " + str(end - start))
    else:
        start = time.time()
        profile = get_user_remote(username)
        end = time.time()
        print("time to get " + username + "'s profile: " + str(end - start))

    return HttpResponse(profile)

def get_posts(request):
    """Get posts from SQLite database"""
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
    """Return our profile when hitting / route"""
    return HttpResponse(get_our_profile())

# Add routes that 
