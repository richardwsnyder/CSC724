# straight from the quickstart
import json
import asyncio
import kad_client
from aiohttp import web
from kademlia.network import Server

kad_port = -1
routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    profile = {}
    profile['username'] = 'cwheezer'
    profile['fullname'] = 'Carl Wheezer'
    return web.Response(text=json.dumps(profile))

@routes.get('/user/{username}')
async def get_user_profile(request):
    kad = Server()
    await kad.listen(8889)
    print('querying network at {}:{}', 'localhost', kad_port)
    await kad.bootstrap([('localhost', kad_port)])

    profile = await kad_client.get_user_profile(kad, request.match_info['username'])
    print(profile.json())
    kad.stop()
    return web.Response(text=str(profile.json()))

# apparently we need to use the asyncio application
# runner to set the address... weird
async def run_site(args, app):
    runner = web.AppRunner(app)
    await runner.setup()
    print("Running http_server at 0.0.0.0:" + str(args['profile_port']))
    site = web.TCPSite(runner, '0.0.0.0', args['profile_port'])
    await site.start()
    print("site started")

# entrypoint from sad.py
def http_server_worker_thread(args):
    global kad_port
    kad_port = args['network_port']
    aio = asyncio.get_event_loop()

    app = web.Application()
    app.add_routes(routes)
    aio.run_until_complete(run_site(args, app))
    aio.run_forever()

