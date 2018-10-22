# Quick and dirty tool to print the real-time tuning data from the command line
#  Will only work once controlsd has had a chance to write the real-time tuning carparams the first time.
#
# v0.01  James-T1:   Initial code

import pickle

rt_tuning_file = '/data/.openpilot_rtt_params.pkl'

with open(rt_tuning_file, "rb") as f_read:
	rtt_params = pickle.load(f_read)

print(rtt_params)