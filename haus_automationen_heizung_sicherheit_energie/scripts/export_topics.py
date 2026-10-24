"""Deterministic, individually copyable views of the canonical package object.

Do not parse and re-dump packages/haus.yaml: both outputs are rendered from
exactly the same in-memory object in build.py (including !secret tags).
"""
from pathlib import Path
import re
import yaml

class Secret(str):
    """Preserve HA !secret tags in package and individual components."""


yaml.SafeDumper.add_representer(
    Secret, lambda dumper, value: dumper.represent_scalar('!secret', str(value)))

TOPICS = ('heizung', 'sicherheit', 'energie')
DOMAINS = ('automation', 'input_boolean', 'input_number', 'input_text',
           'template', 'sensor', 'script', 'shell_command', 'rest_command')


def topic(domain, key):
    if domain == 'automation':
        if key in ('wolf_shadow', 'kalender_abwesenheit'):
            return 'heizung'
        if key in ('wallbox_freigabe', 'ladekosten'):
            return 'energie'
        return 'sicherheit'
    if domain == 'input_boolean':
        if key in ('demo_bt_freigabe', 'demo_wolf_freigabe', 'demo_kalender_ownership',
                   'demo_wolf_ownership', 'demo_shadow'):
            return 'heizung'
        if key in ('demo_laden_freigabe', 'demo_ladesitzung', 'demo_lade_zaehler_gueltig'):
            return 'energie'
        return 'sicherheit'
    if domain == 'input_number':
        return 'energie'
    if domain == 'input_text':
        return 'heizung'
    if domain in ('template', 'sensor'):
        return 'energie' if ('Preis' in key or 'EcoFlow' in key) else 'heizung'
    return 'sicherheit'


def pieces(package):
    """Yield (domain, key, standalone domain value), no hidden shared values."""
    for domain in DOMAINS:
        value = package[domain]
        if domain == 'automation':
            for item in value:
                yield domain, item['id'].removeprefix('public_'), [item]
        elif domain == 'template':
            for block in value:
                for kind, items in block.items():
                    for item in items:
                        yield domain, item['name'], [{kind: [item]}]
        elif domain == 'sensor':
            for item in value:
                yield domain, item['name'], [item]
        else:
            for key, item in value.items():
                yield domain, key, {key: item}


def filename(domain, key):
    if domain in ('template', 'sensor'):
        key = key.lower().replace(' ', '_')
    if not re.fullmatch(r'[a-z0-9_]+', key):
        raise ValueError(f'Unsafe component name: {key!r}')
    return f'{key}.yaml'


def render(package):
    result = {}
    for domain, key, value in pieces(package):
        path = Path('themen') / topic(domain, key) / domain / filename(domain, key)
        if path in result:
            raise ValueError(f'Duplicate export: {path}')
        result[path] = '# Generiert mit scripts/build.py; nur fiktive Entity-IDs.\n' + yaml.safe_dump(
            value, allow_unicode=True, sort_keys=False, width=110)
    return result


def write(root, package):
    destination = root / 'themen'
    expected = render(package)
    # Only remove stale generated YAML; leave any human-owned non-YAML files alone.
    for path in destination.rglob('*.yaml') if destination.exists() else ():
        if path.relative_to(root) not in expected:
            path.unlink()
    for relative, text in expected.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    return expected
