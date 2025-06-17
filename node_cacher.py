import torch
from typing import Callable, Type, Optional
import time
import types
from nodes import NODE_CLASS_MAPPINGS

CACHE_ATTR_NAME      = '_cache_all'
FLAG                 = '_is_caching'
FUNCTION_NAME_PREFIX = '_cache_wrapped'
LOGGING              = True

def log(s): 
    if LOGGING: print(s)

def tensor_hash(v:torch.Tensor) -> int:
    t = time.monotonic()
    r = hash(v.cpu().numpy().tobytes())
    dt = t - time.monotonic()
    log(f"Cache of {v.shape} tensor took {1000*dt:>.6f}ms")
    return r

def make_hash(v) -> int:
    if isinstance(v, torch.Tensor): return tensor_hash(v)
    if isinstance(v, list|tuple):   return sum( make_hash(x) for x in v )
    if isinstance(v, dict):         return sum( hash(f"{k}{make_hash(v[k])}") for k in v )

    try: 
        return hash(v)
    except TypeError:
        log(f"Using hash(str()) for {v}")
        return hash(str(v))
    
class Cacher:
    def __init__(self, limit=4):
        self.entries = []
        self.limit = limit

    def _find(self, key):
        for i,(k,e) in enumerate(self.entries):
            if key==k: return i
        return None

    def retrieve(self, key): 
        index = self._find(key)
        log( "in cache" if index is not None else "not in cache" )
        return self.entries[index][1] if index is not None else None

    def insert(self, key, value):
        self.entries.append((key,value))
        if len(self.entries)>self.limit:
            self.entries = self.entries[1:]


def wrap_function_fullcache(wrappable:Callable) -> Callable:
    def wrapped(node, *args, **kwargs):
        hash = make_hash([args, kwargs])
        if getattr(node, CACHE_ATTR_NAME, None) is None: 
            setattr(node, CACHE_ATTR_NAME, Cacher())
        cache:Cacher = getattr(node, CACHE_ATTR_NAME)
        result = cache.retrieve(hash)
        if result is None:
            result = wrappable(node, *args, **kwargs)
            cache.insert(hash, result)
        return result

    return wrapped

def created_cached_version(class_type:str):
    if getattr(class_type, FLAG, False): return
    class_to_wrap = NODE_CLASS_MAPPINGS[class_type]
    converted = create_caching_node(class_to_wrap)
    if converted:
        NODE_CLASS_MAPPINGS[f"cached_{class_type}"] = create_caching_node(class_to_wrap)

def convert_to_caching(class_type:str):
    if getattr(class_type, FLAG, False): return
    class_to_wrap = NODE_CLASS_MAPPINGS[class_type]
    converted = create_caching_node(class_to_wrap, new_category=class_to_wrap.CATEGORY)
    if converted:
        NODE_CLASS_MAPPINGS[class_type] = converted
    return converted is not None

def is_caching(class_type:str) -> bool:
    class_to_wrap = NODE_CLASS_MAPPINGS[class_type]
    return getattr(class_to_wrap, FLAG, False)
    
def create_caching_node(class_to_wrap:Type, new_name:Optional[str]=None, new_category:Optional[str]=None) -> Type:
    '''
    `class_to_wrap:Type`         the class to be wrapped
    `new_name:Optional[str]`     the name of the new class. If `None`, cached_[wrapped class name] is used
    `new_category:Optional[str]` the category of the new class. If `None`, 'cached_nodes' is used

    returns a new Type which is a subclass of `class_to_wrap`
    '''
    if getattr(class_to_wrap, FLAG, False): 
        print(f"{class_to_wrap.__name__} already has caching")
        return None
    new_name = new_name or f"cached_{class_to_wrap.__name__}"
    if new_name in globals()['NODE_CLASS_MAPPINGS']: 
        print(f"{class_to_wrap.__name__} already wrapped as {new_name}")
        return None
    print(f"Wrapping {class_to_wrap.__name__} as {new_name}")
    new_class = types.new_class(new_name, (class_to_wrap,))
    function_name = getattr(new_class, 'FUNCTION')
    wrapped_function = wrap_function_fullcache( getattr(new_class, function_name) )
    setattr(new_class, f"{FUNCTION_NAME_PREFIX}{function_name}", wrapped_function)
    setattr(new_class, 'FUNCTION', f"{FUNCTION_NAME_PREFIX}{function_name}")
    setattr(new_class, 'CATEGORY', new_category or 'cached_nodes') 
    setattr(new_class, FLAG, True)

    return new_class