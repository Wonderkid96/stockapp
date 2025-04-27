import os
import yaml

def load_config(path="config/settings.yaml"):
    with open(path) as f:
        raw = yaml.safe_load(f)
    # expand env vars
    def expand(v):
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            return os.getenv(v[2:-1], "")
        return v
    return {k: {ik: expand(iv) for ik, iv in v.items()} for k, v in raw.items()} 