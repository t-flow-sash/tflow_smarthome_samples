# Codekarte: Funktion → Implementierung

[← Übersicht](../README.md) · [Architektur](architektur.md) · [Grenzen](grenzen.md)

**Alle 16 Automationen** sind unter `automation:` in [packages/haus.yaml](../packages/haus.yaml) enthalten und werden durch [scripts/build.py](../scripts/build.py) erzeugt. Jede Zeilen-ID verweist jetzt direkt auf eine einzeln kopierbare YAML-Datei (als Listenelement für `automations.yaml`). Externe `beispiel_*`-Adapter werden [separat benötigt](setup.md). Automationen sind keine vollständigen Integrationen oder AI-Anwendungen.

| ID im YAML (`public_…`) | Funktion / Eingänge → Ausgang | Detail |
|---|---|---|
| [`wolf_shadow`](../themen/heizung/automation/wolf_shadow.yaml) | BT-/W600-Templates → `input_boolean.demo_shadow`, **kein Wolf-Aktor** | [Heizung](heizung.md) |
| [`kalender_abwesenheit`](../themen/heizung/automation/kalender_abwesenheit.yaml) | `[Heizung]`-Kalender → optional BT-Preset und Wolf-DHK-Select | [Heizung](heizung.md) |
| [`aufnahme_bei_abwesenheit`](../themen/sicherheit/automation/aufnahme_bei_abwesenheit.yaml) | Personen/Nacht/Freigabe → sechs Aufnahme-Schalter mit Ownership | [Sicherheit](sicherheit-kameras.md) |
| [`schloss_abwesenheit`](../themen/sicherheit/automation/schloss_abwesenheit.yaml) | explizit abwesend + Tür zu → Schloss-Skript | [Sicherheit](sicherheit-kameras.md) |
| [`alarm_meldung`](../themen/sicherheit/automation/alarm_meldung.yaml) | Alarmo `triggered` → HA-Meldung | [Sicherheit](sicherheit-kameras.md) |
| [`eingang_licht`](../themen/sicherheit/automation/eingang_licht.yaml) | Bewegung → Eingang-Licht/Timer | [Sicherheit](sicherheit-kameras.md) |
| [`display_klingel`](../themen/sicherheit/automation/display_klingel.yaml) | Klingel → Displaylicht + HA-Meldung | [Sicherheit](sicherheit-kameras.md) |
| [`kamera_retention`](../themen/sicherheit/automation/kamera_retention.yaml) | täglich → lokaler `shell_command.demo_camera_maintain` | [Kameras](sicherheit-kameras.md) |
| [`kamera_zone_01`](../themen/sicherheit/automation/kamera_zone_01.yaml) | Zone 01 Erkennung → Snapshot + optionaler Finish-POST | [Kameras](sicherheit-kameras.md) |
| [`kamera_zone_02`](../themen/sicherheit/automation/kamera_zone_02.yaml) | Zone 02 Erkennung → Snapshot + optionaler Finish-POST | [Kameras](sicherheit-kameras.md) |
| [`kamera_zone_03`](../themen/sicherheit/automation/kamera_zone_03.yaml) | Zone 03 Erkennung → Snapshot + optionaler Finish-POST | [Kameras](sicherheit-kameras.md) |
| [`kamera_zone_04`](../themen/sicherheit/automation/kamera_zone_04.yaml) | Akku-Zone 04 Erkennung → Readiness-Wartezeit, Snapshot + POST | [Kameras](sicherheit-kameras.md) |
| [`kamera_zone_05`](../themen/sicherheit/automation/kamera_zone_05.yaml) | Akku-Zone 05 Erkennung → Readiness-Wartezeit, Snapshot + POST | [Kameras](sicherheit-kameras.md) |
| [`kamera_zone_06`](../themen/sicherheit/automation/kamera_zone_06.yaml) | Akku-Zone 06 Erkennung → Readiness-Wartezeit, Snapshot + POST | [Kameras](sicherheit-kameras.md) |
| [`wallbox_freigabe`](../themen/energie/automation/wallbox_freigabe.yaml) | Preis/Anschluss/Person/Ladestatus → Wallbox-Ladeerlaubnis | [Energie](energie.md) |
| [`ladekosten`](../themen/energie/automation/ladekosten.yaml) | Zähler/Preis/Ladestatus → aktuelle und letzte geschätzte Sitzung | [Energie](energie.md) |

Weitere Lieferartefakte:

| Datei | Rolle |
|---|---|
| [packages/haus.yaml](../packages/haus.yaml) | Generiertes HA-Paket: 16 Automationen, `demo_abschliessen`-Skript, Freigabe-/Ownership-/Kosten-Helper, Template-/Integrationssensoren, `rest_command` und `shell_command`. |
| [scripts/build.py](../scripts/build.py) | Generator; nach Änderungen erneut laufen lassen und Paket-Diff prüfen. |
| [configuration.yaml](../configuration.yaml) | Ausschließlich leere isolierte Testinstanz; nie bestehende Config überschreiben. |
| [scripts/camera_media.py](../scripts/camera_media.py) | Lokales `prepare`/`maintain` für `/media`-JPEG-Verzeichnisse und Retention. |
| [scripts/camera_episode_receiver.py](../scripts/camera_episode_receiver.py) | JSON-stdin-Validator/Dateiselektor, **kein** HTTP-Server/AI-Worker. |
| [requirements.txt](../requirements.txt) | Lokale Build-/Test-Dependencies, kein Installationsmanifest der HA-Integrationen. |
| [tests/test_contract.py](../tests/test_contract.py), [tests/test_edges.py](../tests/test_edges.py), [tests/test_episode.py](../tests/test_episode.py), [tests/test_docs.py](../tests/test_docs.py) | YAML-/Jinja-/Privacy-/Episode-/Dokumentations-Verträge; keine Live-Aktorik. |
| [LICENSE](../LICENSE) | Lizenz dieses Unterordners. |
