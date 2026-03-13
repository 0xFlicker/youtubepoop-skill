"""YTP Engine — modular video generation capabilities."""

import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent


def get_key(name):
    """Retrieve a secret from doppler. Falls back to env vars."""
    import os
    env_val = os.environ.get(name)
    if env_val:
        return env_val
    r = subprocess.run(
        ["doppler", "secrets", "get", name, "--plain"],
        capture_output=True, text=True, cwd=str(PROJECT_DIR),
    )
    return r.stdout.strip()
