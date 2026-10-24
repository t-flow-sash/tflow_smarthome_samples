"""Contract and security checks for the synthetic package (no physical side effects)."""
import ast
import importlib.util
import re
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT/'packages/haus.yaml').read_text()
class Loader(yaml.SafeLoader):
    pass
Loader.add_constructor('!secret', lambda loader, node: loader.construct_scalar(node))
D = yaml.load(TEXT, Loader=Loader)
A = {a['id']:a for a in D['automation']}

def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for value in obj.values(): yield from walk(value)
    elif isinstance(obj,list):
        for value in obj: yield from walk(value)

class Contract(unittest.TestCase):
    def test_ids_unique_and_build_reproducible(self):
        self.assertEqual(len(A),len(D['automation']))
        self.assertEqual(len(A),16)
        self.assertTrue(all(n.startswith('public_') for n in A))
        self.assertEqual(len([a for a in A if a.startswith('public_kamera_zone_')]),6)

    def test_calendar_guard_before_derived_or_writes(self):
        actions=A['public_kalender_abwesenheit']['actions']
        self.assertEqual(actions[1]['action'],'calendar.get_events')
        guard=actions[2]['value_template']
        self.assertIn('events is sequence',guard)
        self.assertIn('events is not mapping',guard)
        self.assertIn('e is not mapping',guard)
        self.assertIn('as_datetime(e.get(',guard)
        self.assertIn('end',guard)
        self.assertIn('15:00:00',actions[3]['variables']['away'])
        self.assertIn('08:00:00',actions[3]['variables']['away'])
        self.assertIn('timedelta(days=1)',actions[3]['variables']['away'])
        self.assertNotIn('warmwasser',str(actions).lower())

    def test_wolf_claim_only_after_readback_and_separate_consent(self):
        cal=A['public_kalender_abwesenheit']
        self.assertIn('demo_bt_freigabe',str(cal))
        self.assertIn('demo_wolf_freigabe',str(cal))
        self.assertNotIn('select.beispiel_wolf_dhk',cal['actions'][3]['variables']['away'])
        seq=[v for v in walk(cal) if v.get('action')=='input_boolean.turn_on' and v.get('target',{}).get('entity_id')=='input_boolean.demo_wolf_ownership']
        self.assertEqual(len(seq),1)
        parent=[v for v in walk(cal) if isinstance(v.get('sequence'),list) and seq[0] in v['sequence']]
        self.assertEqual(len(parent),1)
        steps=parent[0]['sequence']
        self.assertLess(next(i for i,v in enumerate(steps) if v.get('action')=='select.select_option'),next(i for i,v in enumerate(steps) if v==seq[0]))
        self.assertTrue(any('wait_template' in x for x in steps))
        self.assertTrue(any('is_state' in x.get('value_template','') and 'Standby' in x['value_template'] for x in steps))
        self.assertNotIn('initial',D['input_boolean']['demo_wolf_ownership'])
        self.assertNotIn('initial',D['input_boolean']['demo_kalender_ownership'])

    def test_shadow_is_weighted_validated_and_read_only(self):
        t=str(D['template'])
        self.assertIn("'w':2",t)
        self.assertIn('21600',t)
        self.assertIn('> 70',t)
        self.assertIn('>= 30',t)
        self.assertIn('>= 0.3',t)
        self.assertIn('delay_on',t)
        a=A['public_wolf_shadow']
        self.assertNotIn('select.select_option',str(a))
        self.assertIn("'delay': '00:05:00'",str(a))
        self.assertEqual(a['mode'],'restart')

    def test_camera_one_owner_and_frame_gate(self):
        for i in range(1,7):
            slug=f'zone_{i:02}'
            a=A['public_kamera_'+slug]
            self.assertEqual(a['mode'],'restart')
            self.assertIn("'camera': '"+slug+"'",str(a))
            frame=[x for x in walk(a) if x.get('action')=='camera.snapshot']
            self.assertEqual(len(frame),1)
            self.assertIn('/media/demo_camera/'+slug+'/',frame[0]['data']['filename'])
            self.assertEqual(len([x for x in walk(a) if x.get('count')==100]),1)
            frame_parent=[x for x in walk(a) if isinstance(x.get('sequence'),list) and frame[0] in x['sequence']]
            self.assertEqual(len(frame_parent),1)
            self.assertIn('is_state(\'switch.beispiel_'+slug+'_aufnahme\',\'on\')',str(a))
            self.assertIn('00:00:05',str(a))
            if i>=4:self.assertIn('00:00:30',str(a))
        helper=ast.parse((ROOT/'scripts/camera_media.py').read_text())
        self.assertTrue(helper)
        self.assertIn('demo_camera_finished',D['rest_command'])
        self.assertEqual(D['shell_command']['demo_camera_maintain'],'python3 /config/demo_camera_media.py maintain')

    def test_physical_and_energy_boundaries(self):
        self.assertNotIn('lock.unlock',TEXT)
        self.assertNotIn('alarm_control_panel.alarm_disarm',TEXT)
        self.assertNotIn('ecoflow.',str(D['automation']).lower())
        self.assertIn('intraday_price_ranking',TEXT)
        self.assertIn('demo_lade_preis',str(A['public_ladekosten']))
        self.assertIn('300',str(A['public_ladekosten']))
        self.assertTrue(all(D['input_boolean'][i]['initial'] is False for i in ('demo_bt_freigabe','demo_wolf_freigabe','demo_sicherheit_freigabe','demo_laden_freigabe')))

    def test_privacy_hygiene(self):
        files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        for p in files:
            content=p.read_text()
            self.assertNotRegex(content,r'(?<!\d)(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}')
            self.assertNotRegex(content,r'(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
            self.assertNotRegex(content,r'(?i)https?://[^\s/@]+:[^\s/@]+@')
            self.assertNotRegex(content,r'\b[a-f0-9]{32}\b')

if __name__=='__main__': unittest.main()
