from cereal import car, arne182
from selfdrive.controls.lib.drive_helpers import EventTypes as ET, create_event, create_event_arne

from selfdrive.controls.lib.alertmanager import AlertManager
from selfdrive.controls.lib.drive_helpers import get_events


events = []
ret = car.CarState.new_message()
events.append(create_event('steerTempUnavailable', [ET.WARNING]))
ret.events = events

AM = AlertManager()

CS = ret.as_reader()
events = list(CS.events)

frame = 0
enabled = True
for e in get_events(events, [ET.WARNING]):
  extra_text = ""
  AM.add(frame, e, enabled, extra_text_2=extra_text)
  print(str(e))
