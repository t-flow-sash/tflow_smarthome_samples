# Haus-Automationen: Heizung, Sicherheit, Energie (anonymisiertes Beispiel)

Dieses **für die öffentliche Nutzung vorgesehene Beispiel in einem eigenständigen Unterordner** beschreibt einen anpassbaren Entwurf, keinen 1:1-Export des Hauses. Es enthält [16 Automationen](docs/codekarte.md), erzeugt aus [scripts/build.py](scripts/build.py) in [packages/haus.yaml](packages/haus.yaml). Die fiktiven `beispiel_*`-Entitäten und die externen Dienste müssen in einer isolierten Instanz ersetzt und nachgewiesen werden. **Nicht plug-and-play, nicht produktionszertifiziert.** Insbesondere ist kein echter Kamera-AI-Dienst enthalten. Weder Freigabe noch Sicherheit eines Live-Systems folgen aus einem erfolgreichen Syntaxcheck.

## Einstieg

1. [Architektur und Datenfluss](docs/architektur.md) – Paket, Helper, Generator und Grenzen.
2. [Heizung: gewichteter Shadow und Kalender](docs/heizung.md) – getrennte Zuständigkeiten, Aktoren und Ownership.
3. [Sicherheit, Abwesenheit und Kameras](docs/sicherheit-kameras.md) – Schutzschalter, Frames und fehlender AI-Transport.
4. [Energie, Tibber und Wallbox](docs/energie.md) – Telemetrie, Tarife und Kostenmodell.
5. [Voraussetzungen und isolierte Einrichtung](docs/setup.md) – Integrationen vs. Add-ons vs. HACS, Entitäten, Secrets, Prüfpfad.
6. [Datenschutz, Betriebsgrenzen und fehlende Funktionen](docs/grenzen.md) – kein Sicherheits- oder Vollständigkeitsversprechen.
7. [Codekarte aller 16 Automationen und übriger Artefakte](docs/codekarte.md) – von Funktion zu konkreter Datei.

Die ältere Sammlung `haus_automationen_2026/` ist unabhängig; deren Ausschlüsse, Tests und Kompatibilitätsaussagen beziehen sich nicht auf dieses Paket. Lizenz nur für diesen Unterordner: [LICENSE](LICENSE). Keine privaten Credentials, Alarmo-UI-Konfiguration oder Hermes-Gateway-Installation werden mitgeliefert. **Vor jeder echten Aktorfreigabe die Grenzen und den Integrationsvertrag lesen.**
