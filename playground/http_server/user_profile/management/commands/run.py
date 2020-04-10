from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command

import os
import multiprocessing
import toml

import kad_server
import config as global_config

def get_config():
    path = os.environ['SAD_CONFIG_FILE']
    config = ''
    with open(path, 'r') as content_file:
        config = toml.load(content_file)

    return config

class Command(BaseCommand):
    help = 'run both servers'

    def add_arguments(self, parser):
        parser.add_argument('config_file', type=str, help='toml config file')

    def handle(self, config_file='', *args, **kwargs):

        # Launch processes for the kademlia network and the http server
        os.environ['SAD_CONFIG_FILE'] = config_file
        config = get_config()
        addrport = '0.0.0.0:' + str(config['connection']['profile_port'])

        if os.environ.get('RUN_MAIN') != 'true':
            print('handling the run command')

            global_config.pipe, child_pipe = multiprocessing.Pipe()
        
            # The kademlia network replaces the central servers of a system like naptser,
            # it is used by clients to find out where the user profiles are hosted.
            kad_proc = multiprocessing.Process(target=kad_server.kad_server_worker_thread, args=(child_pipe,))
            kad_proc.start()

        call_command('runserver', addrport, *args, **kwargs)
