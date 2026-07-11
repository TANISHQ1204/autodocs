import re
from pathlib import Path
from typing import Dict

def _marker_start(section_id:str)->str:
    return f"<!-- AUTODOCS:{section_id}:START -->"

def _marker_end(section_id:str)->str:
    return f"<!-- AUTODOCS:{section_id}:END -->"

def _wrap_section(section_id:str, content:str)->str:
    return f"{_marker_start(section_id)}\n{content}\n{_marker_end(section_id)}"

def _upsert_section(existing_text:str, section_id:str, new_content:str)->str:
    start_marker=_marker_start(section_id)
    end_marker=_marker_end(section_id)
    wrapped=_wrap_section(section_id, new_content)
    pattern=re.escape(start_marker)+r".*?"+re.escape(end_marker)

    if re.search(pattern, existing_text, flags=re.DOTALL):
        return re.sub(pattern, wrapped, existing_text, flags=re.DOTALL)
    else:
        return existing_text.rstrip()+"\n\n"+wrapped+"\n"
    
def write_sections(readme_path:Path, sections:Dict[str,str])->None:
    if readme_path.exists():
        text=readme_path.read_text(encoding="UTF-8")
    else:
        text=f"# {readme_path.parent.resolve().name}\n"
    
    for section_id, content in sections.items():
        text=_upsert_section(text,section_id,content)

    readme_path.write_text(text,encoding="UTF-8")
