# Quick and dirty real-time tuning interface from the command-line
#  Will only work once controlsd has had a chance to write the real-time tuning carparams the first time.
#
# v0.01  James-T1:   Initial code

import pickle
import sys

def isDigit(x):
	try:
		float(x)
		return True
	except (ValueError, TypeError) as e:
		return False

rt_tuning_file = '/data/.openpilot_rtt_params.pkl'

# Loop forever (ctrl-C and then Enter key to end script)
while 1:
	with open(rt_tuning_file, "rb") as f_read:
		rtt_params = pickle.load(f_read)

	key_list = []

	print('')
	cnt = 0
	for key in sorted(rtt_params.keys()):
		print('{0}:  {1}'.format(cnt, key))
		key_list.append(key)
		cnt += 1

	print('')
	sys.stdin = open('/dev/tty')
	entry = raw_input('Enter parameter number to modify:  ')

	# Data checking
	try: 
		int(entry)
	except ValueError:
		print ('Please re-enter a valid parameter number.')
		continue
	param_num = int(entry)
	if param_num < 0 or param_num >= len(key_list):
		print('Please re-enter a valid parameter number.')
		continue

	print('')
	print('Old value:')
	key = key_list[param_num]
	original_param_is_list = False
	if isDigit(rtt_params[key]):
		print('  {0}:  {1:.6f}'.format(key, rtt_params[key]))
	else:
		print('  {0}:  {1}'.format(key, rtt_params[key]))
		original_param_is_list = True
	print('')
	entry = raw_input('Enter new value:  ')
	print('')
	#print(entry)
	# Check to see if a list was entered...  basically anything with a comma.
	if ',' in entry or ('[' in entry and ']' in entry):
		if not original_param_is_list:
			print('Original value was float, new value entered is a list.  Try again.')
			print('')
			continue
		entry = entry.replace('[','').replace(']','')
		processed_entry = [float(s) for s in entry.split(',') if isDigit(s)]
		if len(processed_entry) == 0:
			print('Invalid list entry.  Try again.')
			print('')
			continue			
		if len(processed_entry) != len(rtt_params[key]):
			print('New list length does not match length of original list.  Try again.')
			print('')
			continue		
	elif isDigit(entry):
		if original_param_is_list:
			print('Original value was list, new value entered is a float.  Try again.')
			print('')
			continue			
		processed_entry = float(entry)
	else:
		print('Invalid value entered.  Try again.')
		print('')
		continue

	print('New value:')
	if isDigit(processed_entry):
		print('  {0}:  {1:.6f}'.format(key, processed_entry))
	else:
		# must be a list.
		print('  {0}:  {1}'.format(key, processed_entry))

	print('')
	confirm = raw_input('Type "y" to confirm + save or any other key to escape:  ')
	if confirm.lower() == 'y':
		print('Confirmed.  Writing to real-time tuning file.')
		print('')
		# Set it to this value
		rtt_params[key] = processed_entry
		# Save the file
		with open(rt_tuning_file, "wb") as f_write:
			pickle.dump(rtt_params, f_write, -1)    # Dump to file with highest protocol (fastest)
	else:
		print('Escaped!')
		print('')


