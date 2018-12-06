import crcmod
from selfdrive.car.hyundai.values import CHECKSUM

hyundai_checksum = crcmod.mkCrcFun(0x11D, initCrc=0xFD, rev=False, xorOut=0xdf)

def make_can_msg(addr, dat, alt):
  return [addr, 0, dat, alt]

def create_lkas11(packer, car_fingerprint, apply_steer, steer_req, cnt, enabled, lkas11, hud_alert, use_stock, keep_stock=False):
  if enabled:
    use_stock = False

  values = {
    "CF_Lkas_Icon": lkas11["CF_Lkas_Icon"] if use_stock else (2 if enabled else 0),
    "CF_Lkas_LdwsSysState": lkas11["CF_Lkas_LdwsSysState"] if use_stock else (3 if steer_req else 1),
    "CF_Lkas_SysWarning": lkas11["CF_Lkas_SysWarning"] if use_stock else hud_alert,
    "CF_Lkas_LdwsLHWarning": lkas11["CF_Lkas_LdwsLHWarning"] if keep_stock else 0,
    "CF_Lkas_LdwsRHWarning": lkas11["CF_Lkas_LdwsRHWarning"] if keep_stock else 0,
    "CF_Lkas_HbaLamp": lkas11["CF_Lkas_HbaLamp"] if keep_stock else 0,
    "CF_Lkas_FcwBasReq": lkas11["CF_Lkas_FcwBasReq"] if keep_stock else 0,
    "CR_Lkas_StrToqReq": lkas11["CR_Lkas_StrToqReq"] if use_stock else apply_steer,
    "CF_Lkas_ActToi": lkas11["CF_Lkas_ActToi"] if use_stock else steer_req,
    "CF_Lkas_ToiFlt": 0,
    "CF_Lkas_HbaSysState": lkas11["CF_Lkas_HbaSysState"] if keep_stock else 1,
    "CF_Lkas_FcwOpt": lkas11["CF_Lkas_FcwOpt"] if keep_stock else 0,
    "CF_Lkas_HbaOpt": lkas11["CF_Lkas_HbaOpt"] if keep_stock else 3,
    "CF_Lkas_MsgCount": cnt,
    "CF_Lkas_FcwSysState": lkas11["CF_Lkas_FcwSysState"] if keep_stock else 0,
    "CF_Lkas_FcwCollisionWarning": lkas11["CF_Lkas_FcwCollisionWarning"] if keep_stock else 0,
    "CF_Lkas_FusionState": lkas11["CF_Lkas_FusionState"] if keep_stock else 0,
    "CF_Lkas_Chksum": 0,
    "CF_Lkas_FcwOpt_USM": lkas11["CF_Lkas_FcwOpt_USM"] if keep_stock else (2 if enabled else 1),
    "CF_Lkas_LdwsOpt_USM": lkas11["CF_Lkas_LdwsOpt_USM"] if keep_stock else 3,
    "CF_Lkas_Unknown1": lkas11["CF_Lkas_Unknown1"] if keep_stock else 0,
    "CF_Lkas_Unknown2": lkas11["CF_Lkas_Unknown2"] if keep_stock else 0,
  }

  dat = packer.make_can_msg("LKAS11", 0, values)[2]

  if car_fingerprint in CHECKSUM["crc8"]:
    # CRC Checksum as seen on 2019 Hyundai Santa Fe
    dat = dat[:6] + dat[7]
    checksum = hyundai_checksum(dat)
  elif car_fingerprint in CHECKSUM["6B"]:
    # Checksum of first 6 Bytes, as seen on 2018 Kia Sorento
    dat = [ord(i) for i in dat]
    checksum = sum(dat[:6]) % 256
  elif car_fingerprint in CHECKSUM["7B"]:
    # Checksum of first 6 Bytes and last Byte as seen on 2018 Kia Stinger
    dat = [ord(i) for i in dat]
    checksum = (sum(dat[:6]) + dat[7]) % 256

  values["CF_Lkas_Chksum"] = checksum

  return packer.make_can_msg("LKAS11", 0, values)

def create_lkas12():
  return make_can_msg(1342, "\x00\x00\x00\x00\x60\x05", 0)


def create_1191():
  return make_can_msg(1191, "\x01\x00", 0)


def create_1156():
  return make_can_msg(1156, "\x08\x20\xfe\x3f\x00\xe0\xfd\x3f", 0)

def create_clu11(packer, clu11, button):
  values = {
    "CF_Clu_CruiseSwState": button,
    "CF_Clu_CruiseSwMain": clu11["CF_Clu_CruiseSwMain"],
    "CF_Clu_SldMainSW": clu11["CF_Clu_SldMainSW"],
    "CF_Clu_ParityBit1": clu11["CF_Clu_ParityBit1"],
    "CF_Clu_VanzDecimal": clu11["CF_Clu_VanzDecimal"],
    "CF_Clu_Vanz": clu11["CF_Clu_Vanz"],
    "CF_Clu_SPEED_UNIT": clu11["CF_Clu_SPEED_UNIT"],
    "CF_Clu_DetentOut": clu11["CF_Clu_DetentOut"],
    "CF_Clu_RheostatLevel": clu11["CF_Clu_RheostatLevel"],
    "CF_Clu_CluInfo": clu11["CF_Clu_CluInfo"],
    "CF_Clu_AmpInfo": clu11["CF_Clu_AmpInfo"],
    "CF_Clu_AliveCnt1": 0,
  }

  return packer.make_can_msg("CLU11", 0, values)

def create_mdps12(packer, cnt, mdps12, lkas11, camcan):
  values = {
    "CR_Mdps_StrColTq": mdps12["CR_Mdps_StrColTq"],
    "CF_Mdps_Def": mdps12["CF_Mdps_Def"],
    "CF_Mdps_ToiActive": lkas11["CF_Lkas_ActToi"],
    "CF_Mdps_ToiUnavail": mdps12["CF_Mdps_ToiUnavail"],
    "CF_Mdps_MsgCount2": cnt,
    "CF_Mdps_Chksum2": 0,
    "CF_Mdps_ToiFlt": 0,
    "CF_Mdps_SErr": mdps12["CF_Mdps_SErr"],
    "CR_Mdps_StrTq": mdps12["CR_Mdps_StrTq"],
    "CF_Mdps_FailStat": mdps12["CF_Mdps_FailStat"],
    "CR_Mdps_OutTq": mdps12["CR_Mdps_OutTq"],
  }

  dat = packer.make_can_msg("MDPS12", camcan, values)[2]

  dat = [ord(i) for i in dat]
  checksum = (dat[0] + dat[1] + dat[2] + dat[4] + dat[5] + dat[6] + dat[7]) % 256
  values["CF_Mdps_Chksum2"] = checksum

  return packer.make_can_msg("MDPS12", camcan, values)
