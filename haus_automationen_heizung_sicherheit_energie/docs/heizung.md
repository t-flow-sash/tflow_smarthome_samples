# Heizung: Shadow und Kalender sind verschieden

[← Übersicht](../README.md) · [Integrationsvertrag](setup.md) · [Grenzen](grenzen.md)

## Bedarfs-Shadow (keine physische Wolf-Schaltung)

Neun Better-Thermostat-`climate`-Adapter liefern Soll-/Istwert, `hvac_action`, Degradation und Fehlerstatus; einer zählt doppelt. Zwei W600-Adapter liefern zusätzlich Ventilstellung in Prozent und einen höchstens sechs Stunden alten Messwert. Fehlende oder ungültige Daten zählen als ungültiger Raum. Start setzt mindestens zwei gewichtete Flächenpunkte und höchstens einen ungültigen Raum voraus: bei BT Heizaktion und mindestens 0,3 °C Defizit, bei W600 außerdem Ventil >70 %. Das Haltesignal nutzt bei W600 ≥30 %, bei BT die Heizaktion. Start wird fünf Minuten entprellt; ein Defizit von ≥2 °C setzt nach drei Minuten den Komfortpfad; bei fehlendem Halten wird fünf Minuten verzögert abgeschaltet. HA-Start und Automation-Reload stoßen den Abgleich an. Ergebnis ist nur `input_boolean.demo_shadow`: **kein** `select.select_option` und kein physischer Heizkreis- oder Kesselbefehl. Für echte bedarfsgeführte Wolf-Aktorik fehlen eigene sichere Freigabe, kompatibler Aktor, Feedback und Integrationstests.

## Kalenderpfad (kann Aktoren schreiben)

`calendar.beispiel_abwesenheit` wird über `calendar.get_events` abgefragt. Nur Termine mit `[Heizung]` werden ausgewertet; mehrere überlappende Termine ergeben eine ODER-Abwesenheit. Die Fenster reichen von 15:00 am lokalen ersten bis 08:00 am lokalen letzten eingeschlossenen Tag; ein ganztägiges Enddatum ist exklusiv. Leere Ein-Tages-Fenster wirken nicht. Fehlerhafte API-Daten stoppen die Verarbeitung **vor** Marker- oder Aktorschreibvorgängen. Lokale Zeit/DST und Terminkonvention müssen dennoch am echten Kalender getestet werden.

Zwei **getrennte, initial ausgeschaltete** Freigaben: `input_boolean.demo_bt_freigabe` für neun BT-Presets (`eco`/`none`) und `input_boolean.demo_wolf_freigabe` für `select.beispiel_wolf_dhk` (`Auto`/`Standby`, nicht Warmwasser). HA wartet auf Zustands-Readback, bevor Ownership markiert wird. Fremdes `Standby` wird nicht übernommen; bei unbekanntem/fremdem Select gibt es kein blindes Zurücksetzen auf `Auto`. Marker ohne `initial` können reguläre HA-Neustarts überstehen, sind aber nicht atomar mit physischen Befehlen: Crash zwischen Readback und Marker, manueller Eingriff, Servicefehler und verlorene Helper verlangen Betreiberprüfung. Konkurrierende Writer vorher abschalten oder eindeutig trennen. Das Shadow-Signal ist **nicht** der Auslöser dieses Kalenderpfads.
