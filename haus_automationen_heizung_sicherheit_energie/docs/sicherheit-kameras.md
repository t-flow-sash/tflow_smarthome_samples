# Sicherheit, Abwesenheit und sechs Kameras

[← Übersicht](../README.md) · [Einrichtung](setup.md) · [Datenschutz](grenzen.md)

## Sicherheitslogik

Sicherheitsfreigabe ist zu Beginn aus. Für Abwesenheit müssen **beide** Personen explizit `not_home` sein; `unknown` und `unavailable` zählen nicht als Abwesenheit. Nachtmodus ist ein separater Helper. Bei Sicherheitsfreigabe und Bedarf werden die sechs Aufnahme-Schalter angefordert. Nur als paket-eigen markierte Schalter werden bei Wegfall der Nachfrage ausgeschaltet; ein fremd bereits eingeschalteter Schalter bleibt unberührt. Marker sind bei normalen Neustarts persistent, aber Schalteraktion und Ownership-Schreibvorgang sind nicht atomar. Nach Fehler/Crash/manuellem Eingriff prüfen. Der Entzug der Freigabe, auch bei unbekanntem Zustand, blockiert neue Frames vor jedem `camera.snapshot`; ein Best-Effort-Abschluss kann verloren gehen.

Das [Schloss-Skript](../packages/haus.yaml) prüft Freigabe, gültige Abwesenheit und geschlossenen Türkontakt, fordert `lock.lock` an und wartet auf `locked`-Readback. Es gibt **keinen Entriegelungsbefehl**. Alarmo wird hier nur bei `triggered` für eine persistente Meldung beobachtet; **keine Scharf-/Unscharfschaltung**. Alarmo-Modus, Sensor-Mitgliedschaft und Aktivierung werden in der Alarmo-UI vom Betreiber gepflegt und sind nicht aus YAML rekonstruierbar. Bewegung schaltet das Eingang-Licht für drei Minuten, Klingeln das Displaylicht für eine Minute samt HA-Meldung; es wird kein Dashboard-Popup oder Push aufs Telefon mitgeliefert.

## Kamera-Datenfluss

Sechs Zonen, jeweils Person-ODER-Tier-Trigger, Kamera- und Aufnahme-Adapter. Die letzten drei sind als Akku-Kameras modelliert: maximal 30 Sekunden Readiness-Wartezeit, aber **kein Wake-Befehl**. Nach jedem Frame fünf Sekunden Pause; Blöcke zu 100 Versuchen und ein kameragefiltertes Fortsetzungsereignis mit Episode-ID und globalem Index. Jeder Frame prüft Sicherheitsfreigabe, Aufnahme-Schalter, Erkennung und Kamera-Readiness. JPEGs liegen in `/media/demo_camera/zone_XX/`; [Medienhelfer](../scripts/camera_media.py) legt Verzeichnisse an und führt täglich eine Best-Effort-Alters-/Größenbegrenzung aus.

Am normalen Ende gibt es einen einmaligen Best-Effort-`rest_command.demo_camera_finished`-POST. `snapshot_count` zählt **Versuche**, nicht verifiziert geschriebene Dateien. [Receiver-CLI](../scripts/camera_episode_receiver.py) validiert die sieben Metadatenfelder, lokale JPEG-Signaturen und Dateipfade im festen Baum und wählt maximal zwölf Samples aus; die CLI liefert keinen HTTP-Endpunkt, keine Authentisierung und keine Bildanalyse. Reloads, parallele Trigger und Netz-/HTTP-Fehler können Abschlüsse verlieren. Der vollständige, durable AI-Episodenservice mit Auth, Retry, Dedupe, Dateitransfer und Modellverarbeitung ist [nicht enthalten](grenzen.md). `/media` ist über HA Media Source für angemeldete HA-Benutzer sichtbar – POSIX-Rechte sind keine Kontentrennung.
