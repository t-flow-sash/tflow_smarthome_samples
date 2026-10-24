# Architektur und Datenfluss

[← Übersicht](../README.md) · [Codekarte](codekarte.md) · [Einrichtung](setup.md)

```text
Externe HA-Integrationen/Adapter (fiktive beispiel_*-IDs)
  ├─ BT + W600 + Wolf + Kalender → Template-Sensoren → Shadow / Kalender-Aktoren
  ├─ Personen + Tür + Alarmo + Kameras → Sicherheits- und Snapshot-Automationen
  └─ Tibber + EcoFlow + Wallbox → Preis-/Leistungs-Templates → Ladefreigabe/Kosten
                                   ↓
                 packages/haus.yaml (16 Automationen, Helper, Skript,
                 Template-/Integrationssensoren, shell-/rest_command)
                                   ↓
     /media/demo_camera ← camera.snapshot; Wartung: demo_camera_media.py
     optionaler REST-POST → externer authentifizierter Gateway/AI-Service
                            (NICHT Bestandteil dieses Repositories)
```

[Generator](../scripts/build.py) ist die editierbare Quelle des [generierten HA-Pakets](../packages/haus.yaml). Änderungen am Paket nicht isoliert vornehmen: Generator ausführen und Diff prüfen. [configuration.yaml](../configuration.yaml) ist ausschließlich eine minimale Konfiguration für eine **neue, wegwerfbare** HA-Instanz, kein Patch für eine bestehende Installation. Die im Paket erzeugten `input_boolean`, `input_number`, `input_text`, Template-Sensoren und Integrationssensoren sind interne Beispielzustände; alle `beispiel_*`-Entitäten sind externe Adapter und werden nicht automatisch erzeugt. Eine Liste sämtlicher Automationen, Eingänge und Ausgänge steht in der [Codekarte](codekarte.md).

Das Heiz-Shadow-Signal schreibt nur einen HA-Helper. Nur die **separate** Kalenderautomation kann nach eigener Freigabe BT-Presets und das Wolf-DHK-Select verändern. Sicherheitsschalter, Kalender- und Ladefreigabe starten explizit ausgeschaltet. Die Aufnahme-Automationen lösen lediglich lokale JPEG-Snapshots und einen Best-Effort-Abschluss-POST aus. Der [lokale Receiver](../scripts/camera_episode_receiver.py) ist ein Validator/Dateiselektor per CLI, weder HTTP-Server noch AI-Modell. Integration, Veröffentlichung und Live-Betrieb sind getrennte Schritte; grüne lokale Tests ersetzen keine realen Adapter- oder Geräteprüfungen.
