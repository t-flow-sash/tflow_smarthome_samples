# Haus-Automationen: Heizung, Sicherheit, Energie (anonymisiertes Beispiel)

Dieses **für die öffentliche Nutzung vorgesehene Beispiel in einem eigenständigen Unterordner** beschreibt einen anpassbaren Entwurf, keinen 1:1-Export des Hauses. Es enthält [16 Automationen](docs/codekarte.md), erzeugt aus [scripts/build.py](scripts/build.py) in [packages/haus.yaml](packages/haus.yaml). Die fiktiven `beispiel_*`-Entitäten und die externen Dienste müssen in einer isolierten Instanz ersetzt und nachgewiesen werden. **Nicht plug-and-play, nicht produktionszertifiziert.** Insbesondere ist kein echter Kamera-AI-Dienst enthalten. Weder Freigabe noch Sicherheit eines Live-Systems folgen aus einem erfolgreichen Syntaxcheck.

## Direkt zu YAML nach Thema

- [Heizung: 21 YAML-Bausteine](docs/heizung.md#direkt-kopierbare-yaml-bausteine) – Automationen, Freigabe-/Ownership-Helper und alle Shadow-/W600-Templates.
- [Sicherheit und Kameras: 23 YAML-Bausteine](docs/sicherheit-kameras.md#direkt-kopierbare-yaml-bausteine) – Automationen für sechs Zonen, Helper, Schloss-Skript, REST- und Shell-Command.
- [Energie: 16 YAML-Bausteine](docs/energie.md#direkt-kopierbare-yaml-bausteine) – Automationen, Lade-Helper, Tarif-/EcoFlow-Templates und Integrationssensoren.

Jeder Link auf diesen Themenseiten führt unmittelbar zu einer eigenen `.yaml`-Datei. **Jede Einzeldatei enthält im YAML-Kommentarblock ihren eigenen Zweck, Nutzen, bei Automationen den Auslöser („Wann“), die genaue Listen-/Mapping-Einbauform, benötigte interne/externe Abhängigkeiten, Anpassungshinweise und eine Sicherheitsgrenze.** Diese Kommentare entstehen deterministisch aus [der kanonischen Komponentenbeschreibung](scripts/component_notes.py) über [den Exporter](scripts/export_topics.py), nicht durch manuelle Änderungen an den 60 Dateien. Kommentare ändern weder YAML-Werte noch Jinja/`!secret`-Tags. **Entweder** das [vollständige Paket](packages/haus.yaml) **oder** eine Auswahl der Einzeldateien installieren – nie beides. Bei Einzeldateien gelten [Installationsreihenfolge, YAML-Form und Abhängigkeiten](docs/setup.md#installation-aus-einzeldateien). Die Themen sind ein Code-Index, keine autarken, ohne externe Adapter lauffähigen Systeme.

## Einstieg

1. [Architektur und Datenfluss](docs/architektur.md) – Paket, Helper, Generator und Grenzen.
2. [Heizung: gewichteter Shadow und Kalender](docs/heizung.md) – getrennte Zuständigkeiten, Aktoren und Ownership.
3. [Sicherheit, Abwesenheit und Kameras](docs/sicherheit-kameras.md) – Schutzschalter, Frames und fehlender AI-Transport.
4. [Energie, Tibber und Wallbox](docs/energie.md) – Telemetrie, Tarife und Kostenmodell.
5. [Integrationen und direkt anklickbare Repositories](docs/integrationen.md) – notwendige, austauschbare und optionale HACS-Bausteine, Frontend-Karten sowie Core-Links.
6. [Voraussetzungen und isolierte Einrichtung](docs/setup.md) – Entitäten, Secrets und Prüfpfad.
7. [Datenschutz, Betriebsgrenzen und fehlende Funktionen](docs/grenzen.md) – kein Sicherheits- oder Vollständigkeitsversprechen.
8. [Codekarte aller 16 Automationen und übriger Artefakte](docs/codekarte.md) – von Funktion zu konkreter Datei.

Die ältere Sammlung `haus_automationen_2026/` ist unabhängig; deren Ausschlüsse, Tests und Kompatibilitätsaussagen beziehen sich nicht auf dieses Paket. Lizenz nur für diesen Unterordner: [LICENSE](LICENSE). Keine privaten Credentials, Alarmo-UI-Konfiguration oder Hermes-Gateway-Installation werden mitgeliefert. **Vor jeder echten Aktorfreigabe die Grenzen und den Integrationsvertrag lesen.**
