import json
import os
import subprocess
import tempfile
from pathlib import Path
import shlex
from typing import Optional

def save_data(data, full_path:Optional[str] = None, folder:Optional[str] = None, file:Optional[str] = None):
    if full_path == None:
        if not os.path.isdir(folder):
            os.makedirs(folder)
        full_path = os.path.join(folder, file)
        
    with open(full_path, "w+") as f:
        json.dump(data, f)
        
def load_data(full_path = None, folder = None, file = None):
    if full_path == None:
        full_path = os.path.join(folder, file)
        
    with open(full_path, "r") as f:
        return json.load(f)
    
def edit_in_editor(initial_text: str = "", ignore_lines=0, path=None) -> str:
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"
    path_none = path is None
    if path is None:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".temp.txt", delete=False, encoding="utf-8") as f:
            path = Path(f.name)
            f.write(initial_text)
            f.flush()
    else:
        with open(path, 'w+') as f:
            path = Path(f.name)
            f.write(initial_text)
            f.flush()
    try:
        cmd = shlex.split(editor) + [str(path)]
        subprocess.run(cmd, check=False)
        return "\n".join(path.read_text(encoding="utf-8").splitlines()[ignore_lines:])
    finally:
        try:
            if path_none:
                path.unlink(missing_ok=True)
        except Exception:
            pass

def real_path(path_str: str) -> str:
    return str(
        Path(path_str.strip('"').strip("'"))
        .expanduser()
        .resolve(strict=False)
    )