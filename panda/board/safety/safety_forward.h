
// Stores the array index of a matched car fingerprint/forwarding profile
int enabled = -1;


static void forward_rx_hook(CAN_FIFOMailBox_TypeDef *to_push) {

  int bus = GET_BUS(to_push);
  int addr = GET_ADDR(to_push);
  
  if ((bus == 0) && (addr == 832)) {
    hyundai_camera_detected = 1;
  }
  
  // Find out which bus the camera is on
  if ((bus != 0) && (addr == 832)) {
    hyundai_camera_bus = bus;
  }
  
  // 832 is lkas cmd. If it is on camera bus, then giraffe switch 2 is high
  if ((addr == 832) && (bus == hyundai_camera_bus) && (hyundai_camera_detected != 1)) {
    hyundai_giraffe_switch_2 = 1;
  }
  if ((enabled != 1) && (hyundai_camera_detected != 1) && (hyundai_giraffe_switch_2 == 1)) {
    safety_cb_enable_all();
    // begin forwarding with that profile
    enabled = 1;
    }
  if ((enabled == 1) && (hyundai_camera_detected == 1)) {
    safety_cb_disable_all();
    // camera connected, disable forwarding
    enabled = 0;
    }

}

static int forward_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  UNUSED(to_send);
  if (enabled == 1) {
      // must be true for fwd_hook to function
      return 1;
  }
  return 0;
}

static int forward_fwd_hook(int bus_num, CAN_FIFOMailBox_TypeDef *to_fwd) {
  UNUSED(to_fwd);
  int bus_fwd = -1;
  if (enabled == 1) {
    if (bus_num == 0) {
      bus_fwd = hyundai_camera_bus;
    }
    if (bus_num == hyundai_camera_bus) {
      bus_fwd = 0;
    }
  }
  return bus_fwd;
}

static void forward_init(int16_t param) {
  UNUSED(param);
  controls_allowed = 0;
}

const safety_hooks forward_hooks = {
  .init = forward_init,
  .rx = forward_rx_hook,
  .tx = forward_tx_hook,
  .tx_lin = nooutput_tx_lin_hook,
  .ignition = default_ign_hook,
  .fwd = forward_fwd_hook,
};
