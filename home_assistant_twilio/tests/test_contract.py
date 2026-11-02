"""Vertragstests für das öffentliche Home-Assistant-Twilio-Beispiel."""

from __future__ import annotations

import re
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from yaml.nodes import ScalarNode

ROOT = Path(__file__).resolve().parents[1]
YAML_FILES = sorted(ROOT.glob("*.yaml"))
EXPECTED_YAML = {
    "automations.yaml",
    "configuration.yaml",
    "scripts.yaml",
    "secrets.example.yaml",
    "templates.yaml",
}
EXPECTED_SECRETS = {
    "twilio_account_sid",
    "twilio_auth_token",
    "twilio_sms_from_number",
    "twilio_call_from_number",
    "twilio_contact_number",
}


class HomeAssistantLoader(yaml.SafeLoader):
    """Kleiner Loader, der HA-Tags als überprüfbare Marker erhält."""


def _ha_tag(loader: HomeAssistantLoader, tag_suffix: str, node: ScalarNode) -> str:
    value = loader.construct_scalar(node)
    return f"!{tag_suffix} {value}"


HomeAssistantLoader.add_multi_constructor("!", _ha_tag)


def load(name: str):
    return yaml.load((ROOT / name).read_text(encoding="utf-8"), Loader=HomeAssistantLoader)


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class TwilioSampleContract(unittest.TestCase):
    def test_expected_yaml_files_parse(self):
        self.assertEqual({path.name for path in YAML_FILES}, EXPECTED_YAML)
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
        self.assertEqual(automation_text.count("# Wann:"), 2)

    def test_configuration_contract_and_secret_tags(self):
        config = load("configuration.yaml")
        self.assertEqual(
            config["twilio"],
            {
                "account_sid": "!secret twilio_account_sid",
                "auth_token": "!secret twilio_auth_token",
            },
        )
        self.assertEqual(config["notify"], [
            {
                "platform": "twilio_sms",
                "name": "twilio_sms",
                "from_number": "!secret twilio_sms_from_number",
            },
            {
                "platform": "twilio_call",
                "name": "twilio_call",
                "from_number": "!secret twilio_call_from_number",
            },
        ])
        self.assertEqual(config["automation"], "!include automations.yaml")
        self.assertEqual(config["script"], "!include scripts.yaml")
        self.assertEqual(config["template"], "!include templates.yaml")

    def test_secret_inventory_is_exact_and_placeholder_only(self):
        example = load("secrets.example.yaml")
        self.assertEqual(set(example), EXPECTED_SECRETS)
        self.assertTrue(
            all(isinstance(value, str) and value.startswith("REPLACE_WITH_") for value in example.values())
        )
        references = set()
        for path in YAML_FILES:
            if path.name == "secrets.example.yaml":
                continue
            references.update(re.findall(r"!secret\s+([a-z0-9_]+)", path.read_text(encoding="utf-8")))
        self.assertEqual(references, EXPECTED_SECRETS)

    def test_automation_ids_and_inbound_allowlist(self):
        automations = load("automations.yaml")
        self.assertIsInstance(automations, list)
        self.assertEqual(len(automations), 2)
        ids = [entry["id"] for entry in automations]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.startswith("public_twilio_") for item in ids))
        for entry in automations:
            self.assertIn(entry["mode"], {"single", "queued"})
            self.assertEqual(len(entry["triggers"]), 1)
            trigger = entry["triggers"][0]
            self.assertEqual(trigger["trigger"], "event")
            self.assertEqual(trigger["event_type"], "twilio_data_received")
            self.assertEqual(
                trigger["event_data"],
                {
                    "From": "!secret twilio_contact_number",
                    "To": "!secret twilio_sms_from_number",
                },
            )
            template = entry["conditions"][0]["value_template"]
            self.assertIn("Body", template)

    def test_notify_payload_never_contains_sender(self):
        allowed_payload = {"message", "target", "data", "title"}
        notify_actions = []
        for name in ("automations.yaml", "scripts.yaml"):
            for node in walk(load(name)):
                action = node.get("action")
                if isinstance(action, str) and action.startswith("notify."):
                    notify_actions.append(node)
                    payload = node.get("data", {})
                    self.assertLessEqual(set(payload), allowed_payload)
                    self.assertNotIn("from", payload)
                    self.assertNotIn("from_number", payload)
        for service in ("notify.twilio_sms", "notify.twilio_call"):
            twilio_actions = [item for item in notify_actions if item["action"] == service]
            self.assertEqual(len(twilio_actions), 1)
            self.assertEqual(set(twilio_actions[0]["data"]), {"message", "target"})

    def test_outbound_script_has_fixed_target_and_length_gate(self):
        scripts = load("scripts.yaml")
        self.assertEqual(set(scripts), {"twilio_sms_sicher_senden", "twilio_anruf_sicher_starten"})
        script = scripts["twilio_sms_sicher_senden"]
        self.assertEqual(script["mode"], "queued")
        self.assertEqual(script["max"], 3)
        condition = next(step for step in script["sequence"] if step.get("condition") == "template")
        self.assertIn("<= 320", condition["value_template"])
        action = next(step for step in script["sequence"] if step.get("action") == "notify.twilio_sms")
        self.assertEqual(action["data"]["target"], ["!secret twilio_contact_number"])

        call = scripts["twilio_anruf_sicher_starten"]
        self.assertEqual(call["mode"], "single")
        self.assertNotIn("max", call)
        call_conditions = [step["value_template"] for step in call["sequence"] if step.get("condition") == "template"]
        self.assertTrue(any("<= 240" in item for item in call_conditions))
        self.assertTrue(any("http://" in item and "https://" in item for item in call_conditions))
        call_action = next(step for step in call["sequence"] if step.get("action") == "notify.twilio_call")
        self.assertEqual(call_action["data"]["target"], ["!secret twilio_contact_number"])

    def test_status_sender_and_every_example_target_share_one_secret_identity(self):
        status = next(item for item in load("automations.yaml") if item["id"] == "public_twilio_status_sms_beantworten")
        allowed_sender = status["triggers"][0]["event_data"]["From"]
        self.assertEqual(allowed_sender, "!secret twilio_contact_number")
        for script in load("scripts.yaml").values():
            action = next(step for step in script["sequence"] if str(step.get("action", "")).startswith("notify.twilio_"))
            self.assertEqual(action["data"]["target"], [allowed_sender])

    def test_template_sensor_is_data_minimal(self):
        blocks = load("templates.yaml")
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        trigger = block["triggers"][0]
        self.assertEqual(trigger["event_data"], {
            "From": "!secret twilio_contact_number",
            "To": "!secret twilio_sms_from_number",
        })
        self.assertIn("Body", block["conditions"][0]["value_template"])
        sensor = block["sensor"][0]
        self.assertEqual(sensor["default_entity_id"], "sensor.twilio_letzter_sms_eingang")
        self.assertEqual(sensor["unique_id"], "public_twilio_letzter_sms_eingang")
        serialized = yaml.safe_dump(sensor, allow_unicode=True)
        self.assertNotIn("From", serialized)
        self.assertNotIn("To", serialized)
        self.assertNotIn("MessageSid", serialized)
        self.assertNotIn("trigger.event.data.get('Body', '') | trim", serialized)
        self.assertEqual(set(sensor["attributes"]), {"richtung", "zeichenanzahl"})

    def test_scoped_mit_license_and_readme_notice(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted, free of charge", license_text)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("](LICENSE)", readme)
        self.assertIn("ausschließlich", readme)

    def test_readme_links_every_yaml_and_relative_links_resolve(self):
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
        for name in EXPECTED_YAML:
            self.assertIn(f"]({name})", readme)

    def test_no_credentials_numbers_private_hosts_or_webhook_ids(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "README.md", *YAML_FILES, *sorted((ROOT / "scripts").glob("*.py")), *sorted((ROOT / "tests").glob("*.py"))]
        )
        forbidden = {
            "real_account_sid": r"\bAC[0-9a-fA-F]{32}\b",
            "api_key_sid": r"\bSK[0-9a-fA-F]{32}\b",
            "auth_token_shape": r"(?i)(?:auth[_ -]?token|api[_ -]?key)\s*[:=]\s*['\"]?[A-Za-z0-9]{20,}",
            "e164_literal": r"(?<![A-Za-z0-9_])\+[1-9][0-9]{7,14}\b",
            "webhook_secret": r"/api/webhook/[A-Za-z0-9_-]{20,}",
            "private_ipv4": r"\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\b",
        }
        for label, pattern in forbidden.items():
            with self.subTest(label=label):
                self.assertIsNone(re.search(pattern, text), label)
        self.assertNotIn("github" + "_pat_", text)
        self.assertNotIn("gh" + "p_", text)


VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "twilio_validate", ROOT / "scripts" / "validate.py"
)
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
        return subprocess.run(
            ["git", *args], cwd=self.repo, text=True, capture_output=True, check=check
        )

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
