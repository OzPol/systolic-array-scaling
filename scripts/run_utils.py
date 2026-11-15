"""Allocate new output directories without replacing an earlier execution."""
from datetime import datetime, timezone
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def new_run(parent=None, prefix='run'):
    parent = Path(parent or ROOT / 'results/raw')
    parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return Path(tempfile.mkdtemp(prefix=f'{prefix}_{stamp}_', dir=parent)).resolve()
