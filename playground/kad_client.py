import asyncio
import logging
import requests
from kademlia.network import Server

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

aio = asyncio.get_event_loop()

kad = Server()
aio.run_until_complete(kad.listen(8889))

aio.run_until_complete(kad.bootstrap([("127.0.0.1", 8888)]))

aio.run_until_complete(asyncio.sleep(2))
# get the value associated with "my-key" from the network
result = aio.run_until_complete(kad.get("cwheezer"))
print("Client: " + str(result))

# Now that we have gotten the users address from the network,
# lets get their json profile
response = requests.get(str(result) + "/")
print(response.json())

# run forever since we are the first node
try:
    aio.run_forever()
except KeyboardInterrupt:
    pass
finally:
    kad.stop()
    aio.close()
