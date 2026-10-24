"""Canonical German explanations for the generated, separately copyable views.

Descriptions are intentionally kept next to the exporter, not in the 60 YAML
leaves. Missing production components fail the build instead of getting filler.
"""

NOTES = {
    ('automation', 'wolf_shadow'): ('Berechnet Heizbedarf aus gewichteten Raumwerten und setzt den reinen Shadow-Merker.', 'Macht den Wärmebedarf sichtbar, ohne einen Wolf-Aktor zu schalten.', 'Bei stabiler Start-/Komfortanforderung, Haltesignal, HA-Start oder Automation-Reload; Rücknahme erst nach fünf Minuten ohne Bedarf.', 'Shadow-Templates, input_boolean.demo_shadow; externe Better-Thermostat- und W600-Raumwerte.', 'Raumgewichte, Gültigkeitsgrenzen und Schwellwerte an die Anlage anpassen.', 'Kein direkter Kesselbefehl; Shadow ist nur ein Bedarfssignal.'),
    ('automation', 'kalender_abwesenheit'): ('Schaltet BT-Räume bei markierten Abwesenheitsfenstern auf eco und den Wolf-DHK-Select optional auf Standby.', 'Markiert BT-eco und Wolf-Standby nach Readback; versucht bei Abwesenheitsende die Rücknahme bei gesetztem Ownership-Merker.', 'Um 08:00/15:00, alle 15 Minuten, bei Kalenderänderung/-start/-ende sowie HA-Start/Reload; ganztägiges Ende ist exklusiv.', 'calendar.beispiel_abwesenheit mit calendar.get_events, BT-Räume, select.beispiel_wolf_dhk, getrennte BT-/Wolf-Freigaben sowie Kalender-/Wolf-Ownership und input_text.demo_kalender_wolf_vorher.', 'Kalender-Markierung [Heizung], Raum-IDs, Select-Optionen und lokale Zeitzone prüfen.', 'Ungültige Kalenderantwort bewirkt keinen Aktorwechsel; BT-Rücknahme setzt ohne erneuten Preset-Vergleich none für alle neun Räume und kann manuelle Änderungen überschreiben; Wolf-Standby ist kein Warmwasser-Eingriff.'),
    ('automation', 'aufnahme_bei_abwesenheit'): ('Gleicht sechs Aufnahme-Schalter mit Nacht- oder bestätigter Abwesenheit ab.', 'Lässt nur selbst beanspruchte Aufnahme-Schalter beim Widerruf wieder los.', 'Bei Personen-/Nacht-/Freigabewechsel, HA-Start und Reload.', 'person.beispiel_a/b, input_boolean.demo_nacht, demo_sicherheit_freigabe, sechs switch.beispiel_zone_XX_aufnahme und zugehörige Ownership-Helper.', 'Zonen, Person-IDs und Aufnahme-Entity-IDs den eigenen Integrationen zuordnen.', 'Unbekannte Präsenz gilt nicht als Abwesenheit; Ownership-Markierung und physischer Switch-Befehl sind nicht atomar.'),
    ('automation', 'schloss_abwesenheit'): ('Ruft das Abschließ-Skript nur bei gesicherter Abwesenheit auf.', 'Vermeidet einen Schlossbefehl bei unklarer Anwesenheit.', 'Bei Zustandswechsel einer der beiden Personen.', 'person.beispiel_a/b, input_boolean.demo_sicherheit_freigabe und script.demo_abschliessen.', 'Personen und Schloss-Skript der Testanlage zuordnen.', 'Nur abschließen, niemals automatisch aufschließen; vor echtem Schlossbetrieb Türkontakt/Readback prüfen.'),
    ('automation', 'alarm_meldung'): ('Erzeugt eine lokale Meldung bei Alarmo-Status triggered.', 'Macht ausgelöste Alarme sichtbar, ohne Alarmo zu schalten.', 'Beim Zustandswechsel von alarm_control_panel.beispiel_alarmo auf triggered.', 'Extern installierte Alarmo-Integration samt UI-Sensorzuordnung und persistent_notification.', 'Alarmo-Entity und Meldetext anpassen.', 'Keine Scharf-/Unscharfschaltung und keine garantierte externe Alarmübermittlung.'),
    ('automation', 'eingang_licht'): ('Schaltet das Eingangslicht nach Bewegung für drei Minuten ein.', 'Beleuchtet den Eingangsbereich zeitlich begrenzt.', 'Wenn binary_sensor.beispiel_eingang_bewegung auf on wechselt.', 'Bewegungssensor, light.beispiel_eingang und input_boolean.demo_sicherheit_freigabe.', 'Sensor, Licht und Nachlaufzeit anpassen.', 'Vor Live-Einsatz konkurrierende Lichtautomationen und manuellen Override prüfen.'),
    ('automation', 'display_klingel'): ('Aktiviert Display-Licht und lokale Klingelmeldung für eine Minute.', 'Signalisiert einen Klingeldruck ohne Kamera-Livebildzwang.', 'Wenn binary_sensor.beispiel_klingel auf on wechselt.', 'Klingelsensor, light.beispiel_display, persistent_notification und Sicherheitsfreigabe.', 'Klingel- und Display-Entities sowie Leuchtdauer anpassen.', 'Keine gesicherte Fernbenachrichtigung oder Kamerafreigabe.'),
    ('automation', 'kamera_retention'): ('Ruft die lokale Kamera-Medienpflege auf.', 'Begrenzt Bildalter und Speicherbedarf im Beispiel.', 'Täglich um 03:20.', 'shell_command.demo_camera_maintain und installiertes scripts/camera_media.py unter /config/demo_camera_media.py.', 'Lokale Pfade, Aufbewahrung und Dateirechte vor Aktivierung prüfen.', 'Best-Effort-Retention; HA-/media-Bilder können für weitere authentifizierte Nutzer sichtbar sein.'),
    ('automation', 'wallbox_freigabe'): ('Setzt ausschließlich die Ladeerlaubnis der Wallbox.', 'Erlaubt Laden bei Anschluss, Präsenz und günstigem Tarif; laufendes Laden darf bei Preiswechsel fortgesetzt werden.', 'Bei Freigabe-, Stecker-, Tarif-, Lade- und Personenstatus, alle fünf Minuten und beim HA-Start.', 'input_boolean.demo_laden_freigabe, binary_sensor.demo_preis_guenstig, externer Stecker-/Ladestatus, Personen und switch.beispiel_wallbox_freigabe.', 'Wallbox-Switch, Personen, Anschluss und Tarifadapter ersetzen.', 'Freigabe-/Präsenz-Widerruf schaltet aus; Preis-Hysterese ist keine Erlaubnis ohne Zustimmung; keine Netztrennung.'),
    ('automation', 'ladekosten'): ('Verbucht gemessene Ladedifferenzen mit dem zuletzt gespeicherten Tarif.', 'Stellt Sitzungsenergie, Beispielkosten und letzten Abschluss dar; beim Preiswechsel gilt der zuvor gespeicherte Preis für die seit dem letzten Zählerstand gemessene Differenz.', 'Bei Zähler-/Preis-/Ladestatuswechsel, minütlich und bei HA-Start.', 'sensor.beispiel_wallbox_kwh, sensor.beispiel_tibber_eur_kwh, sensor.beispiel_ladestatus, input_boolean.demo_ladesitzung und Lade-/Letzte-Helper.', 'Zähler in kWh, Preis in EUR/kWh, Statuswort charging und Zeitgrenze prüfen.', 'Ungültige Werte oder Zählerrücksprung stoppen die Verbuchung; demo_lade_zaehler_gueltig ist kein aktives Gate; keine eichrechtskonforme Abrechnung.'),
    ('script', 'demo_abschliessen'): ('Schließt das Eingangsschloss erst nach Freigabe, Abwesenheit und geschlossenem Türkontakt.', 'Erlaubt der Abwesenheitsautomation eine kontrollierte Verriegelung mit Readback.', '', 'input_boolean.demo_sicherheit_freigabe, person.beispiel_a/b, binary_sensor.beispiel_tuer_offen und lock.beispiel_eingang.', 'Schloss, Türkontakt und Personen durch verifizierte Test-Entities ersetzen.', 'Nie entriegeln; unbekannte Präsenz/Türzustände sperren den Befehl.'),
    ('shell_command', 'demo_camera_maintain'): ('Startet den lokalen Medienhelfer mit maintain.', 'Bereinigt alte Kameraaufnahmen nach lokalem Aufbewahrungsvertrag.', '', 'scripts/camera_media.py muss als /config/demo_camera_media.py installiert sein; /media/demo_camera vorbereiten.', 'Interpreterpfad, Rechte und Retention vor Aktivierung prüfen.', 'Kein garantierter Löschzeitpunkt; keinen fremdbeschreibbaren Skriptpfad verwenden.'),
    ('rest_command', 'demo_camera_finished'): ('Sendet einen Kamera-Episodenabschluss als JSON an den externen Empfänger.', 'Übergibt Episode, Ende, Grund und Bildanzahl für eine mögliche nachgelagerte Verarbeitung.', '', 'Externes authentifiziertes HTTPS-Gateway; !secret demo_camera_webhook_url und demo_camera_webhook_token.', 'Nur eigene HTTPS-URL und Token in nicht versionierter secrets.yaml setzen; Empfängervertrag prüfen.', 'Kein mitgelieferter AI-/Netzwerkdienst, keine dauerhafte Zustellgarantie; Bildzugriff separat absichern.'),
}

# Helper functions share installation shape, but purpose and prerequisites remain specific.
HELPERS = {
    'demo_bt_freigabe': ('Erlaubt der Kalenderautomation Änderungen an Better-Thermostat-Presets.', 'Hält Kalendersteuerung der BT-Räume zunächst ausgeschaltet.', 'automation.kalender_abwesenheit und neun externe climate.beispiel_bt_XX.', 'Nur nach geprüftem eco/none-Readback einschalten.'),
    'demo_wolf_freigabe': ('Erlaubt ausschließlich den Wolf-Select-Zweig der Kalenderautomation.', 'Trennt Kesselzustimmung von der BT-Raumfreigabe.', 'automation.kalender_abwesenheit und select.beispiel_wolf_dhk.', 'Nur nach Auto/Standby-Readback einschalten; kein Warmwasser-Select.'),
    'demo_sicherheit_freigabe': ('Erlaubt Sicherheits-, Kamera-, Schloss- und Lichtaktionen.', 'Startet alle physischen Sicherheitspfade standardmäßig gesperrt.', 'Sicherheitsautomationen, script.demo_abschliessen, Kamera-/Schloss-/Licht-Adapter.', 'Vor Aktivierung alle Aktoren und Widerrufspfade isoliert testen.'),
    'demo_laden_freigabe': ('Erlaubt die Wallbox-Steuerung durch die Freigabeautomation.', 'Entzieht Ladeerlaubnis ausdrücklich bei Widerruf.', 'automation.wallbox_freigabe und switch.beispiel_wallbox_freigabe.', 'Nur nach Prüfung der Wallbox-Freigabe-Semantik aktivieren; kein Netzschalter.'),
    'demo_kalender_ownership': ('Merkt, dass nach einem eco-Schreibversuch alle neun BT-Presets als eco zurückgelesen wurden.', 'Dient der Kalenderautomation als Marker für die spätere Rücknahme auf none, nicht als Nachweis dauerhafter exklusiver Kontrolle.', 'automation.kalender_abwesenheit und BT-Preset-Readback.', 'Nach Neustart Ownership mit realem Raumzustand abgleichen; keine Prüfung zwischenzeitlicher manueller Preset-Änderungen vor der Rücknahme.'),
    'demo_wolf_ownership': ('Merkt den nach eigenem Select-Schreibversuch zurückgelesenen Wolf-Standby-Wechsel.', 'Markiert eine mögliche Rücknahme auf Auto bei Abwesenheitsende, wenn die zuvor gelesene Option Auto war.', 'automation.kalender_abwesenheit und select.beispiel_wolf_dhk.', 'Nach Neustart Ownership/Readback vor Auto-Rücknahme prüfen; keine Erkennung fremder Änderungen zwischen zwei Readbacks.'),
    'demo_shadow': ('Speichert das verzögerte Heizbedarfs-Schattenbit.', 'Zeigt Raum-Anforderung ohne Aktor-Schaltung an.', 'automation.wolf_shadow und Shadow-Start-/Komfort-/Halten-Templates.', 'Nicht als ungeprüften Kessel-Schaltbefehl verwenden.'),
    'demo_nacht': ('Signalisiert der Aufnahmeautomation einen Nachtbedarf.', 'Erlaubt Aufzeichnung unabhängig von bestätigter Abwesenheit.', 'automation.aufnahme_bei_abwesenheit, Sicherheitsfreigabe und sechs Aufnahme-Adapter.', 'Nachtstatus und Datenschutzregeln vor Aufzeichnungsfreigabe prüfen.'),
    'demo_ladesitzung': ('Merkt eine laufende Wallbox-Abrechnungssitzung.', 'Ermöglicht Abschluss erst nach stabilem Ladeende.', 'automation.ladekosten und Lade-/Zähler-/Preis-Helper.', 'Nach Neustart mit tatsächlichem Ladestatus und Zähler abgleichen.'),
    'demo_lade_zaehler_gueltig': ('Reserviert einen unbenutzten Gültigkeitsmerker für den Ladezähler.', 'Macht eine mögliche spätere Zählerprüfung sichtbar; im Beispiel keine aktive Sperre der Kostenverbuchung.', 'Zähleradapter sensor.beispiel_wallbox_kwh; im Beispiel nicht als aktiver Kosten-Gate verwendet.', 'Nicht als bereits wirksame Sperre behaupten; Zählerqualität separat prüfen.'),
}
for zone in range(1, 7):
    z = f'zone_{zone:02}'
    NOTES[('automation', f'kamera_{z}')] = (
        f'Erstellt begrenzte Snapshots bei Personen-/Tiererkennung in {z}.',
        f'Sammelt pro Episode Bilder aus {z} und meldet deren Ende an den Beispiel-Empfänger.',
        f'Bei Erkennungsbeginn, demo_camera_continue, HA-Start und Reload; {"Akku-Kamera wartet zunächst auf Readiness" if zone >= 4 else "kabelgebundene Beispielzone ohne Akku-Wartezeit"}.',
        f'camera.beispiel_{z}, binary_sensor.beispiel_{z}_person/tier, switch.beispiel_{z}_aufnahme, input_boolean.demo_sicherheit_freigabe, rest_command.demo_camera_finished und /media/demo_camera/{z}.',
        f'Kamera-, Erkennungs- und Aufnahme-IDs von {z} sowie Medienpfad/Empfänger anpassen.',
        'Freigabe und Aufnahme vor jedem Bild prüfen; maximal 100 Frames pro Durchlauf, Best-Effort-Fortsetzung/POST ohne dauerhafte Outbox; /media-Sichtbarkeit beachten.')
    NOTES[('input_boolean', f'demo_aufnahme_ownership_{z}')] = (
        f'Merkt ausschließlich die von der Abwesenheitsautomation beanspruchte Aufnahme in {z}.',
        f'Vermeidet das Abschalten von bereits bei Start eingeschalteten Aufnahmen in {z}, wenn der Marker aus ist.', '',
        f'automation.aufnahme_bei_abwesenheit und switch.beispiel_{z}_aufnahme.',
        f'Ownership-Zuordnung für Kamera {z} nach Neustart prüfen.',
        'Keine sichere Erkennung manueller Änderungen nach der Übernahme; nicht selbst als Zustimmung zur Aufzeichnung verwenden.')

for key, (purpose, benefit, deps, adjust) in HELPERS.items():
    NOTES[('input_boolean', key)] = (purpose, benefit, '', deps, adjust,
        'Freigaben mit initial: false starten aus; Ownership-/Zustandsmerker ohne initial können nach Neustart wiederhergestellt werden.')

NUMBERS = {
    'demo_lade_zaehler': ('letzten verbuchten Wallbox-Zählerstand', 'sensor.beispiel_wallbox_kwh', 'kWh-Zählereinheit und Rücksprünge'),
    'demo_lade_kosten': ('aufgelaufene Sitzungskosten', 'automation.ladekosten und input_number.demo_lade_preis', 'EUR-Betragsbereich und Rundung'),
    'demo_lade_energie': ('aufgelaufene Sitzungsenergie', 'automation.ladekosten und Wallbox-kWh-Zähler', 'kWh-Bereich und Zählerauflösung'),
    'demo_letzte_energie': ('Energie der abgeschlossenen Ladesitzung', 'automation.ladekosten und input_number.demo_lade_energie', 'kWh-Darstellung'),
    'demo_letzte_kosten': ('Kosten der abgeschlossenen Ladesitzung', 'automation.ladekosten und input_number.demo_lade_kosten', 'EUR-Darstellung'),
}
for key, (measurement, deps, adjust) in NUMBERS.items():
    NOTES[('input_number', key)] = (f'Speichert {measurement}.', f'Erhält {measurement} über Reloads als HA-Helper.', '', deps,
                                      f'{adjust} für den eigenen Adapter prüfen.', 'Beispielrechnung, keine eichrechtskonforme Abrechnung; ungültige Messwerte nicht fortschreiben.')

NOTES[('input_number', 'demo_lade_preis')] = (
    'Speichert den aktuell im Helper hinterlegten Tarif für künftige Verbrauchsdifferenzen.',
    'Beim Preiswechsel wird die seit dem letzten Zählerstand entstandene Differenz zunächst mit dem bisher gespeicherten Preis verbucht; erst danach speichert die Automation den neuen Tarif für folgende Deltas.',
    '', 'automation.ladekosten und sensor.beispiel_tibber_eur_kwh',
    'EUR/kWh statt Cent/kWh für den eigenen Adapter prüfen.',
    'Beispielrechnung: Der gespeicherte Tarif gilt für die nächste gemessene Differenz, nicht als Nachweis des exakten Tarifverlaufs innerhalb eines Messintervalls.')

NOTES[('input_text', 'demo_kalender_wolf_vorher')] = ('Bewahrt die vor dem Kalender-Wechsel gelesene Wolf-Option.', 'Erlaubt den Versuch, bei gesetzter Ownership von Standby auf das zuvor gelesene Auto zurückzustellen.', '', 'automation.kalender_abwesenheit, select.beispiel_wolf_dhk und input_boolean.demo_wolf_ownership.', 'Optionstext Auto/Standby am echten Select prüfen.', 'Keine Herkunftserkennung für zwischenzeitlich erneut gesetztes Standby; vor der Rücknahme auf Auto nur aktueller Optionswert und Marker geprüft.')
NOTES[('input_text', 'demo_wolf_ziel')] = ('Reserviert Text für ein mögliches Wolf-Ziel.', 'Dokumentiert einen Erweiterungspunkt; keine Automation nutzt ihn im Beispiel.', '', 'Keine aktive Laufzeitabhängigkeit; Wolf-Adapter nur bei eigener Erweiterung.', 'Vor zusätzlicher Nutzung erlaubte Optionen und Ownership definieren.', 'Nicht als bereits wirksame Kesselsteuerung ausgeben.')

for zone in range(1, 3):
    z = f'{zone:02}'
    base = f'Demo W600 {z}'
    deps = f'climate.beispiel_w600_{z}, sensor.beispiel_w600_{z}_ventil'
    for suffix, purpose, benefit, extra, caveat in [
        ('gueltig', 'Prüft Temperatur, Ventilstellung und frische W600-Telemetrie.', 'Schließt unbekannte, veraltete oder unplausible Raumwerte aus.', deps, 'Messdaten älter als sechs Stunden gelten als ungültig.'),
        ('start', 'Erkennt aktives Heizen mit mindestens 0,3 °C Defizit und Ventilöffnung über 70 %.', 'Liefert eine belastbare Startanforderung für den Shadow.', deps + f', binary_sensor.demo_w600_{z}_gueltig', 'Ungültige W600-Werte dürfen keinen Start auslösen.'),
        ('halten', 'Erkennt Heizen mit Ventilöffnung ab 30 %.', 'Hält bestehenden Shadow-Bedarf, ohne ständig neu zu starten.', deps + f', binary_sensor.demo_w600_{z}_gueltig', 'Nur gültige Messwerte dürfen den Bedarf halten.')]:
        NOTES[('template', f'{base} {suffix}')] = (f'{purpose} (W600 {z})', benefit, '', extra, f'W600 {z}: Raum- und Ventil-Entity sowie Grenzwerte prüfen.', caveat)

for suffix, measure, entity in [('Punkte', 'gewichtete Startpunkte', 'sensor.demo_shadow_punkte'), ('Ungueltig', 'Anzahl unbrauchbarer Räume', 'sensor.demo_shadow_ungueltig'), ('Defizit', 'größtes Temperaturdefizit', 'sensor.demo_shadow_defizit'), ('Halten', 'laufenden Heizbedarf', 'binary_sensor.demo_shadow_halten')]:
    NOTES[('template', f'Demo Shadow {suffix}')] = (f'Ermittelt {measure} aus neun BT- und zwei W600-Räumen.', f'Stellt {entity} für die Shadow-Entscheidung bereit.', '', 'Neun climate.beispiel_bt_XX sowie zwei W600-Climate-/Ventil-Adapter und deren Gültigkeits-/Start-/Halten-Templates.', 'Raumliste, Gewicht 2 für BT 01, Schwellen und externe Attribute abgleichen.', 'Nur gültige Raumwerte zählen; kein Kesselbefehl.')
for suffix, threshold, duration in [('Start Stabil', 'mindestens zwei gewichtete Punkte', 'fünf Minuten'), ('Komfort Stabil', 'mindestens 2 °C maximalen Fehlbetrag', 'drei Minuten')]:
    NOTES[('template', f'Demo Shadow {suffix}')] = (f'Entprellt Shadow-Anforderung mit {threshold} über {duration}.', 'Vermeidet hektisches Flattern des reinen Heizbedarfs-Merkers.', '', 'sensor.demo_shadow_punkte, sensor.demo_shadow_ungueltig und sensor.demo_shadow_defizit; automation.wolf_shadow.', 'Punkte, Defizit und delay_on an Trägheit der Heizungsanlage anpassen.', 'Mindestens zwei ungültige Räume sperren die stabile Anforderung; keine direkte Wolf-Schaltung.')
NOTES[('template', 'Demo Preis Guenstig')] = ('Klassifiziert den Tibber-Preis unter 0,20 EUR/kWh oder Ranking bis 0,25 als günstig.', 'Liefert das Tarifsignal für die Wallbox-Freigabe.', '', 'sensor.beispiel_tibber_eur_kwh mit gültigem Preis und optionalem intraday_price_ranking; automation.wallbox_freigabe.', 'EUR/kWh-Einheit, Preisgrenze und Ranking für den eigenen Tarif prüfen.', 'Ungültige/fehlende Preise gelten nicht als günstig; laufendes Laden folgt separater Zustimmung.')
for suffix, sign in [('Ladung', 'positive'), ('Entladung', 'negative')]:
    NOTES[('template', f'Demo EcoFlow {suffix}')] = (f'Splittet {sign} Batterieleistung in einen nichtnegativen W-Sensor.', f'Liefert die Quelle für den {suffix}-Integrationssensor.', '', 'sensor.beispiel_ecoflow_batterie_w mit signierter Leistung in W.', 'Vorzeichenkonvention und Einheit der eigenen EcoFlow-Integration prüfen.', 'Bei ungültiger Telemetrie nicht verfügbar; kein Akku-Steuerbefehl.')
    NOTES[('sensor', f'Demo EcoFlow {suffix} Energie')] = (f'Integriert EcoFlow-{suffix}leistung zeitlich zu kWh.', f'Zeigt kumulierte {suffix}energie statt Momentanleistung.', '', f'sensor.demo_ecoflow_{suffix.lower()} (Template), HA-Integration-Plattform und gültige W-Telemetrie.', 'Einheit, Methode left und Reset-/Langzeitstatistik des Quellsensors kontrollieren.', 'Messschätzung, kein abrechnungsfähiger Zähler; Sensor-Plattform benötigt HA-Neustart.')

LIST_DOMAINS = {'automation', 'template', 'sensor'}

def comment(domain, key):
    """Return a complete comment block without changing any YAML value."""
    if (domain, key) not in NOTES:
        # The exporter security fixtures intentionally contain only public_demo.
        if (domain, key) != ('automation', 'demo'):
            raise ValueError(f'Missing canonical component note: {domain}.{key}')
        note = ('Test-Automation ohne Aktor.', 'Prüft den sicheren Exportpfad.', 'Testfall.', 'Testfixture.', 'Nur isoliert verwenden.', 'Keine produktive Installation.')
    else:
        note = NOTES[(domain, key)]
    purpose, benefit, when, dependencies, adjust, safety = note
    if domain == 'automation':
        install = 'Als einzelnes Listenelement an automation: (automations.yaml) anhängen; nicht als Mapping einrücken.'
    elif domain in ('template', 'sensor'):
        install = f'Als einzelnes Listenelement an die {domain}:-Liste anhängen; nicht als Mapping einrücken.'
    else:
        install = f'Diesen einen Schlüssel in das Mapping {domain}: mergen (z. B. configuration.yaml oder passender Mapping-Include); nicht die ganze Domain ersetzen.'
    lines = [f'# Baustein: {domain}.{key}', f'# Zweck: {purpose}', f'# Nutzen: {benefit}']
    if domain == 'automation':
        lines.append(f'# Wann: {when}')
    lines += [f'# Einbau: {install}', f'# Abhängigkeiten: {dependencies}', f'# Anpassen: {adjust}', f'# Sicherheitsgrenze: {safety}', '# Entweder dieser Einzelbaustein oder packages/haus.yaml; niemals beide parallel installieren.']
    return '\n'.join(lines) + '\n'
