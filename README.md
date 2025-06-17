# Node Caching

*Add a cache to any ComfyUI node type.*

ComfyUI does a fairly good job of deciding whether a node needs to be executed. But as workflows get more
complicated, especially with switches, filters, and other forms of conditional execution, there are times
when it isn't possible to tell at the start of a run whether the inputs of a node might have changed.

Enter node caching.

Node caching creates a fingerprint from the actual runtime values of the inputs, and 
compares it to a cache of past inputs for which it has stored the output. 
If there is a match, the output is sent without the node being executed.

There's no point doing this for nodes which are really quick - but if you have multiple samplers and a conditional workflow, it might really help!

This custom node set doesn't contain any nodes - instead it allows you to add caching to pretty much any existing node.

## How to use

Right click on a node and select `Convert to caching`. The title of the node (and all other nodes of the same type)
will have `(caching)` added to it.

That's it. Until you restart the server, all instances of this node type (in all workflows...) has caching added.

When you restart the server, the caching will be gone; caching isn't permanent, and it isn't saved with the workflow.

If you want a particular node type to always be cached, see below.

## Important caveats

Please read these before you say something isn't working right...

- the modification happens in the backend, and applies to every instance of that node type until the server is restarted
    - so if you add caching to a KSampler node, all KSampler nodes get their own cache, in all workflows
    - and when the server is restarted, the caching is removed, and you need to re-add it (see below for how to make things permanent)
- the cache only keeps the last four unique inputs (in order to keep memory use to a reasonable limit).
- the cache keeps a reference to the output, not a copy. So if the object gets modified downstream, behaviour won't be as expected.
- if a node's output might depend on other factors (external files, api calls, unseeded randoms) the cache won't know that. So it'll resend output.
- fingerprinting can result in false positives (a match even when something has changed). 
If this happens it probably indicates some Comfy object needs to be fingerprinted better, so please let me know!

## Picking node types to always cache

If you want a particular node type to always be cached, you can add it to `classes_to_cache.txt`. 
When you reload the webpage, all node types named in this file will have caching added to them 
if they haven't got it already.

## Developer options

If you develop your own custom nodes, you can use this code to add caching to them. The most general way 
is to import `create_caching_node`:

```python
def create_caching_node(class_to_wrap:Type, new_name:Optional[str]=None, new_category:Optional[str]=None) -> Type
```
```
class_to_wrap:Type         the class to be wrapped
new_name:Optional[str]     the unique name of the new class. If `None`, cached_[wrapped class name] is used
new_category:Optional[str] the category of the new class. If `None`, 'cached_nodes' is used

returns a new Type object which is a subclass of your node
```

You use this to create a wrapped subclass of your existing node:

```python
class MySlowNode:
    lots of code

NODE_CLASS_MAPPINGS = {
    "My Slow Node" : create_caching_node(MySlowNode, new_category='my_node_category'),
}

__all__ = ["NODE_CLASS_MAPPINGS", ]
```

## Hashing

The fingerprint is generated as follows:

- for each input in `kwargs`
    - hash the value of the input
        - anything that supports `hash()` uses `hash(v)`
            - EXCEPT: `torch.Tensor` uses `hash(v.cpu().numpy().tobytes())`
        - anything else uses hash(str(v))
    - create a string by concatenating the name of the input with the hash the value
    - calculate the hash of that string
- sum over all the inputs

So that's `sum(hash(f"{k}{h(kwargs[k])}") for k in kwargs)`
