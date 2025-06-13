from .node_cacher_api import request, query
from .node_cacher import convert_to_caching
import os

try:
    with open(os.path.join(os.path.dirname(__file__),'classes_to_cache.txt'), 'r') as f:
        for line in f.readlines():
            if not line.startswith('#'):
                line = line.strip()
                if line:
                    try:
                        convert_to_caching(line)
                        print(f"Cacher: Converted {line}")
                    except KeyError:
                        print(f"Cacher: {line} not found to convert")
                    except Exception as e:
                        print(f"Cacher: Failed to convert {line} because {type(e).__name__}")
except:
    print(f"Cacher: problem reading classes_to_cache.txt")

NODE_CLASS_MAPPINGS = { }
WEB_DIRECTORY = "./js"

__all__ = [ "WEB_DIRECTORY", "NODE_CLASS_MAPPINGS", ]
