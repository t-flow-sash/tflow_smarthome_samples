# 🚀 Migration: Zigbee2MQTT (Docker) zu Home Assistant Add-on mit SMLIGHT SLZB-06U (WLAN/LAN-Modus)

Diese Kurzanleitung beschreibt den Umzug einer bestehenden **Zigbee2MQTT (Z2M)** Instanz aus einem eigenständigen Docker-Container in das offizielle **Home Assistant Z2M Add-on**, kombiniert mit dem Wechsel auf den **SMLIGHT SLZB-06U** Koordinator im Netzwerkbetrieb.

---

## 📋 Voraussetzungen & Vorbereitung

1. **Antenne anbringen:** Den SLZB-06U *niemals* ohne Antenne betreiben!
2. **IP-Adresse sichern:** Den Stick initial per USB/Strom versorgen, im Router die IP-Adresse auslesen (z. B. über den Hostnamen `http://slzb-06u.local`) und im Router eine **feste IP-Zuweisung** aktivieren.
3. **Backup erstellen:** Den kompletten `data`-Ordner der alten Docker-Instanz sichern (wichtig: `configuration.yaml`, `database.db`, `state.json`).

---

## 🛠️ Schritt-für-Schritt Installationsanleitung

### 1. IEEE-Adresse klonen (Verhindert neues Koppeln)
* Rufe das Webinterface des SLZB-06U auf (`http://<DEINE-STICK-IP>`).
* Navigiere zu den **System / Zigbee Einstellungen** zum Bereich **"Adapter IEEE address change"**.
* Trage bei **"Flash custom IEEE address"** die originale IEEE-Adresse deines *alten* Zigbee-Sticks ein (Format: `0x...`).
* Speichern und den Stick über das Webinterface neu starten.

### 2. Altes System stoppen
* Stoppe den alten Zigbee2MQTT Docker-Container komplett. (Es darf kein zweiter Koordinator mit derselben IEEE-Adresse funken!).
* *Tipp:* Schalte strombetriebene Zigbee-Geräte (z.B. Leuchtmittel) einmal kurz für 15 Sekunden stromlos, um die Suche nach dem "neuen" Koordinator zu erzwingen.

### 3. Daten in Home Assistant importieren
* Installiere das offizielle **Zigbee2MQTT Add-on** in Home Assistant (noch **nicht** starten!).
* Kopiere alle gesicherten Dateien aus dem alten Docker-`data`-Ordner in das Z2M-Verzeichnis von Home Assistant (üblicherweise `/config/zigbee2mqtt/` oder `/share/zigbee2mqtt/`).

### 4. Konfiguration anpassen (WICHTIG!)
Ändere die Konfiguration **ausschließlich direkt in der `configuration.yaml`** (im Add-on oben rechts auf die drei Punkte -> *In YAML bearbeiten* klicken). Die GUI-Felder und die YAML-Datei können sich sonst gegenseitig blockieren!

Nutze exakt folgende Struktur für den SMLIGHT SLZB-06U im Netzwerkmodus:

```yaml
serial:
  port: tcp://<DEINE-STICK-IP>:6638
  baudrate: 115200
  adapter: zstack
  disable_led: false

advanced:
  transmit_power: 20

```

⚠️ **Achtung beim U-Modell:** Der SLZB-06U tunnelt die Daten im Netzwerkbetrieb so, dass er für Z2M als Texas Instruments Chip sichtbar wird. Daher muss zwingend **`port: ...:6638`** und **`adapter: zstack`** eingetragen werden!

### 5. Start & Überprüfung

* Starte das Zigbee2MQTT Add-on in Home Assistant.
* Öffne das Add-on-Protokoll (Log). Die Verbindung sollte sofort fehlerfrei aufgebaut werden.
* **Geduld haben:** Batteriebetriebene Sensoren wachen nach und nach von alleine auf oder können durch einen kurzen Tastendruck am Gerät aufgeweckt werden. Die Gerätenamen und Automationen bleiben komplett erhalten!
