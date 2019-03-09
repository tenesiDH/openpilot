from selfdrive.controls.lib.pid import PIController
from common.numpy_fast import interp
from cereal import car
from common.realtime import sec_since_boot


def get_steer_max(CP, v_ego):
  return interp(v_ego, CP.steerMaxBP, CP.steerMaxV)


class LatControl(object):
  def __init__(self, CP):
    self.pid = PIController((CP.steerKpBP, CP.steerKpV),
                            (CP.steerKiBP, CP.steerKiV),
                            k_f=CP.steerKf, pos_limit=1.0)
    self.last_cloudlog_t = 0.0
    self.dampened_angle_steers = 0.
    self.angle_steers_des = 0.
    self.sat_time = 0


  def reset(self):
    self.pid.reset()

  def update(self, active, v_ego, angle_steers, angle_rate, steer_override, CP, VM, path_plan):
    if v_ego < 0.3 or not active:
      output_steer = 0.0
      self.pid.reset()
    else:
      self.angle_steers_des = interp(sec_since_boot(), path_plan.mpcTimes, path_plan.mpcAngles)
      projected_angle_steers = angle_steers + 0.5 * angle_rate
      self.dampened_angle_steers = (49. * self.dampened_angle_steers + projected_angle_steers) / 50.
      steers_max = get_steer_max(CP, v_ego)
      self.pid.pos_limit = steers_max
      self.pid.neg_limit = -steers_max
      steer_feedforward = self.angle_steers_des   # feedforward desired angle
      if CP.steerControlType == car.CarParams.SteerControlType.torque:
        steer_feedforward *= v_ego**2  # proportional to realigning tire momentum (~ lateral accel)
      deadzone = 0.0
      output_steer = self.pid.update(self.angle_steers_des, self.dampened_angle_steers, check_saturation=(v_ego > 10), override=steer_override,
                                     feedforward=steer_feedforward, speed=v_ego, deadzone=deadzone)

    # Reset sat_flat always, set it only if needed
    self.sat_flag = False

    # If PID is saturated, set time which it was saturated
    if self.pid.saturated and self.sat_time < 0.5:
      self.sat_time = sec_since_boot()

    # To save cycles, nest in sat_time check
    if self.sat_time > 0.5:
      # If its been saturated for 1.5 seconds then set flag
      if (sec_since_boot() - self.sat_time) > 0.7:
        self.sat_flag = True

      # If it is no longer saturated, clear the sat flag and timer
      if not self.pid.saturated:
        self.sat_time = 0.0

    return output_steer, float(self.angle_steers_des)
