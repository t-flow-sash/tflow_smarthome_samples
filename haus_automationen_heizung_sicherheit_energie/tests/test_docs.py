"""Public navigation and dependency inventory parity with the generated package."""
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / 'README.md', *sorted((ROOT / 'docs').glob('*.md'))]
PACKAGE = (ROOT / 'packages/haus.yaml').read_text(encoding='utf-8')
MANIFEST = yaml.safe_load((ROOT / 'dependencies.yaml').read_text(encoding='utf-8'))


class DocsContract(unittest.TestCase):
    def test_every_relative_markdown_link_resolves(self):
        self.assertEqual(len(DOCS), 9)
        for doc in DOCS:
            for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc or link.startswith('#'):
                    continue
                with self.subTest(doc=doc.relative_to(ROOT), link=link):
                    target = (doc.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(target.is_relative_to(ROOT.resolve()), 'Link leaves package')
                    self.assertTrue(target.is_file(), f'Missing target: {target}')
                    if parsed.fragment:
                        body = target.read_text(encoding='utf-8')
                        headings = re.findall(r'^#{1,6}\s+(.+)$', body, re.MULTILINE)
                        slugs = {re.sub(r'[^\w\- ]', '', h.casefold()).replace(' ', '-') for h in headings}
                        self.assertIn(unquote(parsed.fragment).casefold(), slugs)

    def test_integration_catalog_exact_public_repo_mapping_and_navigation(self):
        catalog = (ROOT / 'docs/integrationen.md').read_text(encoding='utf-8')
        expected = {
            'Better Thermostat': 'KartoffelToby/better_thermostat',
            'Alarmo': 'nielsfaber/alarmo',
            'EcoFlow Energy': 'shuette42/ecoflow-energy-ha',
            'Heidelberg Energy Control': 'Schrolli91/heidelberg_energy_control',
            'Climate Group Helper': 'bjrnptrsn/climate_group_helper',
            'X-Sense': 'Jarnsen/ha-xsense-component_test',
            'Browser Mod': 'thomasloven/hass-browser_mod',
            'Tibber Graph': 'stefanes/tibber-graph',
            'EcoFlow Cloud': 'tolwi/hassio-ecoflow-cloud',
            'Mushroom': 'piitaya/lovelace-mushroom',
            'Room Summary Card': 'homeassistant-extras/room-summary-card',
            'ApexCharts Card': 'RomRider/apexcharts-card',
            'Solar Card': 'victorigualada/lovelace-solar-card',
            'Alarmo Card': 'nielsfaber/alarmo-card',
            'HACS selbst': 'hacs/integration',
        }
        actual = re.findall(r'\[([^\]]+)\]\(https://github\.com/([\w.-]+/[\w.-]+)\)', catalog)
        self.assertEqual(dict(actual), expected)
        self.assertEqual(len(actual), len(expected), 'Each verified repository is linked exactly once')
        for page in ('README.md', 'docs/setup.md', 'docs/heizung.md',
                     'docs/sicherheit-kameras.md', 'docs/energie.md'):
            body = (ROOT / page).read_text(encoding='utf-8')
            self.assertIn('integrationen.md)', body, page)
        for name in ('better_thermostat', 'alarm_control_panel.beispiel_alarmo',
                     'ecoflow_energy', 'heidelberg_energy_control', 'Core-MQTT',
                     'Frontend-Karte', 'Add-on', 'externer Dienst'):
            self.assertIn(name, catalog)

    def test_all_generated_automations_documented_once(self):
        from test_contract import D as package

        ids = {a['id'] for a in package['automation']}
        self.assertEqual(len(ids), 16)
        card = (ROOT / 'docs/codekarte.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| \[`([a-z_]+(?:\d+)?)`\]\(\.\./themen/[^)]+\.yaml\) \|', card, re.MULTILINE)
        self.assertEqual(set(rows), {x.removeprefix('public_') for x in ids})
        self.assertEqual(len(rows), len(ids))

    def test_dependency_manifest_covers_external_entities_and_services(self):
        from test_contract import D, walk
        named = [entity for group in MANIFEST['entities'].values() for entity in group]
        self.assertEqual(len(named), len(set(named)), 'Duplicate external entity')
        actual = set(re.findall(r'\b[a-z_]+\.beispiel_[a-z0-9_]+', PACKAGE))
        self.assertEqual(set(named), actual)
        self.assertEqual(len(named), len(actual))
        explicit = {node['action'] for node in walk(D) if isinstance(node.get('action'), str)}
        core = {'input_boolean.turn_on', 'input_boolean.turn_off', 'input_number.set_value',
                'input_text.set_value', 'script.demo_abschliessen', 'switch.turn_on',
                'switch.turn_off', 'light.turn_on', 'light.turn_off',
                'persistent_notification.create'}
        self.assertEqual(set(MANIFEST['external_services']), explicit - core)
        self.assertEqual(explicit, set(MANIFEST['external_services']) | core)
        self.assertEqual(set(MANIFEST['local_scripts']) | {'scripts/export_topics.py', 'scripts/component_notes.py'}, {str(p.relative_to(ROOT)) for p in (ROOT / 'scripts').glob('*.py')})
        self.assertEqual(set(MANIFEST['secret_names']), set(re.findall(r'!secret [\'\"]?([a-z_]+)', PACKAGE)))
        setup = (ROOT / 'docs/setup.md').read_text(encoding='utf-8')
        self.assertTrue(all(name in setup for name in MANIFEST['secret_names']))
        for category in ('heating', 'security', 'energy'):
            self.assertIn(category, MANIFEST['entities'])


if __name__ == '__main__':
    unittest.main()
