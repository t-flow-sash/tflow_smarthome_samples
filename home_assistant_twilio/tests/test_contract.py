"""Exakte Vertragstests für das öffentliche Kamera-AI→Twilio-SMS-Beispiel."""

from __future__ import annotations

import copy
import importlib.util
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jinja2 import Environment, StrictUndefined
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

ROOT = Path(__file__).resolve().parents[1]
YAML_FILES = sorted(ROOT.glob("*.yaml"))
EXPECTED_YAML = {"automations.yaml", "configuration.yaml", "secrets.example.yaml"}
EXPECTED_FILES = {
    "LICENSE",
    "README.md",
    "automations.yaml",
    "configuration.yaml",
    "scripts/validate.py",
    "secrets.example.yaml",
    "tests/test_contract.py",
}
EXPECTED_SECRETS = {"twilio_account_sid", "twilio_auth_token"}
CAMERAS = tuple(f"camera_{index:02d}" for index in range(1, 9))
HELPERS = {f"camera_ai_sms_last_{camera}" for camera in CAMERAS}
TARGET_PLACEHOLDER = "+491234567890"


class HomeAssistantLoader(yaml.SafeLoader):
    """Erhält Home-Assistant-Tags als überprüfbare Marker."""


def _ha_tag(loader: HomeAssistantLoader, tag_suffix: str, node: ScalarNode) -> str:
    return f"!{tag_suffix} {loader.construct_scalar(node)}"


HomeAssistantLoader.add_multi_constructor("!", _ha_tag)


def load(name: str):
    return yaml.load((ROOT / name).read_text(encoding="utf-8"), Loader=HomeAssistantLoader)


def package_files() -> set[str]:
    return {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def make_environment() -> Environment:
    environment = Environment(undefined=StrictUndefined, autoescape=False)
    environment.filters["regex_match"] = lambda value, pattern: re.match(pattern, value) is not None
    return environment


def render_bool(template: str, **context) -> bool:
    return make_environment().from_string(template).render(**context).strip() == "True"


class StatesDouble:
    """HA-ähnlich: fehlend liefert beim Aufruf unknown, beim Indexzugriff None."""

    def __init__(self, values: dict[str, str]):
        self.values = values

    def __call__(self, entity_id: str) -> str:
        return self.values.get(entity_id, "unknown")

    def __getitem__(self, entity_id: str):
        return object() if entity_id in self.values else None


class TwilioSampleContract(unittest.TestCase):
    def setUp(self):
        self.config = load("configuration.yaml")
        self.automations = load("automations.yaml")
        self.assertEqual(len(self.automations), 1)
        self.automation = self.automations[0]

    def test_exact_package_and_yaml_file_set(self):
        self.assertEqual({path.name for path in YAML_FILES}, EXPECTED_YAML)
        self.assertEqual(package_files(), EXPECTED_FILES)
        for path in YAML_FILES:
            with self.subTest(path=path.name):
                self.assertIsNotNone(load(path.name))

    def test_every_yaml_has_concrete_german_header(self):
        required = (
            "Zweck:",
            "Nutzen:",
            "Einbau:",
            "Abhängigkeiten:",
            "Anpassen:",
            "Sicherheitsgrenze:",
        )
        for path in YAML_FILES:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                for heading in required:
                    self.assertIn(heading, text)
        automation_text = (ROOT / "automations.yaml").read_text(encoding="utf-8")
        self.assertEqual(automation_text.count("# Wann:"), 1)

    def test_configuration_contract_and_real_secret_tags(self):
        self.assertEqual(set(self.config), {"twilio", "notify", "input_text", "automation"})
        self.assertEqual(
            self.config["twilio"],
            {
                "account_sid": "!secret twilio_account_sid",
                "auth_token": "!secret twilio_auth_token",
            },
        )
        self.assertEqual(
            self.config["notify"],
            [{"platform": "twilio_sms", "name": "twilio_wichtige_sms", "from_number": "HomeAlert"}],
        )
        self.assertRegex(self.config["notify"][0]["from_number"], r"^[A-Za-z0-9]{1,11}$")
        self.assertNotIn("target", self.config["notify"][0])
        self.assertNotIn("to", self.config["notify"][0])
        self.assertEqual(self.config["automation"], "!include automations.yaml")

        document = yaml.compose((ROOT / "configuration.yaml").read_text(encoding="utf-8"))
        self.assertIsNotNone(document)
        tagged_values = []

        def collect(node):
            if isinstance(node, ScalarNode) and node.tag == "!secret":
                tagged_values.append(node.value)
            if isinstance(node, MappingNode):
                for key, value in node.value:
                    collect(key)
                    collect(value)
            elif isinstance(node, SequenceNode):
                for value in node.value:
                    collect(value)

        collect(document)
        self.assertEqual(set(tagged_values), EXPECTED_SECRETS)

    def test_helpers_are_exact_restore_capable_markers(self):
        self.assertEqual(set(self.config["input_text"]), HELPERS)
        for helper, definition in self.config["input_text"].items():
            with self.subTest(helper=helper):
                self.assertEqual(set(definition), {"name", "max"})
                self.assertEqual(definition["max"], 32)
                self.assertNotIn("initial", definition)

    def test_secret_inventory_is_exact_and_placeholder_only(self):
        example = load("secrets.example.yaml")
        self.assertEqual(set(example), EXPECTED_SECRETS)
        self.assertTrue(all(value.startswith("REPLACE_WITH_") for value in example.values()))
        references = set(
            re.findall(r"!secret\s+([a-z0-9_]+)", (ROOT / "configuration.yaml").read_text(encoding="utf-8"))
        )
        self.assertEqual(references, EXPECTED_SECRETS)

    def test_automation_has_exact_trigger_mode_and_action_order(self):
        automation = self.automation
        self.assertEqual(automation["id"], "camera_ai_summary_ready_sms")
        self.assertEqual(automation["mode"], "queued")
        self.assertEqual(automation["max"], 20)
        self.assertEqual(
            automation["triggers"],
            [{"trigger": "event", "event_type": "camera_ai_summary_ready"}],
        )
        self.assertEqual(len(automation["conditions"]), 1)
        self.assertEqual(automation["conditions"][0]["condition"], "template")
        self.assertEqual(
            [step.get("action", step.get("condition", "variables")) for step in automation["actions"]],
            ["variables", "template", "notify.twilio_wichtige_sms", "input_text.set_value"],
        )

        variables = automation["actions"][0]["variables"]
        self.assertEqual(set(variables), {"camera_sms_last_helper", "camera_sms_episode"})
        self.assertIn("input_text.camera_ai_sms_last_", variables["camera_sms_last_helper"])
        self.assertIn("trigger.event.data.camera", variables["camera_sms_last_helper"])
        self.assertEqual(variables["camera_sms_episode"], "{{ trigger.event.data.episode_id }}")

        notify = automation["actions"][2]
        self.assertEqual(set(notify["data"]), {"target", "message"})
        self.assertEqual(notify["data"]["target"], TARGET_PLACEHOLDER)
        self.assertEqual(notify["data"]["message"], "{{ trigger.event.data.sms_summary | trim }}")
        self.assertNotIn("summary |", notify["data"]["message"].replace("sms_summary", ""))
        self.assertNotIn("truncate", notify["data"]["message"])

        marker = automation["actions"][3]
        self.assertEqual(marker["target"]["entity_id"], "{{ camera_sms_last_helper }}")
        self.assertEqual(marker["data"], {"value": "{{ camera_sms_episode }}"})

    def test_event_guard_renders_exact_positive_and_negative_contract(self):
        guard = self.automation["conditions"][0]["value_template"]
        base = {
            "camera": "camera_01",
            "episode_id": "0123456789abcdef0123456789abcdef",
            "summary": " Vollständiger Bericht ",
            "sms_summary": " Kurze eigenständige Meldung ",
        }
        self.assertTrue(render_bool(guard, trigger={"event": {"data": base}}))
        self.assertTrue(render_bool(guard, trigger={"event": {"data": {**base, "sms_summary": "x" * 140}}}))

        mutations = {
            "camera_not_allowed": {"camera": "camera_09"},
            "camera_not_string": {"camera": 1},
            "episode_uppercase": {"episode_id": "A" * 32},
            "episode_short": {"episode_id": "a" * 31},
            "episode_not_string": {"episode_id": 7},
            "summary_blank": {"summary": " \t "},
            "summary_not_string": {"summary": None},
            "sms_blank": {"sms_summary": "   "},
            "sms_too_long": {"sms_summary": "x" * 141},
            "sms_newline": {"sms_summary": "Zeile 1\nZeile 2"},
            "sms_carriage_return": {"sms_summary": "Zeile 1\rZeile 2"},
            "sms_tab": {"sms_summary": "Text\tText"},
            "sms_delete": {"sms_summary": "Text\x7f"},
            "sms_not_string": {"sms_summary": 42},
        }
        for label, replacement in mutations.items():
            with self.subTest(label=label):
                data = {**base, **replacement}
                self.assertFalse(render_bool(guard, trigger={"event": {"data": data}}))

    def test_replay_guard_distinguishes_unknown_missing_and_unavailable(self):
        guard = self.automation["actions"][1]["value_template"]
        helper = "input_text.camera_ai_sms_last_camera_01"
        episode = "0123456789abcdef0123456789abcdef"
        cases = (
            ({helper: "unknown"}, True),
            ({helper: ""}, True),
            ({helper: "fedcba9876543210fedcba9876543210"}, True),
            ({helper: episode}, False),
            ({helper: "unavailable"}, False),
            ({}, False),
        )
        for values, expected in cases:
            with self.subTest(values=list(values.values()), expected=expected):
                self.assertEqual(
                    render_bool(
                        guard,
                        states=StatesDouble(values),
                        camera_sms_last_helper=helper,
                        camera_sms_episode=episode,
                    ),
                    expected,
                )

    def test_forbidden_scope_is_absent_from_runtime_yaml(self):
        runtime = "\n".join(path.read_text(encoding="utf-8") for path in YAML_FILES)
        forbidden = (
            "twilio_" + "call",
            "twilio_data_" + "received",
            "STA" + "TUS",
            "media_" + "url",
            "persistent_" + "notification",
        )
        for value in forbidden:
            with self.subTest(value=value):
                self.assertNotIn(value, runtime)
        self.assertFalse((ROOT / ("templates" + ".yaml")).exists())
        self.assertFalse((ROOT / ("scripts" + ".yaml")).exists())

    def test_readme_links_every_yaml_and_documents_required_boundaries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", readme)
        relative_yaml_links = []
        for link in links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or link.startswith("#"):
                continue
            target = (ROOT / unquote(parsed.path)).resolve()
            with self.subTest(link=link):
                self.assertTrue(target.is_relative_to(ROOT.resolve()))
                self.assertTrue(target.is_file(), f"Fehlendes Linkziel: {target}")
            if target.suffix == ".yaml":
                relative_yaml_links.append(target.name)
        self.assertEqual(set(relative_yaml_links), EXPECTED_YAML)
        for required in (
            "camera_ai_summary_ready",
            "sms_summary",
            "summary",
            "episode_id",
            "notify.twilio_wichtige_sms",
            "Best-Effort",
            "keine Telefonanrufe",
            "keinen Twilio-Empfangswebhook",
            "Konfiguration prüfen",
            "GitOps",
            "Neustart",
            "weder eine Ein-Segment-",
            "keine Zustellung",
        ):
            self.assertIn(required, readme)

    def test_no_credentials_real_numbers_private_hosts_or_webhook_ids(self):
        paths = [path for path in ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        text_without_placeholder = text.replace(TARGET_PLACEHOLDER, "")
        forbidden = {
            "real_account_sid": r"\bAC[0-9a-fA-F]{32}\b",
            "api_key_sid": r"\bSK[0-9a-fA-F]{32}\b",
            "auth_token_shape": r"(?i)(?:auth[_ -]?token|api[_ -]?key)\s*[:=]\s*['\"]?[A-Za-z0-9]{20,}",
            "other_e164_literal": r"(?<![A-Za-z0-9_])\+[1-9][0-9]{7,14}\b",
            "webhook_secret": r"/api/webhook/[A-Za-z0-9_-]{20,}",
            "private_ipv4": r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\b",
        }
        for label, pattern in forbidden.items():
            with self.subTest(label=label):
                self.assertIsNone(re.search(pattern, text_without_placeholder), label)
        self.assertNotIn("github" + "_pat_", text)
        self.assertNotIn("gh" + "p_", text)

    def test_scoped_mit_license(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted, free of charge", license_text)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("](LICENSE)", readme)
        self.assertIn("ausschließlich in `home_assistant_twilio/`", readme)


VALIDATOR_SPEC = importlib.util.spec_from_file_location("twilio_validate", ROOT / "scripts" / "validate.py")
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
VALIDATOR = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR)


class ValidatorGitDiffContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.run_git("init", "-q", "-b", "main")
        self.run_git("config", "user.name", "Twilio Test")
        self.run_git("config", "user.email", "twilio-test@example.invalid")
        (self.repo / "sample").mkdir()
        (self.repo / "sample" / "file.txt").write_text("sauber\n", encoding="utf-8")
        self.run_git("add", "sample/file.txt")
        self.run_git("commit", "-q", "-m", "base")
        self.base = self.run_git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.temp.cleanup()

    def run_git(self, *args: str, check: bool = True):
        return subprocess.run(["git", *args], cwd=self.repo, text=True, capture_output=True, check=check)

    def diff_result(self) -> int:
        head = self.run_git("rev-parse", "HEAD").stdout.strip()
        return VALIDATOR.run_diff_checks(self.repo, "sample", self.base, head)

    def test_committed_candidate_whitespace_fails_with_clean_worktree(self):
        (self.repo / "sample" / "file.txt").write_text("fehler   \n", encoding="utf-8")
        self.run_git("add", "sample/file.txt")
        self.run_git("commit", "-q", "-m", "candidate")
        self.assertEqual(self.run_git("status", "--porcelain").stdout, "")
        self.assertNotEqual(self.diff_result(), 0)

    def test_staged_whitespace_fails(self):
        (self.repo / "sample" / "file.txt").write_text("fehler   \n", encoding="utf-8")
        self.run_git("add", "sample/file.txt")
        self.assertNotEqual(self.diff_result(), 0)

    def test_unstaged_whitespace_fails(self):
        (self.repo / "sample" / "file.txt").write_text("fehler   \n", encoding="utf-8")
        self.assertNotEqual(self.diff_result(), 0)

    def test_clean_candidate_passes(self):
        (self.repo / "sample" / "file.txt").write_text("weiter sauber\n", encoding="utf-8")
        self.run_git("add", "sample/file.txt")
        self.run_git("commit", "-q", "-m", "candidate")
        self.assertEqual(self.diff_result(), 0)

    def test_invalid_base_fails_closed(self):
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.resolve_candidate(self.repo, "keine-solche-base", "HEAD")


if __name__ == "__main__":
    unittest.main()
