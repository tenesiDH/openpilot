from cereal import car
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.hyundai.hyundaican import create_lkas11, create_lkas12, \
                                             create_1191, create_1156, \
                                             create_clu11, create_spas11, create_spas12
from selfdrive.car.hyundai.values import CAR, Buttons
from selfdrive.can.packer import CANPacker
import numpy as np

# Steer torque limits

class SteerLimitParams:
  STEER_MAX = 255   # 409 is the max, 255 is stock
  STEER_DELTA_UP = 3
  STEER_DELTA_DOWN = 7
  STEER_DRIVER_ALLOWANCE = 50
  STEER_DRIVER_MULTIPLIER = 2
  STEER_DRIVER_FACTOR = 1
  STEER_ANG_MAX = 45          # SPAS Max Angle
  STEER_ANG_MAX_RATE = 1.2    # SPAS Degrees per ms

VisualAlert = car.CarControl.HUDControl.VisualAlert

def process_hud_alert(enabled, fingerprint, visual_alert, left_line,
                       right_line, left_lane_depart, right_lane_depart):

  hud_alert = 0
  if visual_alert == VisualAlert.steerRequired:
    hud_alert = 3

  # initialize to no line visible
  lane_visible = 1
  if left_line and right_line or enabled:
    lane_visible = 3
    #else:if not enabled:    
      #lane_visible = 4
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
    self.car_fingerprint = car_fingerprint
    self.lkas11_cnt = 0
    self.clu11_cnt = 0
    self.last_resume_frame = 0
    self.last_lead_distance = 0
    # True when giraffe switch 2 is low and we need to replace all the camera messages
    # otherwise we forward the camera msgs and we just replace the lkas cmd signals
    self.camera_disconnected = False
    self.en_cnt = 0
    self.apply_steer_ang = 0.0
    self.en_spas = 3
    self.mdps11_stat_last = 0
    self.lkas = False
    self.spas_present = False # TODO Make Automatic
    self.packer = CANPacker(dbc_name)

  def update(self, enabled, CS, frame, actuators, pcm_cancel_cmd, visual_alert,
              left_line, right_line, left_lane_depart, right_lane_depart):

    ### Steering Torque
    apply_steer = actuators.steer * SteerLimitParams.STEER_MAX

    apply_steer = apply_std_steer_torque_limits(apply_steer, self.apply_steer_last, CS.steer_torque_driver, SteerLimitParams)

    # SPAS limit angle extremes for safety
    apply_steer_ang_req = np.clip(actuators.steerAngle, -1*(SteerLimitParams.STEER_ANG_MAX), SteerLimitParams.STEER_ANG_MAX)
    # SPAS limit angle rate for safety
    if abs(self.apply_steer_ang - apply_steer_ang_req) > 0.6:
      if apply_steer_ang_req > self.apply_steer_ang:
        self.apply_steer_ang += 0.5
      else:
        self.apply_steer_ang -= 0.5
    else:
      self.apply_steer_ang = apply_steer_ang_req

    # Use LKAS or SPAS
    if CS.mdps11_stat == 7 or CS.v_ego > 2.7:
      self.lkas = True
    elif CS.v_ego < 15:
      self.lkas = False
    if self.spas_present:
      self.lkas = True


    # Fix for Genesis hard fault when steer request sent while the speed is low 

    if not enabled or CS.v_ego < 15:
      apply_steer = 0

    steer_req = 1 if apply_steer else 0

    self.apply_steer_last = apply_steer

    hud_alert, lane_visible, left_lane_warning, right_lane_warning =\
            process_hud_alert(enabled, self.car_fingerprint, visual_alert,
            left_line, right_line,left_lane_depart, right_lane_depart)

    can_sends = []

    self.lkas11_cnt = frame % 0x10
    self.spas_cnt = frame % 0x200

    if self.camera_disconnected:
      if (frame % 10) == 0:
        can_sends.append(create_lkas12())
      if (frame % 50) == 0:
        can_sends.append(create_1191())
      if (frame % 7) == 0:
        can_sends.append(create_1156())

    can_sends.append(create_lkas11(self.packer, self.car_fingerprint, apply_steer, steer_req, self.lkas11_cnt,
                                   enabled, CS.lkas11, hud_alert, lane_visible, left_lane_depart, right_lane_depart,
                                   keep_stock=(not self.camera_disconnected)))
    # SPAS11 50hz
    if (frame % 2) == 0 and not self.spas_present:
      if CS.mdps11_stat == 7 and not self.mdps11_stat_last == 7:
        self.en_spas == 7
        self.en_cnt = 0

      if self.en_spas == 7 and self.en_cnt >= 8:
        self.en_spas = 3
        self.en_cnt = 0

      if self.en_cnt < 8 and enabled and not self.lkas:
        self.en_spas = 4
      elif self.en_cnt >= 8 and enabled and not self.lkas:
        self.en_spas = 5

      if self.lkas or not enabled:
        self.apply_steer_ang = CS.mdps11_strang
        self.en_spas = 3
        self.en_cnt = 0

      self.mdps11_stat_last = CS.mdps11_stat
      self.en_cnt += 1
      can_sends.append(create_spas11(self.packer, self.car_fingerprint, (self.spas_cnt / 2), self.en_spas, self.apply_steer_ang))

    # SPAS12 20Hz
    if (frame % 5) == 0 and not self.spas_present:
      can_sends.append(create_spas12(self.packer))

    if pcm_cancel_cmd:
      self.clu11_cnt = frame % 0x10
      can_sends.append(create_clu11(self.packer, CS.clu11, Buttons.CANCEL, self.clu11_cnt))

    if CS.stopped:
      # run only first time when the car stopped
      if self.last_lead_distance == 0:
        # get the lead distance from the Radar
        self.last_lead_distance = CS.lead_distance
        self.clu11_cnt = 0
      # when lead car starts moving, create 6 RES msgs
      elif CS.lead_distance > self.last_lead_distance and (frame - self.last_resume_frame) > 5:
        can_sends.append(create_clu11(self.packer, CS.clu11, Buttons.RES_ACCEL, self.clu11_cnt))
        self.clu11_cnt += 1
        # interval after 6 msgs
        if self.clu11_cnt > 5:
          self.last_resume_frame = frame
          self.clu11_cnt = 0
    # reset lead distnce after the car starts moving
    elif self.last_lead_distance != 0:
      self.last_lead_distance = 0  


    return can_sends
