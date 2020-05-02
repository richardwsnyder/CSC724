import requests
import socket
import sys
import time

port = sys.argv[1]
url = 'http://{}:{}'.format(socket.gethostname(), port)

my_username = sys.argv[2]
their_username = sys.argv[3]
num_nodes = sys.argv[4]

endpoints = ['/', '/posts', 'posts/{}'.format(their_username), '/profile_directory',
            '/feed', '/user/{}'.format(their_username), '/user/{}/follow'.format(their_username),
            '/user/{}/unfollow'.format(their_username), '/followers/{}/addFollower'.format(my_username),
            '/followers/{}/removeFollower'.format(my_username), '/api/known_users', '/api/posts',
            '/api/posts/all', '/api/feed', '/api/profile', '/api/user/{}'.format(their_username)]

output_file = open("output.txt", "a")

output_file.write("Hitting all endpoints for {} nodes in network\n".format(num_nodes))

for endpoint in endpoints:
    req_url = url + endpoint
    begin = time.time()
    response = requests.get(req_url + '/')
    end = time.time()
    print('confirm the response: ' + str(response))

    output_file.write('Time it took to call {}: {}s'.format(endpoint, end-begin))