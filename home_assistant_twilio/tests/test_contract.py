"""Vertragstests für das öffentliche Home-Assistant-Twilio-Beispiel."""

from __future__ import annotations

import re
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
    "twilio_from_number",
    "twilio_recipient_number",
    "twilio_allowed_sender_number",
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
        self.assertEqual(
            config["notify"],
            [
                {
                    "platform": "twilio_sms",
                    "name": "twilio_sms",
                    "from_number": "!secret twilio_from_number",
                }
            ],
        )
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
                    "From": "!secret twilio_allowed_sender_number",
                    "To": "!secret twilio_from_number",
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
        twilio_actions = [item for item in notify_actions if item["action"] == "notify.twilio_sms"]
        self.assertEqual(len(twilio_actions), 1)
        self.assertEqual(set(twilio_actions[0]["data"]), {"message", "target"})

    def test_outbound_script_has_fixed_target_and_length_gate(self):
        scripts = load("scripts.yaml")
        self.assertEqual(set(scripts), {"twilio_sms_sicher_senden"})
        script = scripts["twilio_sms_sicher_senden"]
        self.assertEqual(script["mode"], "queued")
        self.assertEqual(script["max"], 3)
        condition = next(step for step in script["sequence"] if step.get("condition") == "template")
        self.assertIn("<= 320", condition["value_template"])
        action = next(step for step in script["sequence"] if step.get("action") == "notify.twilio_sms")
        self.assertEqual(action["data"]["target"], ["!secret twilio_recipient_number"])

    def test_template_sensor_is_data_minimal(self):
        blocks = load("templates.yaml")
        self.assertEqual(len(blocks), 1)
        sensor = blocks[0]["sensor"][0]
        self.assertEqual(sensor["default_entity_id"], "sensor.twilio_letzter_sms_eingang")
        self.assertEqual(sensor["unique_id"], "public_twilio_letzter_sms_eingang")
        serialized = yaml.safe_dump(sensor, allow_unicode=True)
        self.assertNotIn("From", serialized)
        self.assertNotIn("To", serialized)
        self.assertNotIn("MessageSid", serialized)
        self.assertNotIn("trigger.event.data.get('Body', '') | trim", serialized)
        self.assertEqual(set(sensor["attributes"]), {"richtung", "zeichenanzahl"})

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


if __name__ == "__main__":
    unittest.main()
