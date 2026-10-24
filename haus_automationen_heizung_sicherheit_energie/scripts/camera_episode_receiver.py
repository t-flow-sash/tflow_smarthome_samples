#!/usr/bin/env python3
"""Local demonstration receiver: validate completed episode metadata and select local JPEGs.

Not a Hermes gateway or AI runner. No network listener, no credentials and no delivery ACK.
Invoke only on trusted metadata; the caller owns authentication and transport.
"""
import json
import re
import stat
import sys
from datetime import datetime, timedelta
from pathlib import Path

CAMERAS = frozenset(f'zone_{i:02}' for i in range(1, 7))
FIELDS = frozenset(('event_type', 'camera', 'episode_id', 'started_at', 'ended_at', 'reason', 'snapshot_count'))
REASONS = frozenset(('recording_disabled', 'detection_ended', 'camera_unavailable'))
IDENT = re.compile(r'[0-9a-f]{32}\Z')


def prepare(payload, root=Path('/media/demo_camera')):
    if not isinstance(payload, dict) or set(payload) != FIELDS:
        raise ValueError('Invalid fields')
    if payload['event_type'] != 'camera_phase_finished' or type(payload['camera']) is not str or payload['camera'] not in CAMERAS:
        raise ValueError('Invalid event or camera')
    if not isinstance(payload['episode_id'], str) or not IDENT.fullmatch(payload['episode_id']):
        raise ValueError('Invalid episode ID')
    if type(payload['reason']) is not str or payload['reason'] not in REASONS or type(payload['snapshot_count']) is not int or not 0 <= payload['snapshot_count'] <= 100000:
        raise ValueError('Invalid reason or count')
    try:
        if any(type(payload[k]) is not str for k in ('started_at', 'ended_at')):
            raise ValueError('Timestamp type')
        start, end = (datetime.fromisoformat(payload[k]) for k in ('started_at', 'ended_at'))
        if start.utcoffset() is None or end.utcoffset() is None or not timedelta(0) <= end - start <= timedelta(days=1):
            raise ValueError('Invalid interval')
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid timestamps') from exc
    root = Path(root)
    folder = root / payload['camera']
    for directory in (root, folder):
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077:
            raise ValueError('Invalid directory permissions')
    matches = []
    # Never resolve client-provided paths. Validate every entry before returning any path.
    for path in folder.iterdir():
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Non-regular media entry')
        match = re.fullmatch(r'(\d{8}T\d{12})_([0-9a-f]{32})_([1-9]\d*)\.jpg', path.name)
        if match and match.group(2) == payload['episode_id']:
            if info.st_size < 4 or info.st_size > 20 * 1024 * 1024:
                raise ValueError('Invalid JPEG size')
            with path.open('rb') as stream:
                if stream.read(2) != b'\xff\xd8':
                    raise ValueError('Invalid JPEG signature')
                stream.seek(-2, 2)
                if stream.read() != b'\xff\xd9':
                    raise ValueError('Incomplete JPEG')
            matches.append((int(match.group(3)), str(path)))
    matches.sort()
    paths = [p for _, p in matches]
    if len(paths) > 12:
        paths = [paths[i * (len(paths) - 1) // 11] for i in range(12)]
    return {**payload, 'event_type': 'validated_camera_episode', 'reported_snapshot_count': payload['snapshot_count'],
            'available_count': len(matches), 'sample_paths': paths}


if __name__ == '__main__':
    try:
        result = prepare(json.load(sys.stdin))
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'Rejected: {type(exc).__name__}', file=sys.stderr)
        sys.exit(1)
