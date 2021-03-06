# global sharing across modules

# when running python manage.py this will
# stop interpreter from complaining about kad_server
import sys
sys.path.insert(1, '../')
import multiprocessing
import kad_server
import os
import toml

def get_config():
    global config
    if config == -1:
        try:
            path = os.environ['SAD_CONFIG_FILE']
            print('getting config from ' + path)
            with open(path, 'r') as content_file:
                global kad_port
                config = toml.load(content_file)
                kad_port = config['connection']['network_port']
        # if not running sad.py, os.environ[] won't insert
        # the profile into the dictionary. Catch the KeyError 
        except KeyError:
            print("os.environ[] doesn't containt the key SAD_CONFIG_FILE")

def get_kad_server():
    global kad_proc
    global pipe

    if kad_proc == -1:
        pipe, child_pipe = multiprocessing.Pipe(duplex=True)

        # The kademlia network replaces the central servers of a system like naptser,
        # it is used by clients to find out where the user profiles are hosted.
        kad_proc = multiprocessing.Process(target=kad_server.kad_server_worker_thread, args=(child_pipe,))
        kad_proc.start()

        # these definitions need to be in a method so
# they aren't redefined
def init():
    global config
    global kad_port
    global kad_proc
    
    config = -1
    kad_port = -1
    kad_proc = -1

    get_kad_server()
    get_config()
