# Quick and dirty tool to print the real-time tuning data from the command line
#  Will only work once controlsd has had a chance to write the real-time tuning carparams the first time.
#
# v0.02  James-T1:   Pretty(er) print format
# v0.01  James-T1:   Initial code

import pickle

rt_tuning_file = '/data/.openpilot_rtt_params.pkl'

with open(rt_tuning_file, "rb") as f_read:
	rtt_params = pickle.load(f_read)

print('')
print(rtt_params)
print('')

# Get the maximum key length
#max_len = 0
#for key in rtt_params.keys():
#	if len(key) > max_len:
#		max_len = len(key)

# Print the tuning values in a pretty format
for key in sorted(rtt_params.keys()):
	print('{0:<22}:  {1}'.format(key, rtt_params[key]))
	# TODO:  print the various sized floats, lists, lists of floats, etc differently so they are more human readable and can be directy pasted into the tuning files.
print('')
