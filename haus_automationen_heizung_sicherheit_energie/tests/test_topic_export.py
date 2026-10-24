"""GitHub-browsable component files reconstruct the canonical HA package."""
import importlib.util
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from test_contract import Loader, ROOT

EXPORT = ROOT / 'themen'
sys.path.insert(0, str(ROOT / 'scripts'))  # Dynamic exporter import resolves its canonical notes module.
spec = importlib.util.spec_from_file_location('export_topics', ROOT / 'scripts/export_topics.py')
assert spec is not None and spec.loader is not None
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
class ExportLoader(Loader):
    pass
ExportLoader.add_constructor('!secret', lambda loader, node: export.Secret(loader.construct_scalar(node)))


def small_package():
    return {domain: ([{'id': 'public_demo'}] if domain == 'automation' else
                     [] if domain in ('template', 'sensor') else {}) for domain in export.DOMAINS}


class TopicExport(unittest.TestCase):
    def test_every_domain_component_exactly_once_and_semantically_identical(self):
        canonical = yaml.load((ROOT / 'packages/haus.yaml').read_text(encoding='utf-8'), Loader=ExportLoader)
        expected = export.render(canonical)
        actual = {p.relative_to(ROOT): p for p in EXPORT.rglob('*.yaml')}
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(len(actual), 60)
        self.assertEqual({t: sum(p.parts[1] == t for p in actual) for t in export.TOPICS},
                         {'heizung': 21, 'sicherheit': 23, 'energie': 16})
        parsed = {}
        for path, source in actual.items():
            with self.subTest(path=path):
                self.assertEqual(source.read_text(encoding='utf-8'), expected[path],
                                 'Export must be byte-for-byte generator output')
                value = yaml.load(source.read_text(encoding='utf-8'), Loader=ExportLoader)
                domain = path.parts[2]
                self.assertIn(domain, canonical)
                if domain in ('automation', 'template', 'sensor'):
                    self.assertIsInstance(value, list)
                    self.assertEqual(len(value), 1)
                else:
                    self.assertIsInstance(value, dict)
                    self.assertEqual(len(value), 1)
                parsed[path] = value
        # Reconstruct the independent package domain values, not just counts.
        for domain, original in canonical.items():
            files = [p for p in parsed if p.parts[2] == domain]
            if isinstance(original, dict):
                reconstructed = {}
                for path in files:
                    for key, value in parsed[path].items():
                        self.assertNotIn(key, reconstructed, f'Duplicate {domain}.{key}')
                        reconstructed[key] = value
                self.assertEqual(reconstructed, original)
                if domain == 'rest_command':
                    self.assertIsInstance(reconstructed['demo_camera_finished']['url'], export.Secret)
                    self.assertIsInstance(reconstructed['demo_camera_finished']['headers']['X-Gitlab-Token'], export.Secret)
            elif domain == 'template':
                reconstructed = {kind: {} for kind in original[0]}
                for path in files:
                    for kind, elements in parsed[path][0].items():
                        for item in elements:
                            self.assertNotIn(item['name'], reconstructed[kind])
                            reconstructed[kind][item['name']] = item
                for kind, elements in original[0].items():
                    self.assertEqual(reconstructed[kind], {item['name']: item for item in elements})
            else:
                key = (lambda x: x['id']) if domain == 'automation' else (lambda x: x['name'])
                reconstructed = [parsed[p][0] for p in files]
                self.assertEqual(Counter(key(x) for x in reconstructed),
                                 Counter(key(x) for x in original))
                self.assertEqual({key(x): x for x in reconstructed},
                                 {key(x): x for x in original})

    def test_component_comments_are_specific_complete_and_match_install_shape(self):
        canonical = yaml.load((ROOT / 'packages/haus.yaml').read_text(encoding='utf-8'), Loader=ExportLoader)
        components = {(domain, key): value for domain, key, value in export.pieces(canonical)}
        self.assertEqual(set(components), set(export.component_notes.NOTES), 'Every note must describe one actual component')
        for (domain, key), value in components.items():
            path = Path('themen') / export.topic(domain, key) / domain / export.filename(domain, key)
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding='utf-8')
                header = text.splitlines()[0] + '\n' + export.component_notes.comment(domain, key)
                self.assertTrue(text.startswith(header), 'Header must be generated canonically before YAML')
                self.assertEqual(text[len(header):], yaml.safe_dump(
                    value, allow_unicode=True, sort_keys=False, width=110),
                    'The comment must not alter or reformat the generated YAML body')
                self.assertIn(f'# Baustein: {domain}.{key}', header)
                for field in ('Zweck', 'Nutzen', 'Einbau', 'Abhängigkeiten', 'Anpassen', 'Sicherheitsgrenze'):
                    match = re.search(rf'^# {field}: (.+)$', header, re.MULTILINE)
                    self.assertIsNotNone(match, field)
                    if match is not None:
                        self.assertGreater(len(match.group(1)), 20, field)
                self.assertIn('packages/haus.yaml', header)
                self.assertIn('niemals beide parallel', header)
                self.assertIn(f'{domain}:', header)
                self.assertIn(key, header.splitlines()[1])
                note = export.component_notes.NOTES[(domain, key)]
                self.assertEqual(len(note), 6)
                self.assertEqual(len(set(note) - {''}), 6 if domain == 'automation' else 5,
                                 'Purpose, benefit, dependency, adaptation and safety must differ')
                if domain in ('automation', 'template', 'sensor'):
                    self.assertIn('Listenelement', header)
                    self.assertNotIn('Mapping-Include', header)
                else:
                    self.assertIn('Mapping', header)
                    self.assertNotIn('Listenelement', header)
                if domain == 'automation':
                    self.assertRegex(header, r'(?m)^# Wann: .{15,}$')
                self.assertEqual(yaml.load(text, Loader=ExportLoader), value)

    def test_representative_comments_explain_behavior_and_constraints(self):
        expected = {
            'heizung/automation/wolf_shadow.yaml': ('fünf Minuten', 'ohne einen Wolf-Aktor'),
            'heizung/automation/kalender_abwesenheit.yaml': ('ganztägiges Ende ist exklusiv', 'calendar.get_events'),
            'sicherheit/automation/kamera_zone_04.yaml': ('Akku-Kamera', 'Best-Effort-Fortsetzung'),
            'energie/automation/wallbox_freigabe.yaml': ('Preis-Hysterese', 'Widerruf'),
            'energie/automation/ladekosten.yaml': ('Zählerrücksprung', 'EUR/kWh'),
            'sicherheit/rest_command/demo_camera_finished.yaml': ('!secret', 'Zustellgarantie'),
        }
        for relative, terms in expected.items():
            text = (EXPORT / relative).read_text(encoding='utf-8')
            for term in terms:
                with self.subTest(path=relative, term=term):
                    self.assertIn(term, text)

    def test_safety_notes_match_parsed_actuation_and_restoration_limits(self):
        canonical = yaml.load((ROOT / 'packages/haus.yaml').read_text(encoding='utf-8'), Loader=ExportLoader)
        automations = {item['id'].removeprefix('public_'): item for item in canonical['automation']}
        calendar = automations['kalender_abwesenheit']['actions'][-1]['choose'][1]['sequence']
        bt_return = calendar[0]
        self.assertEqual(bt_return['if'][1]['entity_id'], 'input_boolean.demo_kalender_ownership')
        self.assertEqual(bt_return['then'][1]['data']['preset_mode'], 'none')
        self.assertNotIn('preset_mode', str(bt_return['then'][0]),
                         'No attribute check before resetting BT presets')
        calendar_note = export.component_notes.comment('input_boolean', 'demo_kalender_ownership')
        self.assertIn('Readback', calendar_note)
        self.assertIn('keine', calendar_note.lower())
        self.assertIn('manuell', calendar_note.lower())
        self.assertNotIn('Schützt fremd gesetzte Presets', calendar_note)
        self.assertNotIn('stellt nur nach eigenem Readback bestätigte Zustände zurück',
                             export.component_notes.comment('automation', 'kalender_abwesenheit'))
        self.assertIn('ohne erneuten Preset-Vergleich',
                      export.component_notes.comment('automation', 'kalender_abwesenheit'))
        wolf_note = export.component_notes.comment('input_boolean', 'demo_wolf_ownership')
        self.assertIn('keine Erkennung fremder Änderungen', wolf_note)
        self.assertIn('Keine Herkunftserkennung',
                      export.component_notes.comment('input_text', 'demo_kalender_wolf_vorher'))
        self.assertEqual(canonical['input_boolean']['demo_lade_zaehler_gueltig'],
                         {'name': 'demo_lade_zaehler_gueltig'})
        self.assertNotIn('demo_lade_zaehler_gueltig', str(automations['ladekosten']))
        cost_note = export.component_notes.comment('input_boolean', 'demo_lade_zaehler_gueltig')
        self.assertIn('nicht als aktiver', cost_note)
        self.assertIn('keine aktive Sperre', cost_note)
        receiver_note = export.component_notes.comment('rest_command', 'demo_camera_finished')
        self.assertIn('keine dauerhafte Zustellgarantie', receiver_note)
        self.assertNotIn('garantierte Zustellung', receiver_note)
        for zone in range(1, 7):
            z = f'zone_{zone:02}'
            recording = automations['aufnahme_bei_abwesenheit']['actions']
            self.assertTrue(any(z in str(action) for action in recording))
            note = export.component_notes.comment('input_boolean', f'demo_aufnahme_ownership_{z}')
            self.assertIn('keine', note.lower())
            self.assertIn('manuell', note.lower())

    def test_all_topic_yaml_linked_once_in_correct_theme_and_readme_navigation(self):
        used = []
        for topic, doc in [('heizung', 'heizung.md'), ('sicherheit', 'sicherheit-kameras.md'),
                           ('energie', 'energie.md')]:
            text = (ROOT / 'docs' / doc).read_text(encoding='utf-8')
            links = re.findall(r'\]\(\.\./(themen/[^)]+\.yaml)\)', text)
            expected = {p.relative_to(ROOT).as_posix() for p in (EXPORT / topic).rglob('*.yaml')}
            self.assertEqual(set(links), expected)
            self.assertEqual(len(links), len(expected), 'Each component linked exactly once')
            used.extend(links)
            self.assertIn(f'docs/{doc}#direkt-kopierbare-yaml-bausteine',
                          (ROOT / 'README.md').read_text(encoding='utf-8'))
        self.assertEqual(len(used), len(set(used)))

    def test_symlink_root_rejected_without_external_edits(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'repo'
            root.mkdir()
            external = base / 'external'
            external.mkdir()
            sentinel = external / 'sentinel.yaml'
            sentinel.write_text('private: preserve\n')
            (root / 'themen').symlink_to(external, target_is_directory=True)
            with self.assertRaises(ValueError):
                export.write(root, small_package())
            self.assertEqual({p.name: p.read_bytes() for p in external.iterdir()},
                             {'sentinel.yaml': b'private: preserve\n'})

    def test_symlink_ancestors_rejected_before_stale_cleanup(self):
        for location in ('topic', 'domain'):
            with self.subTest(location=location), TemporaryDirectory() as tmp:
                base = Path(tmp)
                root = base / 'repo'
                theme = root / 'themen'
                theme.mkdir(parents=True)
                stale = theme / 'orphan.yaml'
                stale.write_text('# Generiert mit scripts/build.py; nur fiktive Entity-IDs.\nstale: true\n')
                external = base / 'external'
                external.mkdir()
                sentinel = external / 'sentinel.yaml'
                sentinel.write_text('private: preserve\n')
                if location == 'topic':
                    (theme / 'sicherheit').symlink_to(external, target_is_directory=True)
                else:
                    topic = theme / 'sicherheit'
                    topic.mkdir()
                    (topic / 'automation').symlink_to(external, target_is_directory=True)
                with self.assertRaises(ValueError):
                    export.write(root, small_package())
                self.assertTrue(stale.exists(), 'Preflight must precede deletion')
                self.assertEqual({p.name: p.read_bytes() for p in external.iterdir()},
                                 {'sentinel.yaml': b'private: preserve\n'})

    def test_yaml_leaf_symlinks_rejected_before_deletion_or_write(self):
        for location in ('expected', 'stale'):
            with self.subTest(location=location), TemporaryDirectory() as tmp:
                base = Path(tmp)
                root = base / 'repo'
                directory = root / 'themen' / 'sicherheit' / 'automation'
                directory.mkdir(parents=True)
                external = base / 'sentinel.yaml'
                external.write_text('private: preserve\n')
                stale = root / 'themen' / 'orphan.yaml'
                stale.write_text('# Generiert mit scripts/build.py; nur fiktive Entity-IDs.\nstale: true\n')
                (directory / ('demo.yaml' if location == 'expected' else 'orphan.yaml')).symlink_to(external)
                with self.assertRaises(ValueError):
                    export.write(root, small_package())
                self.assertEqual(external.read_bytes(), b'private: preserve\n')
                self.assertTrue(stale.exists())

    def test_human_yaml_preserved_and_expected_collision_fails_closed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            theme = root / 'themen'
            theme.mkdir()
            human = theme / 'notes.yaml'
            human.write_text('owned: human\n')
            export.unsafe_write(root, small_package())
            self.assertEqual(human.read_text(), 'owned: human\n')
            expected = theme / 'sicherheit' / 'automation' / 'demo.yaml'
            expected.write_text('owned: human\n')
            with self.assertRaises(ValueError):
                export.write(root, small_package())
            self.assertEqual(expected.read_text(), 'owned: human\n')

    def test_stale_generated_yaml_requires_manual_cleanup_without_touching_human_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            theme = root / 'themen'
            theme.mkdir()
            stale = theme / 'orphan.yaml'
            stale.write_bytes(export.GENERATED_HEADER + b'orphan: true\n')
            notes = theme / 'notes.yaml'
            notes.write_text('owned: human\n')
            with self.assertRaises(ValueError):
                export.write(root, small_package())
            self.assertEqual(stale.read_bytes(), export.GENERATED_HEADER + b'orphan: true\n')
            self.assertEqual(notes.read_text(), 'owned: human\n')

    def test_human_leaf_swapped_after_last_ownership_check_is_not_replaced(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'themen/sicherheit/automation/demo.yaml'
            target.parent.mkdir(parents=True)
            target.write_text(export.render(small_package())[Path('themen/sicherheit/automation/demo.yaml')])
            original_walk = export._walk
            swapped = False

            def swap_before_publish(root_fd, parts, stack, *, create=False):
                nonlocal swapped
                directory = original_walk(root_fd, parts, stack, create=create)
                if create and not swapped:
                    swapped = True
                    target.unlink()
                    target.write_text('owned: human\n')
                return directory

            with patch.object(export, '_walk', side_effect=swap_before_publish):
                try:
                    export.unsafe_write(root, small_package())
                except ValueError:
                    pass  # Refusal is permitted, but modifying the human file is not.
            self.assertTrue(swapped)
            self.assertEqual(target.read_bytes(), b'owned: human\n')

    def test_stale_human_leaf_swapped_after_ownership_check_is_not_deleted(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stale = root / 'themen/orphan.yaml'
            stale.parent.mkdir()
            stale.write_bytes(export.GENERATED_HEADER + b'old: generated\n')
            original = export._owned_file
            checks = 0

            def swap_after_check(directory, name):
                nonlocal checks
                owned = original(directory, name)
                if name == 'orphan.yaml':
                    checks += 1
                    if checks == 1:
                        stale.unlink()
                        stale.write_text('owned: human\n')
                return owned

            with patch.object(export, '_owned_file', side_effect=swap_after_check):
                try:
                    export.write(root, small_package())
                except ValueError:
                    pass
            self.assertGreaterEqual(checks, 1)
            self.assertEqual(stale.read_bytes(), b'owned: human\n')

    def test_raced_topic_symlink_never_writes_external_target(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'repo'
            topic = root / 'themen' / 'sicherheit'
            topic.mkdir(parents=True)
            external = base / 'external'
            external.mkdir()
            sentinel = external / 'sentinel.yaml'
            sentinel.write_text('private: preserve\n')
            original = export._directory
            swapped = False

            def swap_before_open(parent, name, stack, *, create=False):
                nonlocal swapped
                if create and name == 'sicherheit' and not swapped:
                    swapped = True
                    topic.rename(root / 'themen' / 'old-topic')
                    topic.symlink_to(external, target_is_directory=True)
                return original(parent, name, stack, create=create)

            with patch.object(export, '_directory', side_effect=swap_before_open):
                with self.assertRaises(ValueError):
                    export.unsafe_write(root, small_package())
            self.assertTrue(swapped)
            self.assertEqual({p.name: p.read_bytes() for p in external.iterdir()},
                             {'sentinel.yaml': b'private: preserve\n'})

    def test_leaf_created_after_preflight_is_not_overwritten(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / 'themen/sicherheit/automation/demo.yaml'
            original = export._walk
            injected = False

            def inject_leaf(root_fd, parts, stack, *, create=False):
                nonlocal injected
                directory = original(root_fd, parts, stack, create=create)
                if create and not injected:
                    injected = True
                    target.write_text('owned: human\n')
                return directory

            with patch.object(export, '_walk', side_effect=inject_leaf):
                with self.assertRaises(ValueError):
                    export.unsafe_write(root, small_package())
            self.assertTrue(injected)
            self.assertEqual(target.read_text(), 'owned: human\n')

    def test_build_twice_is_idempotent_and_canonical_package_unchanged(self):
        paths = [ROOT / 'packages/haus.yaml', *sorted(EXPORT.rglob('*.yaml'))]
        before = {p: p.read_bytes() for p in paths}
        for _ in range(2):
            subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build.py')],
                           check=True, cwd=ROOT, capture_output=True, env={'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual({p: p.read_bytes() for p in paths}, before)
            self.assertEqual(set(EXPORT.rglob('*.yaml')), set(paths[1:]))
        with TemporaryDirectory() as tmp:
            copy = Path(tmp) / 'haus.yaml'
            copy.write_bytes(before[ROOT / 'packages/haus.yaml'])
            self.assertEqual(copy.read_bytes(), (ROOT / 'packages/haus.yaml').read_bytes())

    def test_default_export_rename_after_open_never_creates_external_file(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'repo'
            topic = root / 'themen/sicherheit'
            topic.mkdir(parents=True)
            external = base / 'external'
            external.mkdir()
            sentinel = external / 'sentinel.yaml'
            sentinel.write_bytes(b'private: preserve\n')
            (topic / 'automation').mkdir()
            original_directory = export._directory
            swapped = False

            def adversarial_directory(parent, name, stack, *, create=False):
                nonlocal swapped
                fd = original_directory(parent, name, stack, create=create)
                if name == 'sicherheit' and not swapped:
                    topic.rename(external / 'stolen-topic')
                    topic.symlink_to(external, target_is_directory=True)
                    swapped = True
                return fd

            with patch.object(export, '_directory', side_effect=adversarial_directory):
                with self.assertRaises(ValueError):
                    export.write(root, small_package())
            self.assertTrue(swapped)
            self.assertEqual(sentinel.read_bytes(), b'private: preserve\n')
            self.assertEqual({p.relative_to(external) for p in external.rglob('*')},
                             {Path('sentinel.yaml'), Path('stolen-topic'),
                              Path('stolen-topic/automation')})

    def test_default_build_is_read_only_even_with_missing_package(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'packages').mkdir()
            (root / 'themen').mkdir()
            # The source script is run with an isolated target root, never our checkout.
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build.py'),
                                     '--verify-root', str(root)], cwd=ROOT, capture_output=True,
                                    text=True, env={'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Package missing or changed', result.stderr)
            self.assertEqual(set(root.rglob('*')),
                             {root / 'packages', root / 'themen'})

    def test_rename_after_leaf_check_cannot_create_external_export(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / 'repo'
            topic = root / 'themen/sicherheit'
            (topic / 'automation').mkdir(parents=True)
            external = base / 'external'
            external.mkdir()
            (external / 'sentinel.yaml').write_bytes(b'private: preserve\n')
            original = export._unchanged_file
            swapped = False

            def rename_after_check(directory, name, content):
                nonlocal swapped
                unchanged = original(directory, name, content)
                if name == 'demo.yaml' and not swapped:
                    topic.rename(external / 'stolen-topic')
                    topic.symlink_to(external, target_is_directory=True)
                    swapped = True
                return unchanged

            with patch.object(export, '_unchanged_file', side_effect=rename_after_check):
                with self.assertRaises(ValueError):
                    export.write(root, small_package())
            self.assertTrue(swapped)
            self.assertEqual((external / 'sentinel.yaml').read_bytes(), b'private: preserve\n')
            self.assertEqual({p.relative_to(external) for p in external.rglob('*')},
                             {Path('sentinel.yaml'), Path('stolen-topic'),
                              Path('stolen-topic/automation')})


if __name__ == '__main__':
    unittest.main()
