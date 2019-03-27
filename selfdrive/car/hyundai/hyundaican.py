import crcmod
from selfdrive.car.hyundai.values import FEATURES

hyundai_checksum = crcmod.mkCrcFun(0x11D, initCrc=0xFD, rev=False, xorOut=0xdf)

def make_can_msg(addr, dat, alt):
  return [addr, 0, dat, alt]

def create_lkas11(packer, car_fingerprint, apply_steer, steer_req, cnt, \
        enabled, lkas11, hud_alert, use_stock, keep_stock, checksum):
  if enabled:
    use_stock = False

  if keep_stock == False:
    use_stock = False

  values = {
    "CF_Lkas_Icon": 2 if (car_fingerprint in FEATURES["icon_basic"]) else \
        (lkas11["CF_Lkas_Icon"] if use_stock else (3 if enabled else 1)),
    "CF_Lkas_LdwsSysState": lkas11["CF_Lkas_LdwsSysState"] if use_stock else \
        (3 if steer_req else 1),
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
    "CF_Lkas_LdwsOpt_USM": (3 if lkas11["CF_Lkas_LdwsOpt_USM"] == 4 else lkas11["CF_Lkas_LdwsOpt_USM"]) if keep_stock else 3,
    "CF_Lkas_Unknown1": lkas11["CF_Lkas_Unknown1"] if keep_stock else 0,
    "CF_Lkas_Unknown2": lkas11["CF_Lkas_Unknown2"] if keep_stock else 0,
  }

  dat = packer.make_can_msg("LKAS11", 0, values)[2]

  if checksum == "crc8":
    dat = dat[:6] + dat[7]
    checksumc = hyundai_checksum(dat)
  elif checksum == "6B":
    dat = [ord(i) for i in dat]
    checksumc = sum(dat[:6]) % 256
  elif checksum == "7B":
    dat = [ord(i) for i in dat]
    checksumc = (sum(dat[:6]) + dat[7]) % 256

  values["CF_Lkas_Chksum"] = checksumc

  return packer.make_can_msg("LKAS11", 0, values)

def create_clu11(packer, clu11, button, cnt):
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
    "CF_Clu_AliveCnt1": cnt,
  }

  return packer.make_can_msg("CLU11", 0, values)

def create_mdps12(packer, car_fingerprint, cnt, mdps12, lkas11, camcan, checksum):
  values = {
    "CR_Mdps_StrColTq": mdps12["CR_Mdps_StrColTq"],
    "CF_Mdps_Def": mdps12["CF_Mdps_Def"],
    "CF_Mdps_ToiActive": mdps12["CF_Mdps_ToiActive"] if (checksum == "crc8") else lkas11["CF_Lkas_ActToi"],
    "CF_Mdps_ToiUnavail": mdps12["CF_Mdps_ToiUnavail"],
    "CF_Mdps_MsgCount2": mdps12["CF_Mdps_MsgCount2"] if (checksum == "crc8") else cnt,
    "CF_Mdps_Chksum2": mdps12["CF_Mdps_Chksum2"],
    "CF_Mdps_ToiFlt": mdps12["CF_Mdps_ToiFlt"] if (checksum == "crc8") else 0,
    "CF_Mdps_SErr": mdps12["CF_Mdps_SErr"],
    "CR_Mdps_StrTq": mdps12["CR_Mdps_StrTq"],
    "CF_Mdps_FailStat": mdps12["CF_Mdps_FailStat"],
    "CR_Mdps_OutTq": mdps12["CR_Mdps_OutTq"],
  }

  if not (checksum == "crc8"):
    dat = packer.make_can_msg("MDPS12", camcan, values)[2]
    dat = [ord(i) for i in dat]
    checksum = (dat[0] + dat[1] + dat[2] + dat[4] + dat[5] + dat[6] + dat[7]) % 256
    values["CF_Mdps_Chksum2"] = checksum

  return packer.make_can_msg("MDPS12", camcan, values)

def learn_checksum(packer, lkas11):
    # Learn checksum used
    values = {
      "CF_Lkas_Icon": lkas11["CF_Lkas_Icon"],
      "CF_Lkas_LdwsSysState": lkas11["CF_Lkas_LdwsSysState"],
      "CF_Lkas_SysWarning": lkas11["CF_Lkas_SysWarning"],
      "CF_Lkas_LdwsLHWarning": lkas11["CF_Lkas_LdwsLHWarning"],
      "CF_Lkas_LdwsRHWarning": lkas11["CF_Lkas_LdwsRHWarning"],
      "CF_Lkas_HbaLamp": lkas11["CF_Lkas_HbaLamp"],
      "CF_Lkas_FcwBasReq": lkas11["CF_Lkas_FcwBasReq"],
      "CR_Lkas_StrToqReq": lkas11["CR_Lkas_StrToqReq"],
      "CF_Lkas_ActToi": lkas11["CF_Lkas_ActToi"],
      "CF_Lkas_ToiFlt": lkas11["CF_Lkas_ToiFlt"],
      "CF_Lkas_HbaSysState": lkas11["CF_Lkas_HbaSysState"],
      "CF_Lkas_FcwOpt": lkas11["CF_Lkas_FcwOpt"],
      "CF_Lkas_HbaOpt": lkas11["CF_Lkas_HbaOpt"],
      "CF_Lkas_MsgCount": lkas11["CF_Lkas_MsgCount"],
      "CF_Lkas_FcwSysState": lkas11["CF_Lkas_FcwSysState"],
      "CF_Lkas_FcwCollisionWarning": lkas11["CF_Lkas_FcwCollisionWarning"],
      "CF_Lkas_FusionState": lkas11["CF_Lkas_FusionState"],
      "CF_Lkas_Chksum": lkas11["CF_Lkas_Chksum"],
      "CF_Lkas_FcwOpt_USM": lkas11["CF_Lkas_FcwOpt_USM"],
      "CF_Lkas_LdwsOpt_USM": lkas11["CF_Lkas_LdwsOpt_USM"],
      "CF_Lkas_Unknown1": lkas11["CF_Lkas_Unknown1"],
      "CF_Lkas_Unknown2": lkas11["CF_Lkas_Unknown2"],
    }

    dat = packer.make_can_msg("LKAS11", 0, values)[2]

    # CRC Checksum
    crc = hyundai_checksum(dat[:6] + dat[7])

    dat = [ord(i) for i in dat]
    # Checksum of first 6 Bytes
    cs6b = (sum(dat[:6]) % 256)
    # Checksum of first 6 Bytes and last Byte
    cs7b = ((sum(dat[:6]) + dat[7]) % 256)

    if cs6b != crc and cs7b != crc and cs6b != cs7b:
      if crc == lkas11["CF_Lkas_Chksum"]:
        return "crc8"
      elif cs6b == lkas11["CF_Lkas_Chksum"]:
        return "6B"
      elif cs7b == lkas11["CF_Lkas_Chksum"]:
        return "7B"
      else:
        return "crc8"

    return "NONE"

def create_spas11(packer, cnt, en_spas, apply_steer, checksum):
  values = {
    "CF_Spas_Stat": en_spas,
    "CF_Spas_TestMode": 0,
    "CR_Spas_StrAngCmd": apply_steer,
    "CF_Spas_BeepAlarm": 0,
    "CF_Spas_Mode_Seq": 2,
    "CF_Spas_AliveCnt": cnt,
    "CF_Spas_Chksum": 0,
    "CF_Spas_PasVol": 0,
  }

  dat = packer.make_can_msg("SPAS11", 0, values)[2]
  if checksum == "crc8":
    dat = dat[:6]
    values["CF_Spas_Chksum"] = hyundai_checksum(dat)
  else:
    dat = [ord(i) for i in dat]
    values["CF_Spas_Chksum"] = sum(dat[:6]) % 256

  return packer.make_can_msg("SPAS11", 0, values)

def create_spas12(packer):
  values = {
    "CF_Spas_HMI_Stat": 0,
    "CF_Spas_Disp": 0,
    "CF_Spas_FIL_Ind": 0,
    "CF_Spas_FIR_Ind": 0,
    "CF_Spas_FOL_Ind": 0,
    "CF_Spas_FOR_Ind": 0,
    "CF_Spas_VolDown": 0,
    "CF_Spas_RIL_Ind": 0,
    "CF_Spas_RIR_Ind": 0,
    "CF_Spas_FLS_Alarm": 0,
    "CF_Spas_ROL_Ind": 0,
    "CF_Spas_ROR_Ind": 0,
    "CF_Spas_FCS_Alarm": 0,
    "CF_Spas_FI_Ind": 0,
    "CF_Spas_RI_Ind": 0,
    "CF_Spas_FRS_Alarm": 0,
    "CF_Spas_FR_Alarm": 0,
    "CF_Spas_RR_Alarm": 0,
    "CF_Spas_BEEP_Alarm": 0,
    "CF_Spas_StatAlarm": 0,
    "CF_Spas_RLS_Alarm": 0,
    "CF_Spas_RCS_Alarm": 0,
    "CF_Spas_RRS_Alarm": 0,
  }

  return packer.make_can_msg("SPAS12", 0, values)
