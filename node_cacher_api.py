from .node_cacher import convert_to_caching, is_caching
from server import PromptServer
import json
from aiohttp import web

@PromptServer.instance.routes.post('/cg_cache_node_request')
async def request(d):
    try:
        data = await d.post()
        convert_to_caching(data.get('type'))
        return web.json_response({"response":True})
    except Exception as e:
        return web.json_response({"response":False})

@PromptServer.instance.routes.post('/cg_cache_node_query')
async def query(d):
    try:
        data = await d.post()
        return web.json_response({"response":is_caching(data.get('type'))})
    except Exception as e:
        return web.json_response({"response":False})