
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
    // camera connected, disable forwarding
    enabled = 0;
    safety_cb_disable_all();
    }

}

static int forward_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  int addr = GET_ADDR(to_send);
  if (enabled == 1) {
    if (addr == 593) {
      if (MDPS12_cnt > 330) {
        uint8_t dat[8];
        for (int i=0; i<8; i++) {
          dat[i] = GET_BYTE(to_send, i);
        }
        int StrColTq = dat[0] | (dat[1] & 0x7) << 8;
	//int Chksum2 = dat[3];
        int New_Chksum2 = 0;
	int OutTq = dat[6] >> 4 | dat[7] << 4;
	if (MDPS12_cnt == 331) {
	  StrColTq -= 164;
	  OutTq = 2058;
	  last_StrColT = StrColTq;
	}
	else {
	  StrColTq = last_StrColT + 34;
	  OutTq = 2058;
	  last_StrColT = StrColTq;
	}
	dat[0] = StrColTq & 0xFF;
	dat[1] &= 0xF8;
	dat[1] |= StrColTq >> 8;
	dat[3] = 0;
	dat[6] &= 0xF;
	dat[6] |= (OutTq & 0xF) << 4;
	dat[7] = OutTq >> 4;
        for (int i=0; i<8; i++) {
          New_Chksum2 += dat[i];
	}
	New_Chksum2 %= 256;
        to_send->RDLR &= 0xFFF800;
        to_send->RDLR |= StrColTq | New_Chksum2 << 24;
        to_send->RDHR &= 0xFFFFF;
        to_send->RDHR |= OutTq << 20;
        }
        MDPS12_cnt += 1;
        if (MDPS12_cnt > 344) {
          MDPS12_cnt = 0;
     }
  }
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
