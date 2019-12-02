from cereal import car, arne182
from selfdrive.controls.lib.drive_helpers import EventTypes as ET, create_event, create_event_arne

from selfdrive.controls.lib.alertmanager import AlertManager
from selfdrive.controls.lib.drive_helpers import get_events


ret = car.CarState.new_message()
ret_arne182 = arne182.CarStateArne182.new_message()

events = []
eventsArne182 = []


events.append(create_event('steerTempUnavailable', [ET.WARNING]))
eventsArne182.append(create_event_arne('longControlDisabled', [ET.WARNING]))

ret.events = events
ret_arne182.events = eventsArne182

AM = AlertManager()

CS, CS_Arne = ret.as_reader(), ret_arne182.as_reader()
events = list(CS.events) + list(CS_Arne.events)

frame = 0
enabled = True
for e in get_events(events, [ET.WARNING]):
  extra_text = ""
  AM.add(frame, e, enabled, extra_text_2=extra_text)
  print(str(e))
