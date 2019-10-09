import os
import json
import time


def write_config(params_file, params):
  with open(params_file, "w") as f:
    json.dump(params, f, indent=2, sort_keys=True)
  os.chmod(params_file, 0o764)

class opParams:
  def __init__(self):
    self.params_file = "/data/op_params.json"
    self.kegman_file = "/data/kegman.json"
    self.params = {}
    self.last_read_time = time.time()
    self.default_params = {'cameraOffset': 0.06, 'wheelTouchFactor': 10, 'speed_offset': 0, 'osm': True}
    self.run_init()  # restores, reads, and updates params

  def add_default_params(self, force_update=False):
    for i in self.default_params:
      if force_update:
        self.params.update({i: self.default_params[i]})
      elif i not in self.params:
        self.params.update({i: self.default_params[i]})

  def run_init(self):  # does first time initializing of default params, and/or restoring from kegman.json
    force_update = False  # replaces values with default params if True, not just add add missing key/value pairs
    if os.path.isfile(self.params_file):
      if not self.read_params() == 'used_default':  # don't overwrite corrupted params, just print to screen
        self.add_default_params(force_update=force_update)  # always update missing defaults
        write_config(self.params_file, self.params)
      else:
        print('ERROR: Can\'t read params file')
    elif os.path.isfile(self.kegman_file):
      try:
        with open(self.kegman_file, "r") as f:
          self.params = json.load(f)
      except:
        self.params = self.default_params
        write_config(self.params_file, self.params)
        return
      self.add_default_params()
      write_config(self.params_file, self.params)  # if op_params.json doesn't exist, but kegman.json does, restore and update defaults

  def read_params(self):
    try:
      with open(self.params_file, "r") as f:
        self.params = json.load(f)
        return True
    except:
      self.params = self.default_params
      return 'used_default'

  def put(self, key, value):
    self.params.update({key: value})
    write_config(self.params_file, self.params)

  def get(self, key=None, default=None):  # can specify a default value if key doesn't exist
    if time.time() - self.last_read_time >= 0.5:  # make sure we aren't reading file too often
      self.read_params()
      self.last_read_time = time.time()
    if key is None:  # get all
      return self.params
    else:
      return self.params[key] if key in self.params else default
