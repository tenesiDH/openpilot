from cereal import car
from common.numpy_fast import clip
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.hyundai.hyundaican import create_lkas11, create_lkas12, \
                                             create_1191, create_1156, \
                                             create_clu11, create_scc12
from selfdrive.car.hyundai.values import CAR, Buttons, SteerLimitParams
from selfdrive.can.packer import CANPacker


VisualAlert = car.CarControl.HUDControl.VisualAlert

# Accel limits
ACCEL_HYST_GAP = 0.02  # don't change accel command for small oscilalitons within this value
ACCEL_MAX = 1.5  # 1.5 m/s2
ACCEL_MIN = -3.0 # 3   m/s2
ACCEL_SCALE = max(ACCEL_MAX, -ACCEL_MIN)

def accel_hysteresis(accel, accel_steady):

  # for small accel oscillations within ACCEL_HYST_GAP, don't change the accel command
  if accel > accel_steady + ACCEL_HYST_GAP:
    accel_steady = accel - ACCEL_HYST_GAP
  elif accel < accel_steady - ACCEL_HYST_GAP:
    accel_steady = accel + ACCEL_HYST_GAP
  accel = accel_steady

  return accel, accel_steady

def process_hud_alert(enabled, fingerprint, visual_alert, left_line,
                       right_line, left_lane_depart, right_lane_depart):

  hud_alert = 0
  if visual_alert == VisualAlert.steerRequired:
    hud_alert = 3

  # initialize to no line visible
  lane_visible = 1
  if left_line and right_line:
    if enabled:
      lane_visible = 3
    else:
      lane_visible = 4
  elif left_line:
    lane_visible = 5
  elif right_line:
    lane_visible = 6

  # initialize to no warnings
  left_lane_warning = 0
  right_lane_warning = 0
  if left_lane_depart:
    left_lane_warning = 1 if fingerprint in [CAR.GENESIS , CAR.GENESIS_G90, CAR.GENESIS_G80] else 2
  if right_lane_depart:
    right_lane_warning = 1 if fingerprint in [CAR.GENESIS , CAR.GENESIS_G90, CAR.GENESIS_G80] else 2

  return hud_alert, lane_visible, left_lane_warning, right_lane_warning

class CarController():
  def __init__(self, dbc_name, car_fingerprint):
    self.apply_steer_last = 0
    self.accel_steady = 0.
    self.car_fingerprint = car_fingerprint
    self.lkas11_cnt = 0
    self.scc12_cnt = 0
    self.clu11_cnt = 0
    self.last_resume_frame = 0
    self.last_lead_distance = 0
    # True when giraffe switch 2 is low and we need to replace all the camera messages
    # otherwise we forward the camera msgs and we just replace the lkas cmd signals
    self.camera_disconnected = False

    self.packer = CANPacker(dbc_name)

  def update(self, enabled, CS, frame, actuators, pcm_cancel_cmd, visual_alert,
              left_line, right_line, left_lane_depart, right_lane_depart):

    # *** compute control surfaces ***

    # gas and brake
    apply_accel = actuators.gas - actuators.brake

    apply_accel, self.accel_steady = accel_hysteresis(apply_accel, self.accel_steady)
    apply_accel = clip(apply_accel * ACCEL_SCALE, ACCEL_MIN, ACCEL_MAX)

    ### Steering Torque
    apply_steer = actuators.steer * SteerLimitParams.STEER_MAX

    apply_steer = apply_std_steer_torque_limits(apply_steer, self.apply_steer_last, CS.steer_torque_driver, SteerLimitParams)

    lkas_active = enabled and abs(CS.angle_steers) > 100.

    if not lkas_active:
      apply_steer = 0

    steer_req = 1 if apply_steer else 0

    self.apply_accel_last = apply_accel
    self.apply_steer_last = apply_steer

    hud_alert, lane_visible, left_lane_warning, right_lane_warning =\
            process_hud_alert(enabled, self.car_fingerprint, visual_alert,
            left_line, right_line,left_lane_depart, right_lane_depart)

    can_sends = []

    self.lkas11_cnt = frame % 0x10
    self.scc12_cnt %= 15
    clu11_cnt = frame % 0x10

    if self.camera_disconnected:
      if (frame % 10) == 0:
        can_sends.append(create_lkas12())
      if (frame % 50) == 0:
        can_sends.append(create_1191())
      if (frame % 7) == 0:
        can_sends.append(create_1156())

    can_sends.extend(create_lkas11(self.packer, self.car_fingerprint, apply_steer, steer_req, self.lkas11_cnt,
                                   lkas_active, CS.lkas11, hud_alert, lane_visible, left_lane_depart, right_lane_depart,
                                   keep_stock=(not self.camera_disconnected)))

    speed = 60 if CS.v_ego < 17. else CS.clu11["CF_Clu_Vanz"]
    can_sends.append(create_clu11(self.packer, CS.clu11, Buttons.NONE, speed, clu11_cnt))

    if frame % 2:
      can_sends.append(create_scc12(self.packer, apply_accel, enabled, self.scc12_cnt, CS.scc12))
      self.scc12_cnt += 1

    if pcm_cancel_cmd:
      can_sends.append(create_clu11(self.packer, CS.clu11, Buttons.CANCEL, speed, clu11_cnt))

    if CS.stopped:
      # run only first time when the car stopped
      if self.last_lead_distance == 0:
        # get the lead distance from the Radar
        self.last_lead_distance = CS.lead_distance
        self.clu11_cnt = 0
      # when lead car starts moving, create 6 RES msgs
      elif CS.lead_distance > self.last_lead_distance and (frame - self.last_resume_frame) > 5:
        can_sends.append(create_clu11(self.packer, CS.clu11, Buttons.RES_ACCEL, speed, clu11_cnt))
        self.clu11_cnt += 1
        # interval after 6 msgs
        if self.clu11_cnt > 5:
          self.last_resume_frame = frame
          self.clu11_cnt = 0
    # reset lead distnce after the car starts moving
    elif self.last_lead_distance != 0:
      self.last_lead_distance = 0  

    return can_sends
