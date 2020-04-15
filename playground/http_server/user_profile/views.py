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
from django.core.serializers.json import DjangoJSONEncoder

import json

global_config.init()

def get_our_profile():
    """Get local profile"""
    path = os.path.dirname(os.path.realpath(__file__))
    profile = {}
    profile['fullname'] = global_config.config['account']['fullname']
    profile['username'] = global_config.config['account']['username']
    with open(path + '/../../profile/profile.html', 'r') as content_file:
        profile['html'] = content_file.read()
    return profile

def api_get_profile(request):
    profile = get_our_profile()
    return HttpResponse(json.dumps(profile, cls=DjangoJSONEncoder))

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

    return json.loads(profile)

def get_posts_remote(request, username):
    """Get somebody else's (username's) posts"""
    num = int(request.GET.get('page', 1))
    work_order = {}
    work_order['request'] = 'get_posts'
    work_order['username'] = username
    work_order['page_num'] = num

    # ask kad_server to complete our request
    print('get_user_posts_remote: sending work order: ' + str(work_order))
    global_config.pipe.send(work_order)

    # now wait for an answer
    posts_raw = global_config.pipe.recv()
    posts = json.loads(posts_raw)
    temp = {}
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    temp['nextpage'] = "/posts/" + username + "?page=" + str(num + 1)
    temp['posts'] = posts['posts']

    return render(request, 'posts.html', temp)

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

def get_user_raw(request, username):
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

    return profile

def api_get_user(request, username):
    profile = get_user_raw(request, username)
    return HttpResponse(json.dumps(profile, cls=DjangoJSONEncoder))

def get_user(request, username):
    profile = get_user_raw(request, username)
    temp = {}
    temp['profile'] = profile
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    return render(request, 'profile.html', temp)

def get_posts_raw(request, num):
    # do pagination
    posts = Post.objects.order_by('-date')
    # 10 posts per page
    paginator = Paginator(posts, 4)

    if num not in paginator.page_range:
        return None

    page = paginator.get_page(num)
    pl = []
    for p in page.object_list:
        entry = {}
        entry['fullname'] = global_config.config['account']['fullname']
        entry['username'] = global_config.config['account']['username']
        entry['date'] = p.date
        entry['text'] = p.text
        pl.append(entry)
    return pl

def api_get_posts(request):
    """Get or add to posts from SQLite database"""
    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            p = Post(date=datetime.now(), text=form.cleaned_data['text'])
            p.save()
            return HttpResponse('post created')
    else:
        # get date range
        num = int(request.GET.get('page', 1))

        posts = get_posts_raw(request, num)
        ret = {}
        ret['page_num'] = num
        ret['posts'] = posts

        return HttpResponse(json.dumps(ret, cls=DjangoJSONEncoder))

def get_posts(request):
    num = int(request.GET.get('page', 1))
    posts = get_posts_raw(request, num)

    if request.method == 'POST':
        return HttpResponseRedirect('/posts')
    else:
        temp = {}
        temp['fullname'] = global_config.config['account']['fullname']
        temp['username'] = global_config.config['account']['username']
        temp['form'] = NewPostForm()
        temp['nextpage'] = "/posts?page=" + str(num + 1)
        temp['posts'] = posts

        return render(request, 'posts.html', temp)

# Have to read the Django docs to figure out
# how to add and remove a username from the
# db

# def get_following(request):
#     """Get or add to the list of usernames that you follow"""
#     if request.method == 'POST':
#         p = Followers(name='', dateAdded=datetime.now())

def index(request):
    """Return our profile when hitting / route"""
    temp = {}
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    temp['profile'] = get_our_profile()
    return render(request, 'profile.html', temp)

# Add routes that 
