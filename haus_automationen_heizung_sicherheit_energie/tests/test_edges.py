"""Hermetic retention and calendar edge probes; never touch a live /media tree."""
import importlib.util
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml
from jinja2 import Environment

ROOT=Path(__file__).resolve().parents[1]
class Loader(yaml.SafeLoader):
    pass
Loader.add_constructor('!secret', lambda loader, node: loader.construct_scalar(node))
A={a['id']:a for a in yaml.load((ROOT/'packages/haus.yaml').read_text(), Loader=Loader)['automation']}
CAL=A['public_kalender_abwesenheit']['actions']
ZONE=ZoneInfo('Europe/Berlin')
def dt(s, fallback=None):
    try: return datetime.fromisoformat(s)
    except (TypeError,ValueError): return fallback

def stamp(x, default=0):
    try:
        if isinstance(x,str): x=dt(x)
        if x.tzinfo is None:x=x.replace(tzinfo=ZONE)
        return x.timestamp()
    except (TypeError,AttributeError): return default

def render(template,answer,now):
    env=Environment()
    env.globals.update(as_datetime=dt,as_timestamp=stamp,as_local=lambda x:x.astimezone(ZONE),timedelta=timedelta,now=lambda:now)
    return env.from_string(template).render(answer=answer).strip()=='True'

class Calendar(unittest.TestCase):
    def test_malformed_responses_fail_before_derivation(self):
        guard=CAL[2]['value_template']
        examples=[None,{}, {'calendar.beispiel_abwesenheit':{'events':{'start':'2026-10-24'}}},
                  {'calendar.beispiel_abwesenheit':{'events':['bad']}},
                  {'calendar.beispiel_abwesenheit':{'events':[{'start':'nonsense','end':'2026-10-27','summary':'[Heizung]'}]}},
                  {'calendar.beispiel_abwesenheit':{'events':[{'start':'2026-10-27','end':'2026-10-26'}]}}]
        for bad in examples:
            with self.subTest(bad=bad):self.assertFalse(render(guard,bad,datetime(2026,10,24,tzinfo=ZONE)))

    def test_union_exclusive_boundary_all_day_single_day_and_tz(self):
        guard=CAL[2]['value_template']; window=CAL[3]['variables']['away']
        events=[{'summary':'[Heizung] Reise A','start':'2026-10-24','end':'2026-10-27'},
                {'summary':'[Heizung] Reise B','start':'2026-10-27T00:00:00+01:00','end':'2026-10-29T00:00:00+01:00'},
                {'summary':'[Heizung] eintägig','start':'2026-10-30','end':'2026-10-31'}]
        answer={'calendar.beispiel_abwesenheit':{'events':events}}
        for date,expected in [('2026-10-24T14:59:59+02:00',False),('2026-10-24T15:00:00+02:00',True),('2026-10-26T07:59:59+01:00',True),('2026-10-26T08:00:00+01:00',False),('2026-10-27T07:59:59+01:00',False),('2026-10-27T08:00:00+01:00',False),('2026-10-27T15:00:00+01:00',True),('2026-10-29T08:00:00+01:00',False),('2026-10-30T16:00:00+01:00',False)]:
            now=datetime.fromisoformat(date)
            with self.subTest(now=date):
                self.assertTrue(render(guard,answer,now))
                self.assertEqual(render(window,answer,now),expected)

class Media(unittest.TestCase):
    def test_fixed_directories_age_and_size_and_symlink_denial(self):
        spec=importlib.util.spec_from_file_location('camera_media',ROOT/'scripts/camera_media.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            module.ROOT=Path(tmp);module.MAX_BYTES=10;module.MAX_AGE_SECONDS=20
            module.prepare()
            d=module.ROOT/'zone_01';old=d/'old.jpg';new=d/'new.jpg'
            old.write_bytes(b'12345678');new.write_bytes(b'12345678')
            import os
            os.utime(old,(1,1));os.utime(new,(19,19))
            module.maintain(now=25)
            self.assertFalse(old.exists());self.assertTrue(new.exists())
            new.write_bytes(b'12345678901');module.maintain(now=26)
            self.assertFalse(new.exists())
            (d/'link.jpg').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError): module.maintain(now=27)
            self.assertTrue((d/'link.jpg').is_symlink())
            (d/'link.jpg').unlink()
            d.chmod(0o755)
            with self.assertRaises(ValueError): module.prepare()
            with self.assertRaises(ValueError): module.maintain(now=28)

if __name__=='__main__':unittest.main()
