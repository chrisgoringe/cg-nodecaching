import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js" 

app.registerExtension({
	name: "cg.cache_nodes",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions
        nodeType.prototype.getExtraMenuOptions = function(_, options) {
            getExtraMenuOptions?.apply(this, arguments);
            if (!this._is_caching) {
                options.push(
                    {
                        content: "Convert to caching",
                        callback: async () => {
                            const data = await call_server(this.type, "/cg_cache_node_request")

                            if (data.response) {
                                nodeType.prototype._is_caching = true
                                app.graph.nodes.filter( (node) => (node.type==this.type) ).forEach( (node) => {node._is_caching = true} )
                            } else {
                                console.log(`Failed to convert ${this.type}`)
                            }
                        }
                    }
                )
            }
        }


        const data = await call_server(nodeType.comfyClass, "/cg_cache_node_query")
        if (data.response) nodeType.prototype._is_caching = true

    },

    async nodeCreated(node) {
        const original_getTitle = node.getTitle;
        node.getTitle = function() {
            const t = original_getTitle.bind(node)()
            if (node._is_caching) return `${t} (caching)`
            else return t;
        }
    },
})

async function call_server(type, method) {
    const body = new FormData();
    body.append('type', type);
    const response = await api.fetchApi(method, { method: "POST", body, });
    const data = await response.json()
    return data
}