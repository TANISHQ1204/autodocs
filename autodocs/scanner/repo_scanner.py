"""
repo_scanner.py

Static-analysis pass over a repository. Walks the file tree and produces a
structured summary: languages used, frameworks detected, entry points, and
dependencies. This is Day 1's output — no code parsing yet, that's Day 2.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict 
from typing import Dict, List, Optional
import json
import os 
from pathlib import Path
import tomllib
from .python_analyzer import extract_functions,extract_routes

DEFAULT_IGNORE_DIRS={
    ".git",
    "node_modules",
    "venv", ".venv", "env",
    "__pycache__",
    "dist", "build",
    ".next", ".nuxt",
    "target",       
    "vendor",       
    ".idea", ".vscode",
    "coverage",
    ".pytest_cache", ".mypy_cache",
}

EXT_TO_LANGUAGE={
    ".py": "Python", ".pyi": "Python",
    ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".cc": "C++", ".hpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".sh": "Shell",
}

ENTRY_POINT_CANDIDATES = [
    "main.py", "app.py", "manage.py", "wsgi.py", "asgi.py",
    "index.js", "server.js", "app.js", "main.js",
    "index.ts", "server.ts", "main.ts",
    "main.go",
    "cli.py",
    "__main__.py",
]

MANIFEST_FILES = {
    "package.json": "Node/JavaScript",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "go.mod": "Go",
}

FRAMEWORK_SIGNATURES = {
    "package.json": {
        "Express": ["\"express\""],
        "Next.js": ["\"next\""],
        "React": ["\"react\""],
    },
    "requirements.txt": {
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "Django": ["django"],
    },
    "pyproject.toml": {
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "Django": ["django"],
    },
}

@dataclass
class ScanResult:
    root:str
    total_files:int=0
    total_dirs:int=0
    languages:Dict[str,int]=field(default_factory=dict)
    primary_language:Optional[str]=None
    manifest_files:List[str]=field(default_factory=list)
    frameworks:List[str]=field(default_factory=list)
    entry_points:List[str]=field(default_factory=list)
    dependencies:Dict[str,List[str]]=field(default_factory=dict)
    functions:List[dict]=field(default_factory=list)
    routes:List[dict]=field(default_factory=list)

    def to_dict(self)->dict:
        return asdict(self)
    
    def to_json(self, indent:int=2)->str:
        return json.dumps(self.to_dict(),indent=indent)
    
class RepoScanner:
    def __init__(self,root:str,ignore_dirs:set|None=None):
        self.root=Path(root).resolve()
        self.ignore_dirs=ignore_dirs or set(DEFAULT_IGNORE_DIRS)

    def scan(self)->ScanResult:
        result=ScanResult(root=str(self.root))
        language_counts:Dict[str,int]={}

        for dirpath,dirnames,filenames in os.walk(self.root):
            dirnames[:]=[d for d in dirnames if d not in self.ignore_dirs]

            result.total_dirs+=1
            for fname in filenames:
                result.total_files+=1
                fpath=Path(dirpath)/fname
                ext=fpath.suffix.lower()
                lang=EXT_TO_LANGUAGE.get(ext)
                if lang:
                    language_counts[lang]=language_counts.get(lang,0)+1

                if fname in MANIFEST_FILES:
                    result.manifest_files.append(str(fpath.relative_to(self.root)))
                    self._inspect_manifest(fpath,fname,result)

                if ext==".py":
                    for fn in extract_functions(fpath,self.root):
                        result.functions.append(asdict(fn))
                    for route in extract_routes(fpath,self.root):
                        result.routes.append(asdict(route))
        result.languages=dict(sorted(language_counts.items(),key=lambda kv:-kv[1]))
        if result.languages:
            result.primary_language=next(iter(result.languages))
        
        result.entry_points=self._find_entry_points()
        result.frameworks=sorted(set(result.frameworks))

        return result

    def _find_entry_points(self)->list[str]:
        found=[]
        for candidate in ENTRY_POINT_CANDIDATES:
            if(self.root/candidate).exists():
                found.append(candidate)
        return found
    
    def _inspect_manifest(self,fpath:Path,fname:str,result:ScanResult)->None:
        try:
            text=fpath.read_text(encoding="utf-8",errors="ignore")
        except OSError:
            return
        
        rel=str(fpath.relative_to(self.root))

        if fname=="requirements.txt":
            deps=[ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
            result.dependencies[rel]=deps
        elif fname=="package.json":
            try:
                data=json.loads(text)
                deps=list(data.get("dependencies",{}).keys())+list(data.get("devDependencies",{}).keys())
                result.dependencies[rel]=deps
            except json.JSONDecodeError:
                pass
        elif fname=="pyproject.toml":
            try:
                data=tomllib.loads(text)
                deps=data.get("project",{}).get("dependencies",[])
                result.dependencies[rel]=deps
            except Exception:
                pass
        
        sigs=FRAMEWORK_SIGNATURES.get(fname,{})
        lowered=text.lower()
        for framework,needles in sigs.items():
            if any(needle.lower() in lowered for needle in needles):
                result.frameworks.append(framework)