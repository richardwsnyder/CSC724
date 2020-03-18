# straight from the quickstart
import json
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    profile = {}
    profile['username'] = 'cwheezer'
    profile['fullname'] = 'Carl Wheezer'
    return web.Response(text=json.dumps(profile))

app = web.Application()
app.add_routes(routes)

web.run_app(app)
