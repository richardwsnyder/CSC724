import asyncio
import logging
from kademlia.network import Server

def kad_server_worker_thread():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    aio = asyncio.get_event_loop()
    kad = Server()

    aio.run_until_complete(kad.listen(8888))
    aio.set_debug(True)
    # run forever since we are the first node
    try:
        aio.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        kad.stop()
        aio.close()
