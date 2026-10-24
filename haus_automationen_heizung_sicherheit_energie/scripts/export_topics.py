"""Deterministic, individually copyable views of the canonical package object.

Do not parse and re-dump packages/haus.yaml: both outputs are rendered from
exactly the same in-memory object in build.py (including !secret tags).
"""
from contextlib import ExitStack
import os
from pathlib import Path
import re
import secrets
import stat
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


# Ownership is deliberately narrower than the .yaml extension. A handwritten
# YAML file must never be deleted or overwritten by the exporter.
GENERATED_HEADER = b'# Generiert mit scripts/build.py; nur fiktive Entity-IDs.\n'
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC


def _directory(parent, name, stack, *, create=False):
    if create:
        try:
            os.mkdir(name, dir_fd=parent)
        except FileExistsError:
            pass
    try:
        fd = os.open(name, DIR_FLAGS, dir_fd=parent)
    except OSError as error:
        raise ValueError(f'Unsafe export directory: {name}') from error
    return stack.enter_context(_closing_fd(fd))


class _closing_fd:
    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        return self.fd

    def __exit__(self, *_):
        os.close(self.fd)


def _owned_file(directory, name):
    """Read only an ordinary generated file, never follow a leaf symlink."""
    try:
        fd = os.open(name, FILE_FLAGS, dir_fd=directory)
    except OSError as error:
        raise ValueError(f'Unsafe export file: {name}') from error
    with os.fdopen(fd, 'rb') as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError(f'Unsafe export file: {name}')
        return source.read(len(GENERATED_HEADER)) == GENERATED_HEADER


def _unchanged_file(directory, name, content):
    """Byte-identical existing exports need no path mutation."""
    try:
        fd = os.open(name, FILE_FLAGS, dir_fd=directory)
    except FileNotFoundError:
        return False
    except OSError as error:
        raise ValueError(f'Unsafe export file: {name}') from error
    with os.fdopen(fd, 'rb') as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError(f'Unsafe export file: {name}')
        return source.read() == content


def _scan(directory, prefix, expected, stale):
    """Inspect the entire tree without following any symlinks, before mutations."""
    with os.scandir(directory) as entries:
        for item in entries:
            relative = prefix / item.name
            if item.is_symlink():
                raise ValueError(f'Symlink in export tree: {relative}')
            if item.is_dir(follow_symlinks=False):
                fd = os.open(item.name, DIR_FLAGS, dir_fd=directory)
                try:
                    _scan(fd, relative, expected, stale)
                finally:
                    os.close(fd)
            elif item.name.endswith('.yaml'):
                if not _owned_file(directory, item.name):
                    if relative in expected:
                        raise ValueError(f'Human-owned export collision: {relative}')
                    continue
                if relative not in expected:
                    stale.append(relative)
            elif relative in expected:
                raise ValueError(f'Export collision: {relative}')


def _walk(root_fd, parts, stack, *, create=False):
    directory = root_fd
    for part in parts:
        directory = _directory(directory, part, stack, create=create)
    return directory


def write(root, package):
    expected = render(package)
    # All paths below are relative to stable directory descriptors. O_NOFOLLOW
    # prevents symlink replacement between inspection and opening a directory.
    with ExitStack() as stack:
        root_fd = stack.enter_context(_closing_fd(os.open(root, DIR_FLAGS)))
        try:
            theme = _directory(root_fd, 'themen', stack)
        except ValueError:
            # A missing directory is fine; a symlink, file or inaccessible one is not.
            try:
                os.stat('themen', dir_fd=root_fd, follow_symlinks=False)
            except FileNotFoundError:
                theme = None
            else:
                raise
        stale = []
        if theme is not None:
            _scan(theme, Path('themen'), expected, stale)
        # Preflight *every* expected ancestor before deleting or writing anything.
        for relative in expected:
            with ExitStack() as inspect:
                directory = root_fd
                for part in relative.parts[:-1]:
                    try:
                        directory = _directory(directory, part, inspect)
                    except ValueError:
                        try:
                            os.stat(part, dir_fd=directory, follow_symlinks=False)
                        except FileNotFoundError:
                            break
                        raise
                else:
                    try:
                        os.stat(relative.name, dir_fd=directory, follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        if not _owned_file(directory, relative.name):
                            raise ValueError(f'Human-owned export collision: {relative}')
        # Refuse stale exports rather than unlinking a pathname that may have
        # changed ownership since the scan. Prune them manually in a trusted tree.
        if stale:
            raise ValueError(f'Stale generated exports require manual removal: {stale}')
        # Create and publish each file via a same-directory temporary name.
        # Directory FDs and NOFOLLOW block ancestor escapes; exclusive hard-link
        # publication protects a newly created human-owned leaf from overwrite.
        for relative, text in expected.items():
            with ExitStack() as output:
                directory = _walk(root_fd, relative.parts[:-1], output, create=True)
                if _unchanged_file(directory, relative.name, text.encode('utf-8')):
                    continue
                temporary = f'.export-{secrets.token_hex(16)}.tmp'
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW | os.O_CLOEXEC, 0o644, dir_fd=directory)
                try:
                    with os.fdopen(fd, 'wb') as target:
                        target.write(text.encode('utf-8'))
                    try:
                        os.stat(relative.name, dir_fd=directory, follow_symlinks=False)
                    except FileNotFoundError:
                        # Atomic create-if-absent: a raced human file is not replaced.
                        try:
                            os.link(temporary, relative.name, src_dir_fd=directory,
                                    dst_dir_fd=directory, follow_symlinks=False)
                        except FileExistsError as error:
                            raise ValueError(f'Export collision: {relative}') from error
                    else:
                        # A regular file can be swapped between any ownership
                        # check and os.replace. Never replace an existing name.
                        raise ValueError(f'Export exists; remove manually before regeneration: {relative}')
                finally:
                    try:
                        os.unlink(temporary, dir_fd=directory)
                    except FileNotFoundError:
                        pass

    return expected
