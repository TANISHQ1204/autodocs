from typing import List,Dict

def build_call_graph_diagram(functions:List[Dict],routes:List[Dict]=None)->str:
    lines=["graph TD"]

    for fn in functions:
        caller=fn["name"]
        for callee in fn["calls"]:
            lines.append(f"{caller} --> {callee}")

    if routes:
        for i,route in enumerate(routes):
            node_id=f"route_{i}"
            label=f"{route['method']} {route['path']}"
            label=label.replace("<","&lt;").replace(">","&gt;")
            lines.append(f'{node_id}["{label}"] --> {route["handler"]}')

    return "\n".join(lines)