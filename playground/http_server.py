# straight from the quickstart
import json
import asyncio
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    profile = {}
    profile['username'] = 'cwheezer'
    profile['fullname'] = 'Carl Wheezer'
    return web.Response(text=json.dumps(profile))

# apparently we need to use the asyncio application
# runner to set the address... weird
async def run_site(args, app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, args['profile_addr'])
    await site.start()

# entrypoint from sad.py
def http_server_worker_thread(args):
    aio = asyncio.get_event_loop()
    app = web.Application()
    app.add_routes(routes)
    aio.run_until_complete(run_site(args, app))

