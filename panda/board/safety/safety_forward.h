// Candidate Car Fingerprints
//  fingerprint format:  [[bus#, addr, len], ...]
//  all fingerprints must be matched before forwarding will occur.
//  do not use addresses above 2047 if you want it to ever match.
uint16_t candidate_fp[2][20][3] = { 
  // Hyundai new Giraffe (camera = bus2)
  { {2,832,8}, {0,339,8},{0,356,4},{0,593,8},{0,608,8},{0,809,8},{0,897,8},{0,902,8},{0,916,8},{0,1056,8},{0,1057,8},{0,1078,4},{0,1170,8},{0,1265,4},{0,1312,8},{0,1345,8},{0,1419,8} },
  // Hyundai old Giraffe (camera = bus1)
  { {1,832,8}, {0,339,8},{0,356,4},{0,593,8},{0,608,8},{0,809,8},{0,897,8},{0,902,8},{0,916,8},{0,1056,8},{0,1057,8},{0,1078,4},{0,1170,8},{0,1265,4},{0,1312,8},{0,1345,8},{0,1419,8} }
};

// Candidate Car Forwarding Profiles
//  forwarding format:   [bus0to, bus1to, bus2to]
//    array[bus#] = bus# to forward message to (or -1 for no forwarding)
//  the order of the forwarding profiles must match the candidate_fp order above.
int forward_profile[2][3] = { 
  // Hyundai new Giraffe (camera = bus2)
  {  2, -1,  0 },
  // Hyundai old Giraffe (camera = bus1)
  {  1,  0, -1 }
};

// Stores the array index of a matched car fingerprint/forwarding profile
int identified_car = -1;


static void forward_rx_hook(CAN_FIFOMailBox_TypeDef *to_push) {

  // skip everything if we've already completed fingerprinting 
  //   can be extended in the future for fancier forwarding rules based on specific car id
  if (identified_car >= 0) {
    return;
  }

  // temporarily store our bus number, address, and data length
  uint16_t msg_metadata[3];

  // store the bus number
  msg_metadata[0] = (uint32_t)0x000000FF & (to_push->RDTR >> 4);
  // get the can message info needed for fingerprinting
  if (to_push->RIR & 4) {
    // Extended addresses
    // Not looked at, but have to be separated to avoid address collision
    return;
  } else {
    // store the normal address
    msg_metadata[1] = (uint32_t)0x000007FF & (to_push->RIR >> 21);
  }
  // store the length
  msg_metadata[2] = (uint32_t)0x0000000F & (to_push->RDTR);

  // iterate over all candidate fingerprints
  for (int i = 0; i < (sizeof(candidate_fp) / sizeof(candidate_fp[0])); i++) {
    bool matched = true;
    // iterate over all fingers in this fingerprint
    for (int j = 0; j < (sizeof(candidate_fp[i]) / sizeof(candidate_fp[i][0])); j++) {
      // search for a match
      if ( memcmp(candidate_fp[i][j], msg_metadata, sizeof(uint16_t)*3) == 0) {
        // we matched the candidate finger, so "remove" it's address from the fingerprint array
        candidate_fp[i][j][1] = (uint16_t) 0;
      // if any array addr isn't zero in this fingerprint, then we haven't completely matched this car
      } else if (candidate_fp[i][j][1] != (uint16_t) 0) {
        matched = false;
      }
    }
    if (matched) {
      // re-init can to allow sending messages
      safety_cb_enable_all();
      // we found an exact match, begin forwarding with that profile
      identified_car = i;
      break;
    }
  }
}

static int forward_tx_hook(CAN_FIFOMailBox_TypeDef *to_send) {
  if (identified_car >= 0) {
      // must be true for fwd_hook to function
      return true;
  }
  return false;
}

static int forward_fwd_hook(int bus_num, CAN_FIFOMailBox_TypeDef *to_fwd) {
  // can be extended in the future for fancier forwarding based on specific id
  if (identified_car >= 0) {
      // Hopefully you put valid bus numbers in the forwarding profiles!
      return forward_profile[identified_car][bus_num];
  }
  return -1;
}

static void forward_init(int16_t param) {
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

