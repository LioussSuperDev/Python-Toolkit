import json
from typing import Optional

class ResumeSession:

    def __init__(self, save_path: str):
        self.save_path = save_path
        self._target:list[str] = []
        self._saved_target:list[str] = []
        self._state = dict()
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
                self._target = data.get("target", [])
                self._state = data.get("state", dict())
                self._saved_target = self._target
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save(self):
        with open(self.save_path, "w") as f:
            json.dump({"state": self._state, "target": list(self._saved_target)}, f, indent=2)
            
    def resume(self, progress: list[str]) -> bool:
        if not progress or progress == self._target[:len(progress)]:
            if progress == self._target:
                self._target = []
                self._state = dict()
            return True
        
        if not self._target:
            return True
        
        return False
    
    def save(self, progress: list[str]):
        if progress and progress == self._saved_target[:len(progress)]:
            return
        self._saved_target = progress
        self._save()
    
    def set_state(self, state: dict):
        self._state = state

    def get_state(self) -> dict:
        return self._state