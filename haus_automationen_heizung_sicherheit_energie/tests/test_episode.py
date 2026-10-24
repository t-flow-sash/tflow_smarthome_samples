"""Fail-closed camera handoff and episode-shape regression checks."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class Loader(yaml.SafeLoader):
    pass
Loader.add_constructor('!secret', lambda loader, node: loader.construct_scalar(node))


class Episode(unittest.TestCase):
    def test_six_callbacks_have_stable_episode_and_one_continuation_owner(self):
        config = yaml.load((ROOT / 'packages/haus.yaml').read_text(), Loader=Loader)
        self.assertIn('demo_camera_finished', config['rest_command'])
        payload = config['rest_command']['demo_camera_finished']['payload']
        for field in ('event_type', 'camera', 'episode_id', 'started_at', 'ended_at', 'reason', 'snapshot_count'):
            self.assertIn(field, payload)
        for i in range(1, 7):
            slug = f'zone_{i:02}'
            flow = next(a for a in config['automation'] if a['id'] == 'public_kamera_' + slug)
            text = str(flow)
            self.assertIn('episode_id', text)
            self.assertIn('started_at', text)
            self.assertIn('next_index', text)
            self.assertIn('rest_command.demo_camera_finished', text)
            self.assertIn('recording_disabled', text)
            self.assertIn('detection_ended', text)
            self.assertIn('camera_unavailable', text)
            self.assertEqual(flow['mode'], 'restart')
            self.assertEqual(sum(t.get('event_type') == 'demo_camera_continue' for t in flow['triggers']), 1)
            self.assertNotIn('parallel', text)

    def test_receiver_rejects_invalid_payload_and_unsafe_files(self):
        receiver = module('camera_episode_receiver')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'media'
            (root / 'zone_01').mkdir(parents=True)
            root.chmod(0o700)
            (root / 'zone_01').chmod(0o700)
            event = dict(event_type='camera_phase_finished', camera='zone_01',
                         episode_id='a' * 32, started_at='2026-10-24T10:00:00+00:00',
                         ended_at='2026-10-24T10:00:10+00:00', reason='detection_ended', snapshot_count=1)
            name = '20261024T100001000000_' + 'a' * 32 + '_1.jpg'
            (root / 'zone_01' / name).write_bytes(b'\xff\xd8image\xff\xd9')
            output = receiver.prepare(event, root)
            self.assertEqual(output['available_count'], 1)
            self.assertEqual(output['event_type'], 'validated_camera_episode')
            self.assertEqual(output['sample_paths'], [str(root / 'zone_01' / name)])
            for change in ({'camera': '../other'}, {'camera': ['zone_01']}, {'reason': []}, {'episode_id': 'A' * 32},
                           {'reason': ' detection_ended'}, {'snapshot_count': True},
                           {'snapshot_count': -1}, {'started_at': '2026-10-24'},
                           {'ended_at': '2026-10-23T10:00:00+00:00'},
                           {'unexpected': 'x'}):
                with self.subTest(change=change), self.assertRaises(ValueError):
                    receiver.prepare({**event, **change}, root)
            (root / 'zone_01' / name).unlink()
            (root / 'zone_01' / name).symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):
                receiver.prepare(event, root)
            with self.assertRaises(ValueError):
                receiver.prepare(json.dumps(event), root)
            (root / 'zone_01' / name).unlink()
            (root / 'zone_01').chmod(0o755)
            with self.assertRaises(ValueError):
                receiver.prepare(event, root)


if __name__ == '__main__':
    unittest.main()
