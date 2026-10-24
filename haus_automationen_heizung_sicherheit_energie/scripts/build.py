#!/usr/bin/env python3
"""Generate the self-contained, synthetic HA package. No private source is imported."""
from pathlib import Path
import yaml
class Secret(str):
    pass

yaml.SafeDumper.add_representer(Secret, lambda dumper, value: dumper.represent_scalar('!secret', str(value)))
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'packages' / 'haus.yaml'
P.parent.mkdir(exist_ok=True)
rooms = [f'climate.beispiel_bt_{i:02}' for i in range(1, 10)]
wrooms = [f'climate.beispiel_w600_{i:02}' for i in range(1, 3)]
cameras = [f'zone_{i:02}' for i in range(1, 7)]
D = {'input_boolean': {}, 'input_number': {}, 'input_text': {}, 'template': [], 'automation': [], 'script': {}, 'sensor': [], 'shell_command': {'demo_camera_maintain': 'python3 /config/demo_camera_media.py maintain'}, 'rest_command': {'demo_camera_finished': {'url': Secret('demo_camera_webhook_url'), 'method': 'post', 'headers': {'X-Gitlab-Token': Secret('demo_camera_webhook_token')}, 'content_type': 'application/json', 'payload': "{{ {'event_type':'camera_phase_finished','camera':camera,'episode_id':episode_id,'started_at':started_at,'ended_at':ended_at,'reason':reason,'snapshot_count':snapshot_count | int} | to_json }}"}}}
def ib(key, initial=None):
    x = {'name': key}
    if initial is not None: x['initial'] = initial
    D['input_boolean'][key] = x
for key in ('demo_bt_freigabe','demo_wolf_freigabe','demo_sicherheit_freigabe','demo_laden_freigabe'):
    ib(key, False)
for key in ('demo_kalender_ownership','demo_wolf_ownership','demo_shadow','demo_nacht','demo_ladesitzung','demo_lade_zaehler_gueltig'):
    ib(key)
for key,unit,maxval,step in [('demo_lade_zaehler','kWh',1000000,.001),('demo_lade_kosten','EUR',100000,.0001),('demo_lade_energie','kWh',100000,.001),('demo_lade_preis','EUR/kWh',10,.00001),('demo_letzte_energie','kWh',100000,.001),('demo_letzte_kosten','EUR',100000,.0001)]:
    D['input_number'][key] = {'name':key,'min':0,'max':maxval,'step':step,'mode':'box','unit_of_measurement':unit}
for key in ('demo_kalender_wolf_vorher','demo_wolf_ziel'):
    D['input_text'][key] = {'name':key,'max':50}
T = {'sensor':[], 'binary_sensor':[]}
def sensor(name,state,**kw): T['sensor'].append({'name':name,'state':state,**kw})
def bs(name,state,**kw): T['binary_sensor'].append({'name':name,'state':state,**kw})
for i in range(1,3):
    c=f'climate.beispiel_w600_{i:02}'; v=f'sensor.beispiel_w600_{i:02}_ventil'
    valid=f'binary_sensor.demo_w600_{i:02}_gueltig'
    bs(f'Demo W600 {i:02} gueltig', "{% set c = states('"+c+"') %}{% set v = states('"+v+"') %}{% set x = states.sensor.beispiel_w600_"+f'{i:02}'+"_ventil %}{{ c not in ['unknown','unavailable'] and is_number(state_attr('"+c+"','temperature')) and is_number(state_attr('"+c+"','current_temperature')) and is_number(v) and 0 <= v | float(-1) <= 100 and x is not none and 0 <= as_timestamp(now()) - as_timestamp(x.last_reported, 0) <= 21600 }}")
    bs(f'Demo W600 {i:02} start',"{{ is_state('"+valid+"','on') and state_attr('"+c+"','hvac_action') == 'heating' and state_attr('"+c+"','temperature') | float(0) - state_attr('"+c+"','current_temperature') | float(0) >= 0.3 and states('"+v+"') | float(0) > 70 }}")
    bs(f'Demo W600 {i:02} halten',"{{ is_state('"+valid+"','on') and state_attr('"+c+"','hvac_action') == 'heating' and states('"+v+"') | float(0) >= 30 }}")
# Jinja room table is a public, synthetic adapter boundary. One weighted room, eight ordinary rooms, two W600s.
row = "[" + ','.join("{'e':'%s','w':%s,'w600':%s}"%(c,2 if i==0 else 1,'false') for i,c in enumerate(rooms)) + ',' + ','.join("{'e':'%s','w':1,'w600':%s}"%(c,'true') for c in wrooms)+"]"
calc = """{% set ns = namespace(points=0,invalid=0,max_deficit=0,hold=false) %}{% for r in ROOMS %}{% set idx = r.e[-2:] %}{% set v = (is_state('binary_sensor.demo_w600_' ~ idx ~ '_gueltig','on') if r.w600 else states(r.e) not in ['unknown','unavailable'] and state_attr(r.e,'degraded_mode') != true and state_attr(r.e,'errors') in [none, [], ''] and is_number(state_attr(r.e,'temperature')) and is_number(state_attr(r.e,'current_temperature'))) %}{% if not v %}{% set ns.invalid = ns.invalid + 1 %}{% else %}{% set heat = state_attr(r.e,'hvac_action') == 'heating' %}{% set deficit = state_attr(r.e,'temperature') | float(0) - state_attr(r.e,'current_temperature') | float(0) %}{% set start = (is_state('binary_sensor.demo_w600_' ~ idx ~ '_start','on') if r.w600 else heat and deficit >= 0.3) %}{% set holding = (is_state('binary_sensor.demo_w600_' ~ idx ~ '_halten','on') if r.w600 else heat) %}{% if start %}{% set ns.points = ns.points + r.w %}{% endif %}{% if holding %}{% set ns.hold = true %}{% endif %}{% if heat and deficit > ns.max_deficit %}{% set ns.max_deficit = deficit %}{% endif %}{% endif %}{% endfor %}""".replace('ROOMS',row)
for name,part in [('Demo Shadow Punkte','points'),('Demo Shadow Ungueltig','invalid'),('Demo Shadow Defizit','max_deficit')]:
    sensor(name,calc+'{{ ns.'+part+' }}')
bs('Demo Shadow Halten',calc+'{{ ns.hold }}')
bs('Demo Shadow Start Stabil',"{{ is_number(states('sensor.demo_shadow_punkte')) and is_number(states('sensor.demo_shadow_ungueltig')) and states('sensor.demo_shadow_punkte') | int(0) >= 2 and states('sensor.demo_shadow_ungueltig') | int(99) < 2 }}",delay_on='00:05:00')
bs('Demo Shadow Komfort Stabil',"{{ is_number(states('sensor.demo_shadow_defizit')) and is_number(states('sensor.demo_shadow_ungueltig')) and states('sensor.demo_shadow_defizit') | float(0) >= 2 and states('sensor.demo_shadow_ungueltig') | int(99) < 2 }}",delay_on='00:03:00')
bs('Demo Preis Guenstig',"{{ is_number(states('sensor.beispiel_tibber_eur_kwh')) and 0 <= states('sensor.beispiel_tibber_eur_kwh') | float(-1) <= 10 and ((states('sensor.beispiel_tibber_eur_kwh') | float(99)) < 0.20 or (is_number(state_attr('sensor.beispiel_tibber_eur_kwh','intraday_price_ranking')) and 0 <= state_attr('sensor.beispiel_tibber_eur_kwh','intraday_price_ranking') | float(99) <= 0.25)) }}")
for suffix,expr in [('Ladung',"[states('sensor.beispiel_ecoflow_batterie_w') | float(0),0] | max"),('Entladung',"[0 - states('sensor.beispiel_ecoflow_batterie_w') | float(0),0] | max")]:
    sensor('Demo EcoFlow '+suffix,"{{ "+expr+" }}",availability="{{ is_number(states('sensor.beispiel_ecoflow_batterie_w')) }}",unit_of_measurement='W',device_class='power',state_class='measurement')
    D['sensor'].append({'platform':'integration','source':'sensor.demo_ecoflow_'+suffix.lower(),'name':'Demo EcoFlow '+suffix+' Energie','unit_prefix':'k','unit_time':'h','method':'left'})
D['template'].append(T)
def auto(id,trigger,action,**kw): D['automation'].append({'id':'public_'+id,'alias':'Demo '+id.replace('_',' '),'mode':kw.pop('mode','single'),'triggers':trigger,'actions':action,**kw})
def st(e,to=None,**extra):
    return {'trigger':'state','entity_id':e,**({'to':to} if to is not None else {}),**extra}
def act(service,entity=None,data=None):
    x={'action':service}
    if entity is not None: x['target']={'entity_id':entity}
    if data is not None: x['data']=data
    return x
def cond(t): return {'condition':'template','value_template':t}
def var(**kw): return {'variables':kw}
def wait(t): return {'wait_template':t,'timeout':'00:02:00','continue_on_timeout':True}
start=[st('binary_sensor.demo_shadow_start_stabil','on'),st('binary_sensor.demo_shadow_komfort_stabil','on'),st('binary_sensor.demo_shadow_halten'),{'trigger':'homeassistant','event':'start'},{'trigger':'event','event_type':'automation_reloaded'}]
auto('wolf_shadow',start,[{'choose':[{'conditions':"{{ is_state('binary_sensor.demo_shadow_start_stabil','on') or is_state('binary_sensor.demo_shadow_komfort_stabil','on') }}",'sequence':[act('input_boolean.turn_on','input_boolean.demo_shadow')]},{'conditions':"{{ is_state('binary_sensor.demo_shadow_halten','off') and is_state('binary_sensor.demo_shadow_start_stabil','off') and is_state('binary_sensor.demo_shadow_komfort_stabil','off') }}",'sequence':[{'delay':'00:05:00'},cond("{{ is_state('binary_sensor.demo_shadow_halten','off') and is_state('binary_sensor.demo_shadow_start_stabil','off') and is_state('binary_sensor.demo_shadow_komfort_stabil','off') }}"),act('input_boolean.turn_off','input_boolean.demo_shadow')]}]}],mode='restart')
# Calendar service response is validated BEFORE event derivation. Invalid data does not mutate ownership or actuators.
cal='calendar.beispiel_abwesenheit'; target='select.beispiel_wolf_dhk'; own='input_boolean.demo_kalender_ownership'; wown='input_boolean.demo_wolf_ownership'
caltr=[{'trigger':'time','at':s} for s in ('08:00:00','15:00:00')]+[{'trigger':'time_pattern','minutes':'/15'},{'trigger':'homeassistant','event':'start'},{'trigger':'event','event_type':'automation_reloaded'}]+[{'trigger':'calendar','entity_id':cal,'event':s} for s in ('start','end')]+[st(cal)]
valid="{{ answer is defined and answer is mapping and '"+cal+"' in answer and answer['"+cal+"'] is mapping and answer['"+cal+"'].get('events') is sequence and answer['"+cal+"'].get('events') is not string and answer['"+cal+"'].get('events') is not mapping and answer['"+cal+"'].get('events') | select('mapping') | list | count == answer['"+cal+"'].get('events') | count }}"
# Date-only end exclusive; timestamps converted to local day before applying 15:00 -> 08:00.
window="""{% set ns = namespace(away=false) %}{% set t = as_timestamp(now()) %}{% for e in answer['calendar.beispiel_abwesenheit']['events'] %}{% set a = e.get('start') %}{% set b = e.get('end') %}{% if '[Heizung]' in (e.get('summary','') | string) and a and b %}{% set first = (as_datetime(a).date() if a | string | length == 10 else as_local(as_datetime(a)).date()) %}{% set last = ((as_datetime(b) - timedelta(days=1)).date() if b | string | length == 10 else as_local(as_datetime(b) - timedelta(seconds=1)).date()) %}{% set lo = as_timestamp(first | string ~ ' 15:00:00') %}{% set hi = as_timestamp(last | string ~ ' 08:00:00') %}{% if lo < hi and lo <= t < hi %}{% set ns.away = true %}{% endif %}{% endif %}{% endfor %}{{ ns.away }}"""
# Guard malformed event types/dates before window rendering (including invalid unrelated entries).
valid="""{% set ns = namespace(ok=false) %}{% if answer is defined and answer is mapping and 'calendar.beispiel_abwesenheit' in answer and answer['calendar.beispiel_abwesenheit'] is mapping %}{% set events = answer['calendar.beispiel_abwesenheit'].get('events') %}{% if events is sequence and events is not string and events is not mapping %}{% set ns.ok = true %}{% for e in events %}{% if e is not mapping or e.get('start') is not string or e.get('end') is not string or e.get('summary','') is not string or as_datetime(e.get('start'), none) is none or as_datetime(e.get('end'), none) is none or as_timestamp(e.get('end'), 0) <= as_timestamp(e.get('start'), 0) %}{% set ns.ok = false %}{% endif %}{% endfor %}{% endif %}{% endif %}{{ ns.ok }}"""
all_eco="{{ "+' and '.join("state_attr('%s','preset_mode') == 'eco'"%r for r in rooms)+" }}"
all_normal="{{ "+' and '.join("state_attr('%s','preset_mode') == 'none'"%r for r in rooms)+" }}"
pre="{{ "+' and '.join("states('%s') not in ['unknown','unavailable']"%r for r in rooms)+" }}"
change_eco=[cond(pre),act('climate.set_preset_mode',rooms,{'preset_mode':'eco'}),wait(all_eco),cond(all_eco)]
change_normal=[cond(pre),act('climate.set_preset_mode',rooms,{'preset_mode':'none'}),wait(all_normal),cond(all_normal)]
# Persist ownership only after verified write; do not claim an already-Standby foreign state.
w_start=[cond("{{ is_state('"+wown+"','off') and states('"+target+"') not in ['unknown','unavailable','Standby'] }}"),var(previous_wolf="{{ states('"+target+"') }}"),cond("{{ previous_wolf in ['Auto'] }}"),act('input_text.set_value','input_text.demo_kalender_wolf_vorher',{'value':'{{ previous_wolf }}'}),act('select.select_option',target,{'option':'Standby'}),wait("{{ is_state('"+target+"','Standby') }}"),cond("{{ is_state('"+target+"','Standby') }}"),act('input_boolean.turn_on',wown)]
w_end=[cond("{{ is_state('"+wown+"','on') and is_state('input_text.demo_kalender_wolf_vorher','Auto') and states('"+target+"') in ['Standby','Auto'] }}"),{'if':[{'condition':'state','entity_id':target,'state':'Standby'}],'then':[act('select.select_option',target,{'option':'Auto'}),wait("{{ is_state('"+target+"','Auto') }}")]},cond("{{ is_state('"+target+"','Auto') }}"),act('input_boolean.turn_off',wown)]
calact=[cond("{{ states('"+cal+"') not in ['unknown','unavailable'] }}"),{'action':'calendar.get_events','target':{'entity_id':cal},'data':{'start_date_time':"{{ today_at('00:00') }}",'end_date_time':"{{ today_at('00:00') + timedelta(days=1) }}"},'response_variable':'answer','continue_on_error':True},cond(valid),var(away=window),{'choose':[{'conditions':"{{ away | bool(false) }}",'sequence':[{'if':[{'condition':'state','entity_id':'input_boolean.demo_bt_freigabe','state':'on'}],'then':[{'choose':[{'conditions':"{{ is_state('"+own+"','on') or not ("+all_eco[3:-3]+") }}",'sequence':change_eco+[act('input_boolean.turn_on',own)]}]}]},{'if':[{'condition':'state','entity_id':'input_boolean.demo_wolf_freigabe','state':'on'}],'then':[{'choose':[{'conditions':"{{ is_state('"+wown+"','off') }}",'sequence':w_start}]}]}]},{'conditions':"{{ not (away | bool(false)) }}",'sequence':[{'if':[{'condition':'state','entity_id':'input_boolean.demo_bt_freigabe','state':'on'},{'condition':'state','entity_id':own,'state':'on'}],'then':change_normal+[act('input_boolean.turn_off',own)]},{'if':[{'condition':'state','entity_id':'input_boolean.demo_wolf_freigabe','state':'on'},{'condition':'state','entity_id':wown,'state':'on'}],'then':w_end}]}]}]
auto('kalender_abwesenheit',caltr,calact,mode='single')
# Physical commands are deliberately never unlock/disarm; unknown presence blocks absence activation.
absent="{{ is_state('person.beispiel_a','not_home') and is_state('person.beispiel_b','not_home') }}"
secure=[st('person.beispiel_a'),st('person.beispiel_b'),st('input_boolean.demo_nacht'),{'trigger':'homeassistant','event':'start'}]
auto('aufnahme_bei_abwesenheit',secure,[{'condition':'state','entity_id':'input_boolean.demo_sicherheit_freigabe','state':'on'},{'choose':[{'conditions':"{{ "+absent[3:-3]+" or is_state('input_boolean.demo_nacht','on') }}",'sequence':[act('switch.turn_on',[f'switch.beispiel_{c}_aufnahme' for c in cameras])]},{'conditions':"{{ (is_state('person.beispiel_a','home') or is_state('person.beispiel_b','home')) and is_state('input_boolean.demo_nacht','off') }}",'sequence':[act('switch.turn_off',[f'switch.beispiel_{c}_aufnahme' for c in cameras])]}]}],mode='restart')
D['script']['demo_abschliessen']={'alias':'Demo abschliessen','sequence':[{'condition':'state','entity_id':'input_boolean.demo_sicherheit_freigabe','state':'on'},cond(absent),{'condition':'state','entity_id':'binary_sensor.beispiel_tuer_offen','state':'off'},act('lock.lock','lock.beispiel_eingang'),wait("{{ is_state('lock.beispiel_eingang','locked') }}"),{'condition':'state','entity_id':'lock.beispiel_eingang','state':'locked'}]}
auto('schloss_abwesenheit',[st('person.beispiel_a'),st('person.beispiel_b')],[{'condition':'state','entity_id':'input_boolean.demo_sicherheit_freigabe','state':'on'},cond(absent),act('script.demo_abschliessen')])
auto('alarm_meldung',[st('alarm_control_panel.beispiel_alarmo','triggered')],[act('persistent_notification.create',data={'title':'Demo Alarm','message':'Alarmo meldet einen Alarm; Sensoren vor Ort prüfen.'})])
auto('eingang_licht',[st('binary_sensor.beispiel_eingang_bewegung','on')],[{'condition':'state','entity_id':'input_boolean.demo_sicherheit_freigabe','state':'on'},act('light.turn_on','light.beispiel_eingang'),{'delay':'00:03:00'},act('light.turn_off','light.beispiel_eingang')],mode='restart')
auto('display_klingel',[st('binary_sensor.beispiel_klingel','on')],[{'condition':'state','entity_id':'input_boolean.demo_sicherheit_freigabe','state':'on'},act('light.turn_on','light.beispiel_display'),act('persistent_notification.create',data={'title':'Klingel','message':'Eingang prüfen; Kameraansicht im Dashboard öffnen.'}),{'delay':'00:01:00'},act('light.turn_off','light.beispiel_display')],mode='restart')
# This is a best-effort callback, not a durable episode/outbox. Reload or a racing edge can lose completion.
auto('kamera_retention',[{'trigger':'time','at':'03:20:00'}],[act('shell_command.demo_camera_maintain')])
for i,c in enumerate(cameras):
    det=f'binary_sensor.beispiel_{c}_person'; animal=f'binary_sensor.beispiel_{c}_tier'; rec=f'switch.beispiel_{c}_aufnahme'; cam=f'camera.beispiel_{c}'
    detection="(is_state('"+det+"','on') or is_state('"+animal+"','on'))"
    gate="{{ is_state('"+rec+"','on') and "+detection+" and states('"+cam+"') not in ['unknown','unavailable'] }}"
    reason="{{ 'recording_disabled' if not is_state('"+rec+"','on') else 'detection_ended' if not "+detection+" else 'camera_unavailable' }}"
    trigger=[{'trigger':'template','value_template':"{{ "+detection+" }}"},{'trigger':'event','event_type':'demo_camera_continue','event_data':{'camera':c}},{'trigger':'homeassistant','event':'start'},{'trigger':'event','event_type':'automation_reloaded'}]
    finish=lambda count: [var(reason=reason, ended_at='{{ now().isoformat() }}', snapshot_count=count),act('rest_command.demo_camera_finished',data={'camera':c,'episode_id':'{{ episode_id }}','started_at':'{{ started_at }}','ended_at':'{{ ended_at }}','reason':'{{ reason }}','snapshot_count':'{{ snapshot_count | int }}'})]
    sequence=[{'condition':'state','entity_id':'input_boolean.demo_sicherheit_freigabe','state':'on'},
              var(episode_id="{{ trigger.event.data.episode_id if trigger.platform == 'event' and trigger.event.event_type == 'demo_camera_continue' else context.id | md5 }}",started_at="{{ trigger.event.data.started_at if trigger.platform == 'event' and trigger.event.event_type == 'demo_camera_continue' else now().isoformat() }}",base_index="{{ trigger.event.data.next_index | int(0) if trigger.platform == 'event' and trigger.event.event_type == 'demo_camera_continue' else 0 }}")]
    if i>=3:
        sequence += [{'wait_template':"{{ states('"+cam+"') not in ['unknown','unavailable'] or not is_state('"+rec+"','on') or not "+detection+" }}",'timeout':'00:00:30','continue_on_timeout':True}]
    frame=act('camera.snapshot',cam,{'filename':'/media/demo_camera/'+c+'/{{ now().strftime("%Y%m%dT%H%M%S%f") }}_{{ episode_id }}_{{ base_index | int + repeat.index }}.jpg'})
    frame['continue_on_error']=True
    sequence += [{'repeat':{'count':100,'sequence':[{'choose':[{'conditions':gate,'sequence':[frame,{'delay':'00:00:05'}]}],
                    'default':finish('{{ base_index | int + repeat.index - 1 }}')+[{'stop':'Episode abgeschlossen'}]}]}},
                 {'choose':[{'conditions':gate,'sequence':[{'event':'demo_camera_continue','event_data':{'camera':c,'episode_id':'{{ episode_id }}','started_at':'{{ started_at }}','next_index':'{{ base_index | int + 100 }}'}}]}],
                  'default':finish('{{ base_index | int + 100 }}')}]
    auto('kamera_'+c,trigger,sequence,mode='restart')
# EV control: this is permission only; never storage control and never interrupt an active charge for price alone.
auto('wallbox_freigabe',[st('binary_sensor.beispiel_angeschlossen'),st('binary_sensor.demo_preis_guenstig'),st('sensor.beispiel_ladestatus'),st('person.beispiel_a'),st('person.beispiel_b'),{'trigger':'time_pattern','minutes':'/5'},{'trigger':'homeassistant','event':'start'}],[{'condition':'state','entity_id':'input_boolean.demo_laden_freigabe','state':'on'},{'choose':[{'conditions':"{{ is_state('binary_sensor.beispiel_angeschlossen','on') and (is_state('person.beispiel_a','home') or is_state('person.beispiel_b','home')) and (is_state('binary_sensor.demo_preis_guenstig','on') or is_state('sensor.beispiel_ladestatus','charging')) }}",'sequence':[act('switch.turn_on','switch.beispiel_wallbox_freigabe')]}],'default':[act('switch.turn_off','switch.beispiel_wallbox_freigabe')]}],mode='restart')
# Settle using previous tariff on price-change; invalid energy or tariff holds all bookkeeping.
energy='sensor.beispiel_wallbox_kwh'; price='sensor.beispiel_tibber_eur_kwh'; status='sensor.beispiel_ladestatus'
pr="{{ is_number(states('"+energy+"')) and is_number(states('"+price+"')) and 0 <= states('"+price+"') | float(-1) <= 10 and 0 <= states('"+energy+"') | float(-1) <= 1000000 and states('"+status+"') not in ['unknown','unavailable'] }}"
settle=[var(delta="{{ states('"+energy+"') | float(0) - states('input_number.demo_lade_zaehler') | float(0) }}"),cond("{{ 0 <= delta | float(-1) <= 100 }}"),act('input_number.set_value','input_number.demo_lade_kosten',{'value':"{{ (states('input_number.demo_lade_kosten') | float(0) + delta | float(0) * states('input_number.demo_lade_preis') | float(0)) | round(4) }}"}),act('input_number.set_value','input_number.demo_lade_energie',{'value':"{{ (states('input_number.demo_lade_energie') | float(0) + delta | float(0)) | round(3) }}"}),act('input_number.set_value','input_number.demo_lade_zaehler',{'value':"{{ states('"+energy+"') | float(0) }}"}),act('input_number.set_value','input_number.demo_lade_preis',{'value':"{{ states('"+price+"') | float(0) }}"})]
auto('ladekosten',[st(energy),st(price),st(status),{'trigger':'time_pattern','minutes':'/1'},{'trigger':'homeassistant','event':'start'}],[cond(pr),{'choose':[{'conditions':"{{ is_state('"+status+"','charging') and is_state('input_boolean.demo_ladesitzung','off') }}",'sequence':[act('input_number.set_value','input_number.demo_lade_zaehler',{'value':"{{ states('"+energy+"') | float(0) }}"}),act('input_number.set_value','input_number.demo_lade_preis',{'value':"{{ states('"+price+"') | float(0) }}"}),act('input_number.set_value','input_number.demo_lade_kosten',{'value':0}),act('input_number.set_value','input_number.demo_lade_energie',{'value':0}),act('input_boolean.turn_on','input_boolean.demo_ladesitzung')]},{'conditions':"{{ is_state('input_boolean.demo_ladesitzung','on') }}",'sequence':settle+[{'if':[cond("{{ not is_state('"+status+"','charging') and as_timestamp(now()) - as_timestamp(states.sensor.beispiel_ladestatus.last_changed, as_timestamp(now())) >= 300 }}")],'then':[act('input_number.set_value','input_number.demo_letzte_energie',{'value':"{{ states('input_number.demo_lade_energie') | float(0) }}"}),act('input_number.set_value','input_number.demo_letzte_kosten',{'value':"{{ states('input_number.demo_lade_kosten') | float(0) }}"}),act('input_boolean.turn_off','input_boolean.demo_ladesitzung')]}]}]}],mode='single')
P.write_text('# Generiert mit scripts/build.py; nur fiktive Entity-IDs.\n'+yaml.safe_dump(D,allow_unicode=True,sort_keys=False,width=110))
print(f'{P}: {len(D["automation"])} automations, {len(T["sensor"])} template sensors')
