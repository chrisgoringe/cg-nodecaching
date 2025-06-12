from nodes import KSampler
from .node_cache import cached

_KS = cached(KSampler)

NODE_CLASS_MAPPINGS = {
    "Cached KSampler":_KS,
}

__all__ = [ "NODE_CLASS_MAPPINGS", ]
