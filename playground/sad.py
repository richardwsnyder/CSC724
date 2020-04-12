import os
import sys
# unused imports
# import multiprocessing
# import argparse

# import kad_server
# import kad_client
# import http_server
import subprocess
import toml

def get_config():
    path = os.environ['SAD_CONFIG_FILE']
    print(path)
    config = ''
    with open(path, 'r') as content_file:
        config = toml.load(content_file)

    print(config)
    return config

# Launch processes for the kademlia network and the http server
os.environ['SAD_CONFIG_FILE'] = sys.argv[1]
os.environ['PYTHONPATH'] = '.'
config = get_config()

# once their ip:port address is looked up in the kademlia network, the
# user profile needs to answer http requests so that clients can get
# data. This http server does just that.
#
# --noreload is absolutely required or else the global malarkey i'm
# doing will be messed up.

# might want to remove python3.7 dependency, but will deal with that
# at a later time

# runserver is a django command to start a server
http_proc = subprocess.run(
    [
        'python3.7',
        'http_server/manage.py',
        'runserver',
        '0.0.0.0:' + str(config['connection']['profile_port']),
        '--noreload'
    ],
    check=False
)
