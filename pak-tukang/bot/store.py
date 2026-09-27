import json
from pathlib import Path
DATA=Path("data"); DATA.mkdir(exist_ok=True)
def read(name, default):
    p=DATA/name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        p.write_text(json.dumps(default,ensure_ascii=False,indent=2),encoding="utf-8")
        return default
def write(name, data):
    (DATA/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
