# 🏠 Haus-Automationen 2026

> **36 echte Home-Assistant-Automationen aus meinem Smart Home – sortiert, kommentiert und als Community-Samples aufbereitet.**

Hier findest du die Automationen, die wir 2026 gemeinsam aufgebaut und im Alltag erprobt haben: von präsenz- und helligkeitsabhängigem Licht über Nachtmodus, Türklingel/Kameras, Gartenbewässerung und Shield-Displays bis zur EcoFlow-Selbstheilung.

## 🚀 So nutzt du die Samples

1. Gewünschte YAML-Datei öffnen und kopieren.
2. In Home Assistant unter **Einstellungen → Automatisierungen & Szenen → Automatisierung erstellen → In YAML bearbeiten** einfügen – oder als Listeneintrag in `automations.yaml` übernehmen.
3. **Alle** `entity_id`, `area_id`, `device_id`, `browser_id`, Szenen, Notify-Dienste und URLs an dein System anpassen.
4. Benötigte Integrationen/Custom Components aus dem Kommentar und dem YAML-Code prüfen.
5. Konfiguration validieren, Automationen neu laden und zunächst kontrolliert testen.

> [!IMPORTANT]
> Das sind Beispiele aus einem individuellen Smart Home, keine Plug-and-play-Blueprints. Personenbezeichnungen, Geräte-/Config-Entry-IDs, Browser-IDs, die lokale Home-Assistant-Adresse und der private Reolink-Link wurden neutralisiert. Sicherheitskritische Abläufe wie Türschloss, Kameras und Push-Nachrichten bitte besonders sorgfältig testen.

## 📁 Verzeichnis

### [Beleuchtung & Präsenz](./01_beleuchtung_und_praesenz/)

| Automation | Wann? | Was passiert? |
|---|---|---|
| [Ambiente Büro](./01_beleuchtung_und_praesenz/ambiente_buero.yaml) | Statusänderung von binary_sensor.buro_buro_presence_presence_sensor_1_2 auf on; Statusänderung von binary_sensor.buro_buro_presence_presence_sensor_1_2 auf off; illuminance.crossed_threshold bei sensor.buro_buro_presence_light_sensor_light_level_2 | Die Automation führt `scene.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Badezimmer Licht bei Präsenz](./01_beleuchtung_und_praesenz/badezimmer_licht_bei_praesenz.yaml) | Statusänderung von binary_sensor.prasenz_badezimmer_presence auf on; Statusänderung von binary_sensor.prasenz_badezimmer_presence auf off | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Esstisch Schalter toggelt Esstisch unten](./01_beleuchtung_und_praesenz/esstisch_schalter_toggelt_esstisch_unten.yaml) | Geräteereignis (mqtt: action) | Die Automation führt `light.turn_off`, `light.turn_on` aus (mit verzweigten Bedingungen). |
| [Flur Ambiente](./01_beleuchtung_und_praesenz/flur_ambiente.yaml) | Statusänderung von binary_sensor.flur_presence_presence auf on; illuminance.crossed_threshold bei sensor.flur_presence_illuminance; occupancy.detected; Sobald die definierte Template-Bedingung wahr wird | Die Automation führt `scene.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Gäste WC Licht bei Präsenz](./01_beleuchtung_und_praesenz/gaeste_wc_licht_bei_praesenz.yaml) | Statusänderung von binary_sensor.prasenz_gaste_wc_presence auf on; Statusänderung von binary_sensor.prasenz_gaste_wc_presence auf off | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Kellertreppe Licht](./01_beleuchtung_und_praesenz/kellertreppe_licht.yaml) | occupancy.detected bei binary_sensor.motion_kellertreppe_occupancy; occupancy.cleared bei binary_sensor.motion_kellertreppe_occupancy; occupancy.detected; occupancy.cleared | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Küche Arbeitsplatte](./01_beleuchtung_und_praesenz/kueche_arbeitsplatte.yaml) | Geräteereignis (mqtt: action) | Die Automation führt `light.turn_off`, `light.turn_on` aus (mit verzweigten Bedingungen). |
| [Küche Schalter oben Override Küche oben](./01_beleuchtung_und_praesenz/kueche_schalter_oben_override_kueche_oben.yaml) | Geräteereignis (mqtt: action) | Die Automation führt `scene.turn_on`, `input_boolean.turn_off`, `scene.create`, `input_boolean.turn_on`, `light.turn_on` aus (mit verzweigten Bedingungen). |
| [Light Strings Terrasse Automatik](./01_beleuchtung_und_praesenz/light_strings_terrasse_automatik.yaml) | Sonne: sunset; Statusänderung von input_boolean.nachtmodus auf on | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Schlafzimmer Abends](./01_beleuchtung_und_praesenz/schlafzimmer_abends.yaml) | Statusänderung von binary_sensor.schlafzimmer_presence_presence auf on; Statusänderung von binary_sensor.schlafzimmer_presence_presence auf off; illuminance.crossed_threshold bei sensor.schlafzimmer_presence_illuminance | Die Automation führt `scene.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Ventilator WZ Switch Fix](./01_beleuchtung_und_praesenz/ventilator_wz_switch_fix.yaml) | Statusänderung von switch.nebelventilator_power auf off | Die Automation führt `switch.turn_on`, `fan.turn_off` aus (mit Warte-/Verzögerungsschritten). |
| [Wohnzimmmer Ambiente Abends](./01_beleuchtung_und_praesenz/wohnzimmmer_ambiente_abends.yaml) | Statusänderung von binary_sensor.wz_presence_gruppe auf on; Statusänderung von binary_sensor.wz_presence_gruppe auf off für 00:05:00; illuminance.crossed_threshold bei sensor.lichtstarke_wohnzimmer; illuminance.crossed_threshold bei sensor.lichtstarke_wohnzimmer | Die Automation führt `scene.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |

### [Nachtmodus & Familie](./02_nachtmodus_und_familie/)

| Automation | Wann? | Was passiert? |
|---|---|---|
| [Gute Nacht Kind 1](./02_nachtmodus_und_familie/gute_nacht_kind_1.yaml) | Statusänderung von input_boolean.gute_nacht_kind_1 auf on; Statusänderung von input_boolean.gute_nacht_kind_1 auf off | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen). |
| [Gute Nacht Kind 2](./02_nachtmodus_und_familie/gute_nacht_kind_2.yaml) | Statusänderung von input_boolean.gute_nacht_kind_2 auf on; Statusänderung von input_boolean.gute_nacht_kind_2 auf off | Die Automation führt `input_boolean.turn_off`, `light.turn_off`, `light.turn_on` aus (mit verzweigten Bedingungen). |
| [Kind 2 Deckenlicht Präsenz](./02_nachtmodus_und_familie/kind_2_deckenlicht_praesenz.yaml) | Statusänderung von binary_sensor.praesenz_kind_2_presence auf on; Zahlenwert von sensor.praesenz_kind_2_illuminance unter 40; Statusänderung von binary_sensor.praesenz_kind_2_presence auf off; Statusänderung von input_boolean.gute_nacht_kind_2 auf off; Home Assistant: start | Die Automation führt `input_boolean.turn_off`, `light.turn_off`, `light.turn_on` aus (mit verzweigten Bedingungen). |
| [Kind 2 Lichtschalter Down Gute Nacht](./02_nachtmodus_und_familie/kind_2_lichtschalter_down_gute_nacht.yaml) | Geräteereignis (mqtt: action) | Die Automation führt `input_boolean.toggle` aus. |
| [Kind 2 Lichtschalter Up Deckenlicht Override](./02_nachtmodus_und_familie/kind_2_lichtschalter_up_deckenlicht_override.yaml) | Geräteereignis (mqtt: action) | Die Automation führt `input_boolean.turn_off`, `light.turn_off`, `light.turn_on`, `scene.turn_on`, `scene.create`, `input_boolean.turn_on` aus (mit verzweigten Bedingungen, mit Warte-/Verzögerungsschritten). |
| [Küche oben Nacht-/Kinderlogik](./02_nachtmodus_und_familie/kueche_oben_nacht_kinderlogik.yaml) | Statusänderung von binary_sensor.kuche_presence_presence auf on; Statusänderung von binary_sensor.kuche_presence_presence auf off; illuminance.crossed_threshold bei sensor.kuche_presence_illuminance; Statusänderung von input_boolean.nachtmodus, input_boolean.gute_nacht_kind_1, input_boolean.gute_nacht_kind_2; Home Assistant: start | Die Automation führt `input_boolean.turn_off`, `light.turn_off`, `light.turn_on` aus (mit verzweigten Bedingungen). |
| [Nachtmodus Schlafzimmer](./02_nachtmodus_und_familie/nachtmodus_schlafzimmer.yaml) | Statusänderung von input_boolean.nachtmodus auf on | Die Automation führt `input_boolean.turn_on`, `scene.turn_on`, `light.turn_off`, `input_boolean.turn_off` aus (mit Warte-/Verzögerungsschritten). |

### [Sicherheit, Kameras & Zutritt](./03_sicherheit_kameras_und_zutritt/)

| Automation | Wann? | Was passiert? |
|---|---|---|
| [Flur Cam auf Tablet bei Bewegung](./03_sicherheit_kameras_und_zutritt/flur_cam_auf_tablet_bei_bewegung.yaml) | Statusänderung von binary_sensor.motion_flur_oben_occupancy auf on; Statusänderung von binary_sensor.motion_flur_oben_occupancy auf off | Die Automation führt `fully_kiosk.load_url` aus (mit verzweigten Bedingungen). |
| [Garage Flutlicht bei Person an Haustür](./03_sicherheit_kameras_und_zutritt/garage_flutlicht_bei_person_an_haustuer.yaml) | Statusänderung von binary_sensor.front_door_person_2, binary_sensor.front_door_verweilen_area_1_person_2 auf on; Statusänderung von binary_sensor.front_door_person_2, binary_sensor.front_door_verweilen_area_1_person_2 auf off für 00:01:00 | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen, mit Warte-/Verzögerungsschritten). |
| [Kamera-Aufnahme nach Nachtmodus und Anwesenheit](./03_sicherheit_kameras_und_zutritt/kamera_aufnahme_nach_nachtmodus_und_anwesenheit.yaml) | Statusänderung von input_boolean.nachtmodus, person.person_1, person.person_2; Statusänderung von lock.flur_eg_haustur_lock auf locked, unlocked; Home Assistant: start; Statusänderung von switch.zion_nvr_aufzeichnen auf off | Die Automation führt `switch.turn_on`, `switch.turn_off` aus (mit verzweigten Bedingungen). |
| [Schloss verriegeln](./03_sicherheit_kameras_und_zutritt/schloss_verriegeln.yaml) | Statusänderung von input_boolean.nachtmodus auf on; Statusänderung von person.person_1 auf not_home; Statusänderung von person.person_2 auf not_home | Die Automation führt `lock.lock` aus (mit verzweigten Bedingungen). |
| [Spots Eingang Aus vor Sonnenaufgang](./03_sicherheit_kameras_und_zutritt/spots_eingang_aus_vor_sonnenaufgang.yaml) | Sonne: sunrise mit Offset -00:30:00 | Die Automation führt `light.turn_off` aus. |
| [Spots Eingang Automatik](./03_sicherheit_kameras_und_zutritt/spots_eingang_automatik.yaml) | Sonne: sunset mit Offset 00:00:00; Statusänderung von input_boolean.nachtmodus auf on; Statusänderung von binary_sensor.front_door_person_2, binary_sensor.front_door_verweilen_area_1_person_2 auf on; Statusänderung von binary_sensor.front_door_person_2, binary_sensor.front_door_verweilen_area_1_person_2 auf off für 00:01:00 | Die Automation führt `light.turn_on`, `light.turn_off` aus (mit verzweigten Bedingungen, mit Warte-/Verzögerungsschritten). |
| [Terrasse Flutlicht bei Nacht](./03_sicherheit_kameras_und_zutritt/terrasse_flutlicht_bei_nacht.yaml) | Statusänderung von input_boolean.nachtmodus; Statusänderung von media_player.wohnzimmer_tv_wohnzimmer_homekit; Statusänderung von person.person_1; Statusänderung von person.person_2 | Die Automation führt `select.select_option` aus (mit verzweigten Bedingungen). |
| [Türklingel Benachrichtigung](./03_sicherheit_kameras_und_zutritt/tuerklingel_benachrichtigung.yaml) | Statusänderung von binary_sensor.flur_eg_front_door_besucher auf on | Die Automation führt `notify.mobile_app_dein_iphone` aus. |
| [Türklingel Fully Kiosk](./03_sicherheit_kameras_und_zutritt/tuerklingel_fully_kiosk.yaml) | Statusänderung von binary_sensor.front_door_verweilen_area_1_person_2, binary_sensor.front_door_besucher_2 auf on | Die Automation führt `camera.play_stream`, `media_player.play_media`, `media_player.media_stop`, `fully_kiosk.load_url`, `browser_mod.navigate` aus (mit verzweigten Bedingungen, mit Warte-/Verzögerungsschritten). |

### [Garten & Wetter](./04_garten_und_wetter/)

| Automation | Wann? | Was passiert? |
|---|---|---|
| [Bewässerung Wiese](./04_garten_und_wetter/bewaesserung_wiese.yaml) | Täglich um 05:00:00 | Die Automation führt `select.select_option`, `button.press` aus (mit Warte-/Verzögerungsschritten). |
| [Bewässerung Zypressen](./04_garten_und_wetter/bewaesserung_zypressen.yaml) | Täglich um 05:00:00 | Die Automation führt `select.select_option`, `button.press` aus (mit Warte-/Verzögerungsschritten). |
| [Hitzetage Zähler](./04_garten_und_wetter/hitzetage_zaehler.yaml) | Täglich um 23:59:00 | Die Automation führt `input_number.increment`, `input_number.set_value` aus (mit verzweigten Bedingungen). |

### [Medien & Displays](./05_medien_und_displays/)

| Automation | Wann? | Was passiert? |
|---|---|---|
| [Shield Büro bei Präsenz](./05_medien_und_displays/shield_buero_bei_praesenz.yaml) | Statusänderung von binary_sensor.buro_buro_presence_presence_sensor_1_2 auf on; Statusänderung von binary_sensor.buro_buro_presence_presence_sensor_1_2 auf off für 00:10:00 | Die Automation führt `media_player.turn_on`, `media_player.play_media`, `androidtv.adb_command`, `media_player.turn_off` aus (mit verzweigten Bedingungen, mit Warte-/Verzögerungsschritten, mit Wiederholungslogik). |
| [Shield Büro echten Start erfassen](./05_medien_und_displays/shield_buero_echten_start_erfassen.yaml) | Statusänderung von media_player.buro_promo_screen_buro von off auf idle | Die Automation führt `input_datetime.set_datetime` aus. |
| [Shield Büro Kamin-Watchdog](./05_medien_und_displays/shield_buero_kamin_watchdog.yaml) | Zeitmuster minutes=/1 | Die Automation führt `media_player.play_media` aus. |

### [Energie, Raumklima & Geräte](./06_energie_klima_und_geraete/)

| Automation | Wann? | Was passiert? |
|---|---|---|
| [EcoFlow Cloud Selbstheilung](./06_energie_klima_und_geraete/ecoflow_cloud_selbstheilung.yaml) | Statusänderung von binary_sensor.ecoflow_daten_stale auf on | Die Automation führt `homeassistant.reload_config_entry`, `input_datetime.set_datetime` aus. |
| [Luftentfeuchter durch Raumwerte Regeln](./06_energie_klima_und_geraete/luftentfeuchter_durch_raumwerte_regeln.yaml) | humidity.crossed_threshold bei sensor.temperatur_buro_luftfeuchtigkeit; humidity.crossed_threshold bei sensor.temperatur_buro_luftfeuchtigkeit | Die Automation führt `humidifier.turn_on`, `humidifier.turn_off` aus (mit verzweigten Bedingungen). |

## 🧩 Typische Abhängigkeiten

- Home-Assistant-Core-Domains wie `light`, `scene`, `lock`, `camera`, `media_player`, `humidifier`, `select` und diverse Helper (`input_boolean`, `input_datetime`, `input_number`).
- Je nach Sample: Reolink, Fully Kiosk Browser, Browser Mod, Android TV/ADB, Google Cast, EcoFlow sowie gerätespezifische Trigger.
- Die verwendeten Szenen und Helper sind nicht Bestandteil dieses Ordners und müssen passend zum eigenen Setup angelegt werden.
- Trigger vom Typ `illuminance.crossed_threshold` bzw. `occupancy.*` setzen die entsprechenden Home-Assistant-Funktionen/Integrationen voraus; bei Bedarf durch normale State-/Numeric-State-Trigger ersetzen.

## 🚫 Bewusst nicht enthalten

Wie angekündigt sind folgende große Systeme aus dieser Sammlung ausgeschlossen:

- Reminder Engine
- Saugroboter-/Saugplanungs-Automationen
- Heizungsautomationen (Wolf / Better Thermostat)

## 🔒 Datenschutz & Sicherheit

- Keine Tokens, Passwörter oder Secrets veröffentlichen.
- Geräte-/Config-Entry- und Browser-IDs stehen als `REPLACE_WITH_...`-Platzhalter im YAML.
- Personenbezeichnungen sind als `person.person_1`, `person.person_2`, `Kind 1` und `Kind 2` abstrahiert.
- Die lokale Adresse wurde auf `http://homeassistant.local:8123` vereinheitlicht.
- Personen-, Raum- und Entity-Namen zeigen die Logik und müssen vor Nutzung an dein Zuhause angepasst werden.

## 💙 Community

Du hast eine Automation verbessert oder auf andere Geräte portiert? Forke das Repo und schick gern einen Pull Request. Viel Spaß beim Nachbauen! 🚀

— **T-Flow / TheT_Flow**
