# Integrationen und Bezugsquellen

[← Übersicht](../README.md) · [Einrichtung und Entity-Vertrag](setup.md) · [Heizung](heizung.md) · [Sicherheit/Kameras](sicherheit-kameras.md) · [Energie](energie.md)

**Geltungsbereich:** Dieses öffentliche YAML-Beispiel installiert **keine** der verlinkten Integrationen. `beispiel_*` sind fiktive Entity-IDs; Betreiber müssen passende Entitäten, Werte, Berechtigungen und Readbacks bereitstellen und vor Aktorfreigabe testen. Die Liste ist eine Orientierung für die hier gezeigten vier Themen, **keine Installationsliste für alle Geräte des Haushalts**. „Erforderlich“ unten gilt nur, wenn der jeweilige konkrete Beispielpfad unverändert übernommen wird; ein anderer Adapter kann die Schnittstelle nachbilden. HACS-Installation, aktivierte Konfiguration, tatsächliche Verwendung und erfolgreich getesteter Ablauf sind verschiedene Aussagen.

## Konkrete Drittanbieter-Integration für unveränderte Pfade

| Thema | Direktes Repository | Art und tatsächlicher Vertrag |
|---|---|---|
| Heizung | [Better Thermostat](https://github.com/KartoffelToby/better_thermostat) | HACS-Custom-Integration `better_thermostat`: neun BT-`climate`-Entities mit Soll/Ist, `hvac_action`, Fehler-/Degradationsprüfung und `eco`/`none`-Presets. Für diesen BT-spezifischen Pfad nötig, **nicht** für die zwei W600-Climates. |
| Sicherheit | [Alarmo](https://github.com/nielsfaber/alarmo) | HACS-Custom-Integration für den unveränderten `alarm_control_panel.beispiel_alarmo`-Statuspfad. Das Sample reagiert nur auf `triggered`; Alarmmodi, Kontakte und Scharfschaltung bleiben eine separate UI-Einrichtung und werden nicht mitgeliefert. Wer den Statuspfad weglässt oder auf einen kompatiblen Alarm-Adapter umbaut, benötigt Alarmo nicht zwingend. |

## Austauschbare Geräte- und Messadapter

Diese Repositories sind **konkret belegte mögliche Implementierungen**, keine zusätzliche Installationspflicht; ein gleichwertiger Adapter mit dem [beschriebenen Entity-Vertrag](setup.md#externer-entity-vertrag-platzhalter-nicht-aus-paket-erzeugt) genügt.

| Thema | Direktes Repository | Art und Abgrenzung |
|---|---|---|
| Batterie | [EcoFlow Energy](https://github.com/shuette42/ecoflow-energy-ha) | HACS-Custom-Integration `ecoflow_energy`: möglicher signierter Batterie-Leistungssensor in W (+ lädt). Das Sample steuert keinen Speicher und verlangt **nicht** gerade dieses Repo. |
| Wallbox | [Heidelberg Energy Control](https://github.com/Schrolli91/heidelberg_energy_control) | HACS-Custom-Integration `heidelberg_energy_control`: mögliche Zähler-/Status-/Ladefreigabe-Entities. Das Sample setzt einen monotonen kWh-Zähler und einen **Ladeerlaubnis-**, keinen Netztrenn-Schalter voraus. Fahrzeugstatus kann aus einem anderen Adapter kommen. |

Die zwei W600-Climates und Ventilpositionssensoren sind in der geprüften lokalen Zuordnung über **Core-MQTT**, nicht Better Thermostat angebunden. Auch das konkrete Wolf-Heizkreis-`select` wurde dort über **Core-MQTT** bereitgestellt; WolfLink ist nicht automatisch die Quelle dieses Selects. Für diese Verträge ist **kein W600-/Wolf-HACS-Repo vorgeschrieben**. Broker/Gateway oder Gerätebrücken können unabhängig von HACS benötigt werden.

## Optionale Begleiter (nicht vom YAML aufgerufen)

| Thema | Direktes Repository | Art / Grenze |
|---|---|---|
| Heizung | [Climate Group Helper](https://github.com/bjrnptrsn/climate_group_helper) | Optionale HACS-Custom-Integration für gruppierte Climate-Darstellung, kein Ersatz für die neun Einzel-Entities im Shadow. |
| Sicherheit | [X-Sense](https://github.com/Jarnsen/ha-xsense-component_test) | Optionale geräteabhängige HACS-Custom-Integration; keine X-Sense-spezifischen Entitäten im Sample. |
| Sicherheit/UI | [Browser Mod](https://github.com/thomasloven/hass-browser_mod) | Optionale HACS-Custom-Integration für Browser-/Popup-Funktionen; der Beispielcode löst **keinen** Browser-Mod-Popup aus. |
| Energie | [Tibber Graph](https://github.com/stefanes/tibber-graph) | Optionale HACS-Custom-Integration für weitere Tibber-Darstellung; **nicht** die Quelle des hier benötigten Preissensors. Dieser kann über die HA-Core-Tibber-Integration oder einen kompatiblen Preisadapter kommen. |
| Batterie | [EcoFlow Cloud](https://github.com/tolwi/hassio-ecoflow-cloud) | Optionale alternative HACS-Custom-Integration; der beispielhafte Batterie-Leistungspfad verlangt sie nicht zusätzlich zu EcoFlow Energy. Repo-Name `hassio` bedeutet hier **nicht**, dass dieses Sample ein Supervisor-Add-on installiert. |

### Optionale Frontend-Karten (nur Dashboards)

Dies sind **HACS-Frontend-Karten**, keine Geräteintegrationen, Sensor-Adapter oder Voraussetzungen zum Ausführen von `packages/haus.yaml`. Ein Dashboard kann sie unabhängig vom YAML verwenden:

- [Mushroom](https://github.com/piitaya/lovelace-mushroom) – allgemeine UI-Karten.
- [Room Summary Card](https://github.com/homeassistant-extras/room-summary-card) – Raumübersicht.
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) – Zeitreihen, etwa Wärme oder Energie.
- [Solar Card](https://github.com/victorigualada/lovelace-solar-card) – Energievisualisierung.
- [Alarmo Card](https://github.com/nielsfaber/alarmo-card) – Alarmo-Dashboard; unabhängig von der Alarmo-Backend-Integration.

[HACS selbst](https://github.com/hacs/integration) ist ein **optionaler Installationsweg** für Community-Integrationen und Frontend-Karten, keine HA-Core-Funktion, kein Supervisor-Add-on und keine automatisch durch das Sample installierte Abhängigkeit. Installations- und Versionshinweise des jeweiligen Repos beachten.

## Home Assistant Core – offizielle Dokumentation, keine HACS-Repos

- Heizung/Geräte: [WolfLink](https://www.home-assistant.io/integrations/wolflink/) (Wolf SmartSet), [MQTT](https://www.home-assistant.io/integrations/mqtt/) (u. a. W600 und lokal verwendetes Wolf-Select). Ein MQTT-Broker ist ein separater Dienst.
- Preis/Kameras/Anzeige: [Tibber](https://www.home-assistant.io/integrations/tibber/), [Reolink](https://www.home-assistant.io/integrations/reolink/), [Fully Kiosk Browser](https://www.home-assistant.io/integrations/fully_kiosk/). Reolink ist eine mögliche Kamera-Anbindung, nicht die einzig zulässige; Fully Kiosk ist für diesen YAML-Pfad nicht nötig.
- Weitere Core-Schnittstellen: [Kalender](https://www.home-assistant.io/integrations/calendar/), [Person](https://www.home-assistant.io/integrations/person/), [Schloss](https://www.home-assistant.io/integrations/lock/), [Kamera](https://www.home-assistant.io/integrations/camera/), [Template](https://www.home-assistant.io/integrations/template/) und [Integrationssensor](https://www.home-assistant.io/integrations/integration/). Der jeweilige Kalender-/Schloss-/Kamera-Provider ist austauschbar; dieses Sample schreibt keinen bestimmten Kalenderanbieter vor.

**Add-on / externer Dienst:** Weder ein bestimmter Supervisor-Add-on-Katalog noch ein MQTT-Broker oder der optionale authentifizierte Kamera-/AI-Empfänger sind in diesem Repository enthalten oder durch die HACS-Liste belegt. Der mitgelieferte Receiver ist eine lokale CLI zur Eingabeprüfung, **kein** HTTP-/AI-Dienst. Bei Übernahme der Kamera-Finish-POSTs muss ein eigener sicherer Empfänger unabhängig eingerichtet und getestet werden; ohne ihn gibt es keinen vollständigen AI-Ablauf. Siehe [Grenzen](grenzen.md) und [Einrichtung](setup.md).
