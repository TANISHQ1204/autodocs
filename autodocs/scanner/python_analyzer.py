"""
python_analyzer.py

Parses Python files using the `ast` module to extract:
  - function definitions (name, file, line number)
  - what each function calls (for the call graph)

Output shape is intentionally generic (not Python-specific field names),
so a future js_analyzer.py can produce matching structures.
"""

import ast
from dataclasses import dataclass,field
from pathlib import Path
from typing import List

@dataclass
class FunctionInfo:
    name:str
    file:str
    line:int
    calls:List[str]=field(default_factory=list)

@dataclass
class RouteInfo:
    method:str
    path:str
    handler:str
    file:str
    line:int

FLASK_ROUTE_DECORATORS={"route","get","post","put","patch","delete"}

def extract_functions(filepath:Path, root:Path)->List[FunctionInfo]:
    try:
        source=filepath.read_text(encoding="UTF-8", errors="ignore")
        tree=ast.parse(source)
    except(SyntaxError,OSError):
        return[]
    
    rel_path=str(filepath.relative_to(root))
    functions=[]

    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            info=FunctionInfo(
                name=node.name,
                file=rel_path,
                line=node.lineno,
            )
            info.calls=_extract_calls(node)
            functions.append(info)
    _filter_internal_calls(functions)
    return functions

def _extract_calls(func_node:ast.AST)->List[str]:
    calls=[]
    for node in ast.walk(func_node):
        if isinstance(node,ast.Call):
            name=_get_call_name(node.func)
            if name:
                calls.append(name)
    return calls

def _get_call_name(node:ast.AST)->str|None:
    if isinstance(node,ast.Name):
        return node.id
    if isinstance(node,ast.Attribute):
        return node.attr
    return None

def _filter_internal_calls(functions:List[FunctionInfo])->None:
    known_names={fn.name for fn in functions}
    for fn in functions:
        fn.calls=[c for c in fn.calls if c in known_names]

def extract_routes(filepath:Path,root:Path)->List["RouteInfo"]:
    try:
        source=filepath.read_text(encoding="UTF-8",errors="ignore")
        tree=ast.parse(source)
    except(SyntaxError,OSError):
        return []
    
    rel_path=str(filepath.relative_to(root))
    routes=[]

    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            routes.extend(_extract_routes(node,rel_path))

    return routes

def _extract_routes(node:ast.FunctionDef,rel_path:str)->List[RouteInfo]:
    routes=[]
    for decorator in node.decorator_list:
        if not isinstance(decorator,ast.Call):
            continue
        if not isinstance(decorator.func,ast.Attribute):
            continue

        decorator_name=decorator.func.attr
        if decorator_name not in FLASK_ROUTE_DECORATORS:
            continue

        path=_get_string_arg(decorator.args)
        if path is None:
            continue
        method=_get_route_method(decorator_name,decorator.keywords)

        routes.append(RouteInfo(
            method=method,
            path=path,
            handler=node.name,
            file=rel_path,
            line=node.lineno,
        ))
    return routes

def _get_string_arg(args:list)->str|None:
    if args and isinstance(args[0],ast.Constant) and isinstance(args[0].value,str):
        return args[0].value
    return None

def _get_route_method(decorator_name:str,keywords:list)->str:
    if decorator_name!="route":
        return decorator_name.upper()
    
    for kw in keywords:
        if kw.arg=="methods" and isinstance(kw.value,ast.List):
            for elt in kw.value.elts:
                if isinstance(elt,ast.Constant):
                    return elt.value
    return "GET"