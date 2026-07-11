import yaml
from pathlib import Path

DEFAULT_CONFIG={
    "base_branch":"main",
    "extra_ignore_dirs":[],
}

def load_config(repo_path: str)->dict:
    config_path=Path(repo_path) / ".autodocs.yml"

    if not config_path.exists():
        return dict(DEFAULT_CONFIG)

    try:
        user_config=yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return dict(DEFAULT_CONFIG)

    merged=dict(DEFAULT_CONFIG)
    merged.update(user_config)
    return merged