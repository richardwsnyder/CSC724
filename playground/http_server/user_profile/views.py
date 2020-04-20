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
from .forms import *
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

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

    return profile

def get_posts_remote_raw(request, username, num):
    """Get somebody else's (username's) posts"""
    work_order = {}
    work_order['request'] = 'get_posts'
    work_order['username'] = username
    work_order['page_num'] = num

    # ask kad_server to complete our request
    print('get_user_posts_remote: sending work order: ' + str(work_order))
    global_config.pipe.send(work_order)

    # now wait for an answer
    posts_raw = global_config.pipe.recv()
    posts = {}
    if posts_raw['status'] != 200:
        posts['dne'] = True
    else:
        posts = json.loads(posts_raw['body'])
    return posts

def get_posts_remote(request, username):
    num = int(request.GET.get('page', 1))
    posts = get_posts_remote_raw(request, username, num)
    temp = {}
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    if username == global_config.config['account']['username']:
        temp['form'] = NewPostForm()
    temp['nextpage'] = "/posts/" + username + "?page=" + str(num + 1)
    temp['posts'] = posts

    return render(request, 'posts.html', temp)

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
        profile_raw = get_user_remote(username)
        if profile_raw['status'] != 200:
            profile['dne'] = True
        else:
            profile = json.loads(profile_raw['body'])
        end = time.time()
        print("time to get " + username + "'s profile: " + str(end - start))

    print(profile)
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
    postlist = []
    if num == -1:
        # return all posts
        postlist = posts
    else:
        # 10 posts per page
        paginator = Paginator(posts, 10)

        if num not in paginator.page_range:
            return None

        page = paginator.get_page(num)
        postlist = page.object_list

    pl = []
    for p in postlist:
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

def api_get_posts_all(request):
    # return all posts
    posts = get_posts_raw(request, -1)

    ret = {}
    ret['posts'] = posts

    return HttpResponse(json.dumps(ret, cls=DjangoJSONEncoder))


def get_posts(request):
    num = int(request.GET.get('page', 1))
    posts = get_posts_raw(request, num)

    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            p = Post(date=datetime.now(), text=form.cleaned_data['text'])
            p.save()
        return HttpResponseRedirect('/posts')
    else:
        temp = {}
        temp['fullname'] = global_config.config['account']['fullname']
        temp['username'] = global_config.config['account']['username']
        temp['form'] = NewPostForm()
        temp['nextpage'] = "/posts?page=" + str(num + 1)
        temp['posts'] = posts

        return render(request, 'posts.html', temp)

def get_following_list(request):
    """Get the list of usernames that you follow. Returns a QuerySet"""
    return Following.objects.all()

def addFollower(request, username):
    follower = Followers(name=username, dateAdded=datetime.now())
    follower.save()
    return HttpResponse('added ' + username + ' to followers')

def removeFollower(request, username):
    follower = Followers.objects.filter(name=username)
    follower.delete()
    return HttpResponse('removed ' + username + ' from followers')

def addToFollowing(request, username):
    """Add a username to the following list"""
    alreadyFollowing = Following.objects.filter(name=username).count() > 0
    retString = ''
    if alreadyFollowing:
        retString = 'You are already following ' + username
    else:
        following = Following(name=username, dateAdded=datetime.now())
        following.save()
        my_username = global_config.config['account']['username']
        work_order = {}
        work_order['request'] = 'add_follower'
        work_order['my_username'] = my_username
        work_order['username'] = username
        print('addToFollower: sending work order: ' + str(work_order))
        global_config.pipe.send(work_order)

        respString = global_config.pipe.recv()['body']
        print('respString: ' + respString)
        if respString != 'added ' + username + ' to followers':
            print('something went wrong')
        retString = 'Now following user ' + username
    
    return HttpResponse(retString)

def removeFromFollowing(request, username):
    """Remove a user from the following list"""
    notFollowing = Following.objects.filter(name=username).count() == 0
    retString = ''
    if notFollowing:
        retString = 'You do not follow ' + username
    else:
        following = Following.objects.filter(name=username)
        following.delete()
        my_username = global_config.config['account']['username']
        work_order = {}
        work_order['request'] = 'remove_follower'
        work_order['my_username'] = my_username
        work_order['username'] = username
        print('removeFromFollowing: sending work order: ' + str(work_order))
        global_config.pipe.send(work_order)

        respString = global_config.pipe.recv()['body']
        print('respString: ' + respString)
        if respString != 'removed ' + username + ' from followers':
            print('something went wrong')
        retString = 'You are now not following ' + username
    return HttpResponse(retString)

def index(request):
    """Return our profile when hitting / route"""
    temp = {}
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    temp['profile'] = get_our_profile()
    return render(request, 'profile.html', temp)

# Add routes that 
def search_user(request):
    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/user/' + str(form.cleaned_data['username']))

def pull_fresh_feed(request):
    following = Following.objects.all()
    # clear the old data, we are regenerating everything
    # each time this is run
    FeedPost.objects.all().delete()

    for f in following:
        print('--- getting posts for ' + f.name)
        user_posts = {}
        if f.name == global_config.config['account']['username']:
            user_posts = get_posts_raw(request, -1)
        else:
            user_posts = get_posts_remote_raw(request, f.name, -1)
            if 'dne' in user_posts.keys():
                user_posts = []
            else:
                user_posts = user_posts['posts']

        # add posts from this user to the db
        for post in user_posts:
            fp = FeedPost(text=post['text'],
                          date=post['date'],
                          fullname=post['fullname'],
                          username=post['username'])
            fp.save()
            u = User.objects.get_or_create(fullname=post['fullname'],
                                           username=post['username'])

def get_feed_raw(request, num):
    pull_fresh_feed(request)
    # get feed paginator
    posts = FeedPost.objects.order_by('-date')
    paginator = Paginator(posts, 10)

    if num not in paginator.page_range:
        return None

    page = paginator.get_page(num)
    return page.object_list

def api_get_feed(request):
    num = int(request.GET.get('page', 1))
    user_posts = get_feed_raw(request, num)
    return HttpResponse(serializers.serialize('json', user_posts))

def get_feed(request):
    num = int(request.GET.get('page', 1))
    user_posts = get_feed_raw(request, num)
    temp = {}
    temp['title'] = 'News Feed'
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    temp['nextpage'] = "/feed?page=" + str(num + 1)
    temp['posts'] = user_posts
    return render(request, 'posts.html', temp)

def get_known_users_raw(num):
    users = User.objects.all()
    if num == -1:
        return users
    paginator = Paginator(users, 10)

    if num not in paginator.page_range:
        return None

    page = paginator.get_page(num)
    return page.object_list

def api_get_known_users(request):
    users = get_known_users_raw(-1)
    return HttpResponse(serializers.serialize('json', users))

def get_known_users(request):
    num = int(request.GET.get('page', 1))
    users = get_known_users_raw(num)
    temp = {}
    temp['title'] = 'Known Users In This Network'
    temp['fullname'] = global_config.config['account']['fullname']
    temp['username'] = global_config.config['account']['username']
    temp['users'] = users
    return render(request, 'user_directory.html', temp)
