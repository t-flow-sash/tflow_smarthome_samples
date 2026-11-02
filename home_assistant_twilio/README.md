# Home Assistant + Twilio: SMS- und Anruf-Codepaket (Deutsch)

Dieses additive Beispielpaket zeigt eine aktuelle, anonymisierte Twilio-Anbindung für Home Assistant:

- **ausgehende SMS** über den YAML-Notifier `twilio_sms`,
- **ausgehende TTS-Sprachanrufe** über den getrennten YAML-Notifier `twilio_call`,
- **eingehende SMS** über den von der Twilio-Integration erzeugten Home-Assistant-Webhook,
- erlaubnisbasierte Verarbeitung eines `STATUS`-Kommandos,
- eine datensparsame Diagnose-Entity ohne Nachrichtentext oder Telefonnummer,
- Secrets, Kosten- und Sicherheitsgrenzen sowie lokale Vertragsprüfungen.

> **Kein Plug-and-play-Paket und keine Produktionsfreigabe.** Nummern, Account SID, Auth Token, externe URL und Twilio-Konsole müssen zur eigenen Installation passen. Beim Testen können Twilio-Kosten entstehen.

## Dateien

| Datei | Einbauform | Zweck |
|---|---|---|
| [`configuration.yaml`](configuration.yaml) | In bestehende `configuration.yaml` **zusammenführen** | Twilio-Client, getrennte SMS-/Call-Notifier und Includes |
| [`automations.yaml`](automations.yaml) | Als komplette Include-Liste oder einzelne Einträge übernehmen | Eingehende SMS anzeigen und `STATUS` beantworten |
| [`templates.yaml`](templates.yaml) | Als Template-Include-Liste übernehmen | Zeitpunkt/Metadaten des letzten SMS-Eingangs, ohne Inhalt/Nummer |
| [`scripts.yaml`](scripts.yaml) | Als Script-Mapping übernehmen | Getrennte begrenzte SMS- und TTS-Anruf-Scripts |
| [`secrets.example.yaml`](secrets.example.yaml) | Schlüssel nach `secrets.yaml` kopieren und privat befüllen | Dokumentiert alle benötigten Geheimnisse/Nummern |
| [`LICENSE`](LICENSE) | Im Beispielordner belassen | MIT-Nutzungsrechte ausschließlich für diesen Ordner |

Die Dateien bilden zusammen ein minimales Beispiel. Sie dürfen nicht zusätzlich zu identischen, bereits vorhandenen Blöcken installiert werden.

## Architektur

```text
Ausgehend:
Automation / Tools → script.twilio_sms_sicher_senden
                   → notify.twilio_sms
                   → Twilio Messages API → Empfänger

Automation / Tools → script.twilio_anruf_sicher_starten
                   → notify.twilio_call
                   → Twilio Calls API → TTS-Anruf beim festen Kontakt

Eingehend:
Twilio-Nummer → HTTPS-POST an geheimen HA-Webhook
              → Event twilio_data_received
              ├→ persistente HA-Benachrichtigung
              ├→ STATUS-Prüfung → ausgehende Antwort-SMS
              └→ Template-Sensor (nur Zeitpunkt, Richtung, Zeichenanzahl)
```

Wichtig: `twilio_sms` und `twilio_call` sind zwei **getrennte ausgehende Legacy-Notify-Plattformen**. `twilio_sms` versendet Textnachrichten; `twilio_call` startet einen Anruf und liest normalen Nachrichtentext per TTS vor. Eingehende SMS kommen dagegen über den separat in der Home-Assistant-UI eingerichteten Twilio-Webhook als Event `twilio_data_received`. Home Assistant erzeugt dabei keine dauerhafte SMS-Entity und der Webhook antwortet nicht mit eigenem TwiML; die `STATUS`-Antwort ist eine neue, kostenpflichtige ausgehende SMS und niemals ein Anruf.

## Voraussetzungen

1. Aktuelles Home Assistant mit Dateizugriff auf die YAML-Konfiguration.
2. Twilio-Konto mit SMS-fähiger Twilio-Nummer bzw. zulässiger Sender-ID; für das optionale Call-Script zusätzlich eine sprachfähige Twilio-Rufnummer. Eine alphanumerische SMS-Sender-ID ist keine Call-Absendernummer.
3. Für eingehende Events eine von Twilio erreichbare **HTTPS**-Adresse und korrekt gesetzte externe Home-Assistant-URL.
4. Gültige Empfänger-/Absenderfreigaben, Länder-, Messaging- und Registrierungsregeln von Twilio. Für US-Ziele gelten insbesondere die aktuellen A2P-10DLC-/Toll-Free-Vorgaben.
5. Ein Backup der vorhandenen Home-Assistant-Konfiguration.

## Einrichtung

### 1. Secrets privat anlegen

Die Schlüssel aus [`secrets.example.yaml`](secrets.example.yaml) in die echte, **nicht veröffentlichte** `secrets.yaml` übernehmen:

- `twilio_account_sid`: beginnt bei Twilio üblicherweise mit `AC`;
- `twilio_auth_token`: vertraulicher API-Schlüssel;
- `twilio_sms_from_number`: eigene SMS-fähige Twilio-Nummer im E.164-Format;
- `twilio_call_from_number`: eigene sprachfähige Twilio-Nummer im E.164-Format;
- `twilio_contact_number`: **eine einzige Kontaktidentität**, die zugleich erlaubter eingehender Absender und festes Ziel aller SMS-/Call-Beispiele ist.

Telefonnummern mit führendem `+` immer quoten. Auth Token, Account SID und Webhook-URL niemals committen, posten oder in Screenshots zeigen.

### 2. YAML einbauen

Das Beispiel in [`configuration.yaml`](configuration.yaml) ist eine **Zusammenführungs-Vorlage**, kein Ersatz für die eigene Hauptdatei:

```yaml
automation: !include automations.yaml
script: !include scripts.yaml
template: !include templates.yaml
```

Existieren diese Schlüssel bereits, nicht duplizieren. Stattdessen die verlinkten Listen/Mapping-Einträge in die vorhandenen Dateien übernehmen. `twilio:` und die beiden benannten Einträge unter `notify:` dürfen ebenfalls nur einmal passend vorhanden sein. Die Namen erzeugen die getrennten Actions `notify.twilio_sms` und `notify.twilio_call`.

**Schema-Grenze:** `from_number` gehört bei beiden Plattformen ausschließlich in die jeweilige `notify:`-Konfiguration. In den hier gezeigten Actions stehen nur `message` und `target`; ein `from`/`from_number` in der Action ist falsch. SMS-spezifische Optionen wie `media_url` gehören nicht in einen Call-Payload.

Nach dem Einbau zuerst **Entwicklerwerkzeuge → YAML → Konfiguration prüfen** verwenden. Neue/geänderte YAML-Integrationen und Secrets erfordern im Regelfall einen kontrollierten Home-Assistant-Neustart; ein bloßer Automation-Reload lädt die Twilio-Basiskonfiguration nicht neu.

### 3. Twilio-Webhooks für eingehende Daten

1. In Home Assistant **Einstellungen → Geräte & Dienste → Twilio → Konfigurieren** öffnen und den „Twilio Webhook“ anlegen.
2. Die erzeugte URL vertraulich kopieren. Sie enthält eine geheime Webhook-ID.
3. In der Twilio Console zu **Phone Numbers → Manage → Active numbers → eigene Nummer → Configure** wechseln.
4. Unter **A message comes in** die Home-Assistant-Webhook-URL mit Methode **HTTP POST** eintragen und speichern.
5. „A call comes in“ nur dann auf dieselbe URL setzen, wenn eigene, getrennt gefilterte Call-Automationen vorgesehen sind. Dieses Paket verarbeitet absichtlich nur SMS-Daten mit einem nichtleeren `Body`.

Die UI-Webhook-Konfiguration enthält keine Account SID und keinen Auth Token und ersetzt daher nicht den YAML-Block für ausgehende Nachrichten. Der untersuchte Home-Assistant-Core-Handler prüft keine zusätzliche `X-Twilio-Signature`; die nicht erratbare Webhook-URL ist deshalb wie ein Secret zu behandeln. Home Assistant nur über einen gepflegten HTTPS-Reverse-Proxy/Cloud-Zugang exponieren und keine beliebigen Internet-Ports öffnen.

## Nutzung

### Ausgehende SMS

Das SMS-Script aus [`scripts.yaml`](scripts.yaml) hält den Empfänger fest in `!secret twilio_contact_number`, entfernt Außen-Whitespace und akzeptiert 1 bis 320 Zeichen. Aufruf aus einer eigenen Automation:

```yaml
- action: script.twilio_sms_sicher_senden
  data:
    message: "Home Assistant meldet: Beispieltext"
```

Alternativ das Script in **Entwicklerwerkzeuge → Aktionen** auswählen. Dieser Aufruf sendet eine echte SMS und kann Kosten erzeugen.

### Ausgehender TTS-Anruf

Das bewusst separat benannte `script.twilio_anruf_sicher_starten` verwendet `notify.twilio_call`, denselben festen Kontakt und maximal 240 Zeichen. HTTP(S)-Nachrichten werden abgelehnt, weil `twilio_call` eine damit beginnende Nachricht als Twimlet-/TwiML-URL statt als normalen TTS-Text behandeln kann:

```yaml
- action: script.twilio_anruf_sicher_starten
  data:
    message: "Home Assistant meldet eine Störung."
```

Dieser Aufruf startet einen echten kostenpflichtigen Telefonanruf. Er ist weder eine SMS-Antwort noch Teil des `STATUS`-Flows. Twilio-Trialkonten können nur verifizierte Ziele erreichen; Sprachfähigkeit, Länderfreigaben und Anrufpreise separat prüfen.

### Eingehende SMS

[`automations.yaml`](automations.yaml) und der trigger-basierte Sensor in [`templates.yaml`](templates.yaml) akzeptieren nur Events, deren `From` und `To` denselben privaten Secrets entsprechen und deren `Body` nicht leer ist:

- Jede erlaubte, nichtleere SMS wird als persistente HA-Benachrichtigung angezeigt.
- Der exakte Befehl `STATUS` (Groß-/Kleinschreibung und Rand-Whitespace werden normalisiert) löst über das Script eine kurze Antwort aus.
- Andere Absender oder eine andere Zielnummer führen keine Action aus.
- Der erlaubte `From`-Wert und das feste Antwort-/Beispielziel referenzieren beide exakt `twilio_contact_number`; ein erlaubter Kontakt kann daher nicht den Versand an eine zweite Secret-Identität auslösen.

Dies ist lediglich eine Allowlist, keine starke Absenderauthentifizierung: Telefonnummern und Webhooks können angegriffen oder fehlkonfiguriert werden. Keine Schlösser, Tore, Alarmanlagen oder andere sicherheitskritische Aktoren allein durch eine SMS schalten.

## Datenschutz, Kosten und Sicherheit

- Eingehende SMS-Texte erscheinen in persistenten Benachrichtigungen und können je nach Recorder-/Log-Konfiguration Spuren hinterlassen. Keine Passwörter, Tokens, Gesundheits- oder hochsensiblen Daten per SMS senden.
- [`templates.yaml`](templates.yaml) speichert absichtlich nur Zeitpunkt, Richtung und Zeichenanzahl – weder Text noch Nummer.
- SMS können pro Segment, Land, Zeichensatz, Absenderart und Richtung kosten. 320 Zeichen sind nur ein Kostenlimit des Beispiels, **keine Ein-Segment-Garantie** (Unicode/GSM-7 und Multipart beachten).
- Twilio Trial, Länderfreigaben, verifizierte Ziele, Sender-ID-Fähigkeit und Registrierungen können Versand oder Empfang begrenzen.
- Sprachanrufe werden nach eigenen Voice-Tarifen, Ziel und Dauer berechnet. Die 240-Zeichen-Grenze begrenzt nur dieses Beispiel und garantiert weder Dauer noch Preis.
- Der Webhook muss geheim bleiben. Bei Offenlegung in Home Assistant neu erzeugen und in Twilio ersetzen.
- Das SMS-Script ist `mode: queued` mit maximal drei Läufen; das Call-Script ist `mode: single` und startet keinen zweiten Lauf parallel. Das verhindert keine zeitlich wiederholte Auslösung. Für produktive Alarmierung zusätzlich Cooldown, Budgetalarm und Provider-Monitoring vorsehen.
- Eine erfolgreiche Home-Assistant-Action beweist nicht die Zustellung. Twilio Message SID, Status und Fehlercode in der Twilio Console prüfen, ohne sie öffentlich zu posten.

## Test und Fehlerdiagnose

1. **Ohne SMS-Kosten:** lokale Tests ausführen:
   ```bash
   python3 -m unittest discover -s home_assistant_twilio/tests -v
   python3 home_assistant_twilio/scripts/validate.py
   ```
2. **Home Assistant:** Konfiguration prüfen, kontrolliert neu starten und danach unter Entwicklerwerkzeuge sicherstellen, dass `notify.twilio_sms`, `notify.twilio_call`, beide Scripts und `sensor.twilio_letzter_sms_eingang` vorhanden sind.
3. **Ausgehend:** Bei Fehlern zuerst Automation-/Script-Trace prüfen. `from` oder `from_number` im Action-Payload entfernen; der Sender steht in [`configuration.yaml`](configuration.yaml). Danach Twilio-Logs/Message-Status prüfen.
4. **Eingehend:** In **Entwicklerwerkzeuge → Ereignisse** kurzzeitig auf `twilio_data_received` lauschen, eine bewusst erlaubte Testnachricht senden und danach das Lauschen beenden. Keine Event-Daten veröffentlichen. Fehlt das Event, externe URL, Twilio-Webhook, POST-Methode, TLS/Proxy und Zielnummer prüfen.
5. **Event vorhanden, keine Automation:** `From`/`To`, `Body`, Automation-Trace und die Secret-Werte vergleichen. Nummern müssen im selben E.164-Format vorliegen.
6. **Automation lief, keine SMS:** Script-Trace → `notify.twilio_sms` → Twilio Message Log in dieser Reihenfolge prüfen. HA-Ausführung, Providerannahme und Zustellung sind drei getrennte Grenzen.

Keine Probe-SMS ist Teil der Repository-Tests; kostenpflichtige End-to-End-Tests erfolgen nur bewusst durch den Betreiber.

## Offizielle Quellen

- [Home Assistant: Twilio](https://www.home-assistant.io/integrations/twilio/)
- [Home Assistant: Twilio SMS](https://www.home-assistant.io/integrations/twilio_sms/)
- [Home Assistant: Twilio Call](https://www.home-assistant.io/integrations/twilio_call/)
- [Home Assistant: Template](https://www.home-assistant.io/integrations/template/)
- [Home Assistant: Notifications](https://www.home-assistant.io/integrations/notify/)
- [Twilio: Webhooks](https://www.twilio.com/docs/usage/webhooks)
- [Twilio: Telefonnummern im E.164-Format](https://www.twilio.com/docs/glossary/what-e164)

Geprüft gegen die am 2. November 2026 veröffentlichte Home-Assistant-Dokumentation (Core 2026.10.4) und die zugehörigen Core-Schemata. Vor einem späteren Einsatz die verlinkten Seiten erneut prüfen.

## Lizenz

Die Dateien **ausschließlich in `home_assistant_twilio/`** stehen unter der [MIT-Lizenz](LICENSE). Diese ordnerspezifische Lizenz ändert weder die Lizenzlage im Repository-Root noch die Nutzungsrechte anderer Verzeichnisse.
