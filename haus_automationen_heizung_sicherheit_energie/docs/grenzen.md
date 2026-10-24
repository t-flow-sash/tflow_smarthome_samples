# Datenschutz, Risiken und was ausdrücklich fehlt

[← Übersicht](../README.md) · [Einrichtung](setup.md) · [Codekarte](codekarte.md)

## Publikation ≠ Produktionsfreigabe

Dieser Unterordner ist als anonymisiertes öffentliches **Beispiel** gedacht; seine Veröffentlichung bedeutet weder unabhängige Sicherheitsabnahme noch lauffähige 1:1-Rekonstruktion. Keine realen Namen, Adressen, Topologien, Token oder Geräteschlüssel gehören hierhin. Im übrigen, älteren Repository-Verlauf wurden bereits private Netzwerkadressen in zwei Baseline-Dateien festgestellt: Der neue Unterordner macht **nicht** die komplette Git-History anonym. Eine gesonderte History-/Privacy-Prüfung vor Repository-weiten Aussagen bleibt notwendig. Die ältere Sammlung `haus_automationen_2026/` bleibt unberührt.

Alle angemeldeten HA-Benutzer können lokale Medien unter `/media` über Media Source sehen. Restriktive POSIX-Rechte schützen **nicht** gegen andere autorisierte HA-Konten. `/media` nicht via unauthentifizierten HTTP-/SMB-Share ausliefern. Bei vertraulichem Videomaterial eine dedizierte HA-Instanz mit wenigen Konten oder eine eigene abgesicherte Ablage außerhalb `/media` samt autorisiertem Transfer entwickeln; dafür müssten Snapshot-Pfade, Wartungshelfer und Validator angepasst und getestet werden. Die tägliche Alters-/Größenwartung ist Best-Effort, kein Speicher- oder Löschgarant. Der Receiver gibt lokale `sample_paths` aus: nur in vertrauenswürdigem Prozess verwenden und nicht ungefiltert in Logs/Netz weitergeben. Vertrauenswürdigen `shell_command`-Code prüfen; untrusted PRs nie direkt in produktives HA übernehmen.

## Nicht gelieferte Funktionen – für „gesamten nötigen Code“ wesentlich

| Bereich | In diesem Unterordner | Was für echte End-to-End-Funktion fehlt |
|---|---|---|
| Bedarfsgeführte Wolf-Heizkreisregelung | Gewichtetes **Shadow**-Signal | Physischer Shadow→Wolf-Aktor, eigene Freigabe, Zustands-Readback und Ausfall-/Eigentümerkonzept. Kalender-DHK-Standby ist **nicht** dasselbe. |
| Kalender-Aktoren | BT-Eco/Normal und Wolf-DHK-Standby/Auto mit separaten Freigaben/Ownership | Echte BT-/Wolf-Integration, gültige Entities und Hardware-Abnahme; keine Warmwasser-Programmierung. Crash zwischen Aktor und Marker bleibt nicht atomar. |
| Alarm / Sicherheit | Beobachtung von Alarmo `triggered`, Schließen mit Readback, HA-Meldungen, Licht/Recorder | Alarmo-Integration und **UI-seitige** Modi/Sensor-Mitgliedschaft/Aktivierung; keine Scharf-/Unscharfschaltung, kein Entriegeln, keine zertifizierte Einbruchssicherung oder Push-/Dashboard-Flow. |
| Kamera-AI | Sechs Snapshot-Automationen, lokale JPEG-Wartung und Validator-CLI, einmaliger Best-Effort-POST | Authentifizierter HTTP-Finish-Receiver, Hermes-Gateway-/Profilkonfiguration, abgesicherter Bildtransfer/Media-Source-Brücke, AI-Modell/Tool-Aufruf, persistente Episode/Outbox, Retry/Dedupe, verifizierter JPEG-Zähler und End-to-End-Nachweis. **Kein AI-Service im Code.** |
| Batterie / Tarif / Wallbox | EcoFlow-Telemetrie, Tibber-Preis-Template, Ladeerlaubnis und geschätzte Sitzungskosten | Reale Provider-/Geräteadapter samt Credentials und Mapping; keine EcoFlow-Steuerung, keine abrechnungsfeste Tarifgrenzenmessung oder lückenlose Restart-/Zählerreset-Abrechnung. |
| Betrieb / Reproduktion | Generator, HA-YAML, CLI, syntaktischer Offline-Check und lokale Tests | Secret- und Geräteprovisionierung, reale Adapter-/Serviceverträge, konkurrierende Writer abstimmen, physische Nicht-Aktuierungs-/Ausfalltests, unabhängiger Datenschutz-/Security-Review. |

Der native HA-`check_config` prüft in leerer isolierter Instanz Syntax/Setup, **nicht** tatsächliche Integrationen, Actuator-Readbacks, DST-Ränder, Kamera-Dateischreibvorgänge, HTTP-Zustellung oder AI-Auswertung. Der echte Hermes-Webhook kann schon `202 Accepted` für die Vorverarbeitung zurückgeben, bevor ein Agent fertig ist: auch dieser Status beweist keine Analyse. Fehlende Teile dürfen nicht als plug-and-play oder vollständig getestete Anlagensteuerung beworben werden.
