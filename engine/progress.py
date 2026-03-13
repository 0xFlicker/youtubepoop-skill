"""Resumable progress tracking for pipeline steps."""

import json
from pathlib import Path


class ProgressTracker:
    def __init__(self, progress_file: Path):
        self.file = progress_file
        self.data = self._load()

    def _load(self):
        if self.file.exists():
            return json.loads(self.file.read_text())
        return {}

    def _save(self):
        self.file.write_text(json.dumps(self.data, indent=2))

    def is_done(self, step: str) -> bool:
        return self.data.get(step) == "done"

    def mark_done(self, step: str):
        self.data[step] = "done"
        self._save()

    def invalidate(self, step: str):
        self.data.pop(step, None)
        self._save()
