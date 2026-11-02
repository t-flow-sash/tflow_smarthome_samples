# Home Assistant: finale Kamera-AI-Kurzfassung per Twilio-SMS

Dieses anonymisierte Beispiel bildet **genau einen real eingesetzten Use Case** ab: Ein externer Kamera-AI-Prozess meldet nach Abschluss einer Episode ein `camera_ai_summary_ready`-Event an Home Assistant. Home Assistant prüft den Vertrag, verhindert das unmittelbar gleiche Replay bestmöglich und übergibt ausschließlich die eigens formulierte `sms_summary` an einen generischen Twilio-SMS-Notifier.

Nicht enthalten sind Kamera-/Snapshot-Producer, eingehende SMS, Empfangs-Webhooks, SMS-Befehle, Telefonanrufe, Template-Sensoren oder Versand-Scripts. Das Paket sendet bei Installation oder Tests **keine** SMS.

> **Beispiel, nicht Plug-and-play.** Kamera-IDs, Zielnummer, Sender-ID, Twilio-Freigaben und externe Event-Erzeugung müssen zur eigenen Installation passen. SMS können Kosten verursachen und sensible Kamera-Informationen über Dritte transportieren.

## Navigation

- [Dateien](#dateien)
- [Datenfluss und Eventvertrag](#datenfluss-und-eventvertrag)
- [Einrichtung](#einrichtung)
- [GitOps, Prüfung und Neustart](#gitops-prüfung-und-neustart)
- [Replay-, Zustell- und Kostengrenzen](#replay-zustell--und-kostengrenzen)
- [Datenschutz](#datenschutz)
- [Lokale Tests](#lokale-tests)

## Dateien

| Datei | Einbauform | Zweck |
|---|---|---|
| [`configuration.yaml`](configuration.yaml) | Blöcke in die eigene Hauptkonfiguration **zusammenführen** | Twilio-Zugang, generischer Notifier, restore-fähige Marker und Automation-Include |
| [`automations.yaml`](automations.yaml) | Einen Listeneintrag übernehmen oder als Automation-Liste einbinden | Event prüfen, Kurzfassung senden, danach Marker schreiben |
| [`secrets.example.yaml`](secrets.example.yaml) | Zwei Schlüssel privat nach `secrets.yaml` übertragen | Benötigte Twilio-Zugangsdaten dokumentieren |
| [`LICENSE`](LICENSE) | Im Beispielordner belassen | MIT-Lizenz ausschließlich für diesen Ordner |

Es gibt bewusst keine `templates.yaml` und keine Laufzeit-`scripts.yaml`.

## Datenfluss und Eventvertrag

```text
externer, finaler Kamera-AI-Producer
  → Home-Assistant-Event camera_ai_summary_ready
  → Schema- und Kamera-Allowlist
  → Best-Effort-Replay-Prüfung im passenden input_text
  → notify.twilio_wichtige_sms (nur sms_summary)
  → erst danach Replay-Marker aktualisieren
```

Der externe Producer ist **nicht Teil dieses Repositories**. Er muss das Event erst nach einer abgeschlossenen Analyse mit genau diesen Feldern erzeugen:

| Feld | Vertrag |
|---|---|
| `camera` | String aus der festen Allowlist `camera_01` bis `camera_08` |
| `episode_id` | String aus exakt 32 kleingeschriebenen Hex-Zeichen |
| `summary` | Nichtleere vollständige Zusammenfassung; wird validiert, aber nicht per SMS gesendet |
| `sms_summary` | Eigene Kurzfassung: roh und nach Trim jeweils höchstens 140 Zeichen, nach Trim nichtleer und ohne C0-/DEL-Steuerzeichen (einschließlich CR/LF) |

`summary` und `sms_summary` sind absichtlich getrennt. Die Automation schneidet den Volltext nicht ab und verwendet ihn nicht als Fallback. Zusätzliche Eventfelder bestimmen weder Ziel noch Nachricht.

Beispiel nur zur Formprüfung in **Entwicklerwerkzeuge → Ereignisse** (nicht als Repository-Test ausführen):

```yaml
event_type: camera_ai_summary_ready
event_data:
  camera: camera_01
  episode_id: 0123456789abcdef0123456789abcdef
  summary: "Vollständige, extern finalisierte Beispielzusammenfassung."
  sms_summary: "Kurze, eigenständig formulierte Beispielmeldung."
```

Das manuelle Feuern dieses Events würde bei fertig eingerichtetem Twilio einen kostenpflichtigen Versand auslösen. Daher ist es kein empfohlener Konfigurations- oder Repository-Test.

## Einrichtung

### 1. Secrets privat setzen

Die beiden Schlüssel aus [`secrets.example.yaml`](secrets.example.yaml) in die echte, nicht versionierte `/config/secrets.yaml` übernehmen:

- `twilio_account_sid`
- `twilio_auth_token`

Keine echten Werte in Git, Logs, Screenshots oder Support-Posts kopieren.

### 2. YAML zusammenführen

Die Blöcke aus [`configuration.yaml`](configuration.yaml) in die vorhandene Hauptdatei einbauen. Bestehende Top-Level-Keys wie `notify:`, `input_text:` oder `automation:` erweitern statt duplizieren. [`automations.yaml`](automations.yaml) ist eine Liste mit genau einer Automation.

Die acht `input_text`-Helfer haben bewusst **kein** `initial:`. Dadurch kann Home Assistant den letzten Zustand wiederherstellen. Namen und `camera_01` bis `camera_08` gemeinsam anpassen, damit dynamischer Helpername und Allowlist deckungsgleich bleiben.

`from_number: HomeAlert` ist eine anonymisierte alphanumerische Beispiel-Sender-ID. Vor Nutzung prüfen, ob Twilio sie für Zielregion, Konto und Nachrichtentyp unterstützt; andernfalls privat eine zulässige Absenderidentität konfigurieren.

### 3. Festes Ziel ersetzen

In [`automations.yaml`](automations.yaml) ist `+491234567890` ein offensichtlich anonymisierter E.164-Beispielplatzhalter. Vor produktivem Einsatz genau dieses feste Ziel durch die eigene zulässige, quoted E.164-Nummer ersetzen. Das Ziel bleibt in der Automation fest und darf niemals aus Eventdaten stammen.

## GitOps, Prüfung und Neustart

1. Änderungen nur im eigenen Konfigurations-Repository vornehmen; `secrets.yaml` bleibt außerhalb von Git.
2. Diff prüfen und sicherstellen, dass keine echten Nummern, SIDs, Tokens, Webhook-IDs oder privaten Hosts enthalten sind.
3. Lokal die [Vertragstests](#lokale-tests) ausführen.
4. In Home Assistant **Entwicklerwerkzeuge → YAML → Konfiguration prüfen** verwenden oder offline den nativen `check_config` gegen die eingesetzte Core-Version ausführen.
5. Erst nach erfolgreicher Prüfung kontrolliert neu starten. Neue/geänderte `twilio:`, `notify:`- und Secret-Konfiguration wird nicht durch einen bloßen Automation-Reload vollständig aktiviert.
6. Nach dem Neustart nur die Existenz von `notify.twilio_wichtige_sms`, der Automation und aller acht Helper prüfen. Dafür kein Event auslösen und keine Probe-SMS senden.

## Replay-, Zustell- und Kostengrenzen

- `mode: queued` mit `max: 20` serialisiert angenommene Läufe, ist aber keine dauerhafte Queue. Überlauf, Neustart oder Fehler können Events verlieren.
- Ein vorhandener Helper im Zustand `unknown` darf beim Erststart senden. Ein fehlender Helper oder Zustand `unavailable` blockiert fail-closed.
- Der Marker wird erst nach erfolgreicher Rückkehr der Notify-Aktion geschrieben. Ein Abbruch danach, aber vor dem Marker-Schreibvorgang kann eine doppelte SMS ermöglichen.
- Pro Kamera wird nur die **letzte** Episoden-ID gespeichert. `A → B → A` kann `A` erneut senden; Restore kann beim Start noch nicht rechtzeitig verfügbar sein. Das ist Best-Effort-Replay-Schutz, kein Exactly-once-Verfahren.
- 140 Zeichen sind weder eine Ein-Segment- noch eine Preisgarantie. GSM-7, Unicode, Multipart, Land, Absenderart, Registrierung und Twilio-Tarif beeinflussen Segmente, Preis und Annahme.
- Eine ohne Fehler beendete Home-Assistant-Aktion beweist keine Zustellung. Providerannahme, Message-Status und tatsächliche Zustellung sind getrennte Grenzen und werden von diesem Paket nicht behauptet.

## Datenschutz

Kamera-Zusammenfassungen können Personen, Verhalten, Orte oder andere sensible Inhalte beschreiben. SMS sind nicht Ende-zu-Ende-verschlüsselt und werden von Home Assistant, Twilio, beteiligten Netzbetreibern und dem Zielgerät verarbeitet beziehungsweise je nach Konfiguration protokolliert. Kurzfassungen datensparsam formulieren, Aufbewahrung und Zugriffe begrenzen und nur mit einer geeigneten Rechtsgrundlage versenden.

Dieses Beispiel nimmt nichts entgegen: Es konfiguriert keinen Twilio-Empfangswebhook und verarbeitet keine eingehenden Nachrichten. Es startet auch keine Telefonanrufe.

## Lokale Tests

Ohne Providerzugriff und ohne SMS-Kosten:

```bash
python3 -m unittest discover -s home_assistant_twilio/tests -v
python3 home_assistant_twilio/scripts/validate.py
```

Der Validator prüft den exakten YAML-/Dokumentationsvertrag und drei getrennte Whitespace-Gates: Candidate-Diff gegen die Merge-Base, Index und Arbeitsbaum. Der native Home-Assistant-Check wird separat mit der Zielversion ausgeführt; er ist kein Zustelltest.

## Offizielle Quellen

- [Home Assistant: Twilio](https://www.home-assistant.io/integrations/twilio/)
- [Home Assistant: Twilio SMS](https://www.home-assistant.io/integrations/twilio_sms/)
- [Home Assistant: Notifications](https://www.home-assistant.io/integrations/notify/)
- [Twilio: SMS-Zeichen und Segmente](https://www.twilio.com/docs/glossary/what-sms-character-limit)
- [Twilio: E.164](https://www.twilio.com/docs/glossary/what-e164)

## Lizenz

Die Dateien **ausschließlich in `home_assistant_twilio/`** stehen unter der [MIT-Lizenz](LICENSE). Diese ordnerspezifische Lizenz ändert weder die Lizenzlage im Repository-Root noch die Nutzungsrechte anderer Verzeichnisse.
