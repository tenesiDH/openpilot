
// Stores the array index of a matched car fingerprint/forwarding profile
int enabled = 1;
int camera_detected = -1;
int camera_bus = -1;
int giraffe_switch_2 = -1;

void default_rx_hook(CAN_FIFOMailBox_TypeDef *to_push) {

  int bus = GET_BUS(to_push);
  int addr = GET_ADDR(to_push);
  
  if ((bus == 0) && (addr == 832)) {
    camera_detected = 1;
  }
  
  // Find out which bus the camera is on
  if ((bus != 0) && (addr == 832)) {
    camera_bus = bus;
  }
  
  // 832 is lkas cmd. If it is on camera bus, then giraffe switch 2 is high
  if ((addr == 832) && (bus == camera_bus) && (camera_detected != 1)) {
    giraffe_switch_2 = 1;
  }
  if ((enabled == 1) && (camera_detected == 1)) {
    // camera connected, disable forwarding
    enabled = 0;
    safety_cb_disable_all();
    }

}

int default_ign_hook(void) {
  return -1; // use GPIO to determine ignition
}

// *** no output safety mode ***

static void nooutput_init(int16_t param) {
  UNUSED(param);
  controls_allowed = 0;
}

static int nooutput_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  UNUSED(to_send);
  return 1;
}

static int nooutput_tx_lin_hook(int lin_num, uint8_t *data, int len) {
  UNUSED(lin_num);
  UNUSED(data);
  UNUSED(len);
  return false;
}

static int default_fwd_hook(int bus_num, CAN_FIFOMailBox_TypeDef *to_fwd) {
  UNUSED(to_fwd);
  int bus_fwd = -1;
  if (enabled == 1) {
    if (bus_num == 0) {
      bus_fwd = camera_bus + 10;
    }
    if (bus_num == camera_bus) {
      bus_fwd = 0 + 10;
    }
  }
  if (bus_num == 1) {
    bus_fwd = 0 + 20;
  }
  return bus_fwd;
}

const safety_hooks nooutput_hooks = {
  .init = nooutput_init,
  .rx = default_rx_hook,
  .tx = nooutput_tx_hook,
  .tx_lin = nooutput_tx_lin_hook,
  .ignition = default_ign_hook,
  .fwd = default_fwd_hook,
};

// *** all output safety mode ***

static void alloutput_init(int16_t param) {
  UNUSED(param);
  controls_allowed = 1;
}

static int alloutput_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  UNUSED(to_send);
  return true;
}

static int alloutput_tx_lin_hook(int lin_num, uint8_t *data, int len) {
  UNUSED(lin_num);
  UNUSED(data);
  UNUSED(len);
  return true;
}

const safety_hooks alloutput_hooks = {
  .init = alloutput_init,
  .rx = default_rx_hook,
  .tx = alloutput_tx_hook,
  .tx_lin = alloutput_tx_lin_hook,
  .ignition = default_ign_hook,
  .fwd = default_fwd_hook,
};
