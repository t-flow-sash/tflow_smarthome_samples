#!/usr/bin/env python3
"""Local, fixed-root camera media preparation and bounded retention; no HA privilege escalation."""
import argparse
import os
import stat
from pathlib import Path

ROOT = Path('/media/demo_camera')
SUBDIRECTORIES = tuple(f'zone_{i:02}' for i in range(1, 7))
MAX_AGE_SECONDS = 7 * 86400
MAX_BYTES = 2 * 1024**3

def checked_dir(path):
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_mode & 0o077:
        raise ValueError('Refusing non-private directory or symlink')
    return path

def prepare():
    # Parent is provisioned by operator; do not traverse an attacker-supplied root.
    checked_dir(ROOT)
    for name in SUBDIRECTORIES:
        path = ROOT / name
        try:
            path.mkdir(mode=0o700)
        except FileExistsError:
            pass
        checked_dir(path)

def maintain(now=None):
    if now is None:
        now = __import__('time').time()
    checked_dir(ROOT)
    entries = []
    # Preflight all entries before deleting anything; unknown files and links fail closed.
    for name in SUBDIRECTORIES:
        folder = checked_dir(ROOT / name)
        with os.scandir(folder) as listing:
            for item in listing:
                info = item.stat(follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode) or Path(item.name).suffix.lower() not in ('.jpg','.jpeg') or info.st_nlink != 1:
                    raise ValueError('Refusing unknown media entry')
                entries.append((info.st_mtime, info.st_size, Path(item.path)))
    remaining = []
    for timestamp, size, path in entries:
        if now - timestamp > MAX_AGE_SECONDS:
            path.unlink()
        else:
            remaining.append((timestamp,size,path))
    total = sum(size for _, size, _ in remaining)
    for _, size, path in sorted(remaining):
        if total <= MAX_BYTES:
            break
        path.unlink()
        total -= size

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare','maintain'))
    args = parser.parse_args()
    if args.operation == 'prepare': prepare()
    else: maintain()

if __name__ == '__main__':
    main()
