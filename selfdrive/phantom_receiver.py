import zmq
from selfdrive.services import service_list
import selfdrive.messaging_arne as messaging_arne


class PhantomReceiver:
  def __init__(self):
    self.phantomData_sock = None

  def broadcast_data(self, status, speed, angle, time):
    status = True if status == "true" or status else False
    data = messaging_arne.new_message()
    data.init('phantomData')
    data.phantomData.status = status
    data.phantomData.speed = speed
    data.phantomData.angle = angle
    data.phantomData.time = time
    self.phantomData_sock.send(data.to_bytes())

  def open_socket(self):
    self.phantomData_sock = messaging_arne.pub_sock(zmq.Context(), service_list['phantomData'].port)

  def close_socket(self):
    self.phantomData_sock.close()
