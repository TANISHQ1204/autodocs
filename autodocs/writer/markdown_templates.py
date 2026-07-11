from typing import Dict

def render_overview_section(scan_data:Dict)->str:
    lines=[]
    lines.append(f"**Primary language:** {scan_data.get('primary_language') or 'Not detected'}")

    frameworks=scan_data.get("frameworks") or []
    if frameworks:
        lines.append(f"**Frameworks:** {', '.join(frameworks)}")
    lines.append(f"**Total files:** {scan_data.get('total_files',0)}")

    entry_points=scan_data.get("entry_points") or []
    if entry_points:
        lines.append(f"**Entry point:** `{entry_points[0]}`")

    return "\n\n".join(lines)

def render_api_section(routes:list)->str:
    if not routes:
        return "_No API routes detected._"
    lines=["| Method | Path | Handler | Location |", "|---|---|---|---|"]

    for route in routes:
        method=route.get("method","")
        path=route.get("path","")
        handler=route.get("handler","")
        location=f"{route.get('file','')}:{route.get('line','')}"
        lines.append(f"| {method} | {path} | `{handler}` | {location} |")

    return "\n".join(lines)

def render_full_document(scan_data:dict,diagram_text:str)->str:
    sections=[]

    sections.append("## Overview\n\n"+render_overview_section(scan_data))
    sections.append("## API Endpoints\n\n"+render_api_section(scan_data.get("routes", [])))
    sections.append("## Architecture\n\n```mermaid\n"+diagram_text+"\n```")

    return "\n\n".join(sections)