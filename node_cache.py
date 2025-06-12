import torch
from typing import Callable, Type
import time

LATEST     = '_cache_single'
FULL_CACHE = '_cache_all'

def log(s): print(s)

def tensor_hash(v:torch.Tensor) -> str:
    t = time.monotonic()
    r = str(hash(v.cpu().numpy().tobytes()))
    dt = t - time.monotonic()
    print(f"Cache of {v.shape} tensor took {dt:>.6}s")
    return r

def make_hash(v):
    if isinstance(v, torch.Tensor): return tensor_hash(v)
    if isinstance(v, int|float|str): return str(v)
    if isinstance(v, list|tuple): return sum( make_hash(x) for x in v )
    if isinstance(v, dict): return sum( f"{k}{make_hash(v[k])}" for k in v )
    raise TypeError(f"Cache can't hash {v}")

def wrap_function(wrappable:Callable):
    def wrapped(node, *args, **kwargs):
        hash = make_hash([args, kwargs])
        if getattr(node, LATEST, [None,None])[0] != hash:
            log('not in cache')
            result = wrappable(*args, **kwargs)
            setattr(node, LATEST, [hash,result])
        else:
            log('in cache')
        return getattr(node, LATEST)[1]
    return wrapped

'''
def wrap_function_fullcache(wrappable:Callable):
    def wrapped(node, *args, **kwargs):
        hash = make_hash([args, kwargs])
        if getattr(node, FULL_CACHE, None) is None: 
            setattr(node, FULL_CACHE, {})
        if hash not in getattr(node, FULL_CACHE):
            result = wrappable(*args, **kwargs)
            getattr(node, FULL_CACHE)[hash] = result
        return getattr(node, FULL_CACHE)[hash]
    return wrapped'''

def cached(node_class:Type):
    '''
    Decorator. Usage:
    @cached
    class MyCoolNode:
    '''
    function_name = getattr(node_class, 'FUNCTION')
    wrapped_function = wrap_function( getattr(node_class, function_name) )
    setattr(node_class, f"_cache_wrapped{function_name}", wrapped_function)
    setattr(node_class, 'FUNCTION', f"_cache_wrapped{function_name}")
    setattr(node_class, 'CATEGORY', 'cached_nodes') 
    return node_class