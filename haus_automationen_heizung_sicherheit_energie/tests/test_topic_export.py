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
spec = importlib.util.spec_from_file_location('export_topics', ROOT / 'scripts/export_topics.py')
assert spec is not None and spec.loader is not None
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
class ExportLoader(Loader):
    pass
ExportLoader.add_constructor('!secret', lambda loader, node: export.Secret(loader.construct_scalar(node)))


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


if __name__ == '__main__':
    unittest.main()
