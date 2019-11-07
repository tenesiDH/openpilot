from selfdrive.services import service_list
import selfdrive.messaging_arne as messaging_arne


class PhantomReceiver:
  def __init__(self):
    self.phantomData_sock = None

  def broadcast_data(self, speed, angle, time):
    with open('/data/bd.test', 'a') as f:
      f.write('{}\n'.format([speed, angle, time]))
    data = messaging_arne.new_message()
    data.init('phantomData')
    data.phantomData.status = True
    data.phantomData.speed = speed
    data.phantomData.angle = angle
    data.phantomData.time = time
    self.phantomData_sock.send(data.to_bytes())

  def enable_phantom(self):
    with open('/data/bd.test', 'a') as f:
      f.write('{}\n'.format('open socket'))
    self.phantomData_sock = messaging_arne.pub_sock(service_list['phantomData'].port)

  def disable_phantom(self):
    with open('/data/bd.test', 'a') as f:
      f.write('{}\n'.format('close socket'))
    self.phantomData_sock.close()
