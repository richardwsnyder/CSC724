from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.management import call_command

import os
import toml
import global_config

def get_config():
    path = os.environ['SAD_CONFIG_FILE']
    config = ''
    with open(path, 'r') as content_file:
        config = toml.load(content_file)

    return config

class Command(BaseCommand):
    help = 'run both servers'

    def handle(self, config_file='', *args, **kwargs):

        if os.environ.get('RUN_MAIN') != 'true':
            print('handling the run command')
            # Launch processes for the kademlia network and the http server
            #global_config.init()


        config = get_config()
        addrport = '0.0.0.0:' + str(config['connection']['profile_port'])
            
        kwargs['noreloa'] = True
        call_command('runserver', addrport, *args, **kwargs)
