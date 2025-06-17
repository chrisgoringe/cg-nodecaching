from .node_cacher import convert_to_caching, is_caching
from server import PromptServer
import os
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
    
@PromptServer.instance.routes.post('/cg_cache_node_init')
async def init(d):
    try:
        with open(os.path.join(os.path.dirname(__file__),'classes_to_cache.txt'), 'r') as f:
            for line in f.readlines():
                if not line.startswith('#'):
                    line = line.strip()
                    if line:
                        try:
                            converted = convert_to_caching(line)
                            if converted: print(f"Cacher: Converted {line}")
                        except KeyError:
                            print(f"Cacher: {line} not found to convert")
                        except Exception as e:
                            print(f"Cacher: Failed to convert {line} because {type(e).__name__}")
    except:
        print(f"Cacher: problem reading classes_to_cache.txt")
    return web.json_response({})