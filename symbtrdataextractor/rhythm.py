from metadata import getAttributeDict
import copy 

def extractRhythmicStructure(score):
	usul_bounds = [ii for ii, code in enumerate(score['code']) if code == 51]
	usul_dict = getAttributeDict('usul')

		
	rhythmic_structure = []
	for ii, ub in enumerate(usul_bounds):
		start = score['index'][ub]
		if ii < len(usul_bounds)-1:
			end = score['index'][usul_bounds[ii+1]-1]
		else:  # end of file
			end = score['index'][len(score['code'])-1]

		key_set = False
		for uk, dd in usul_dict.iteritems():
			if key_set:
				break
			for var in dd['variants']:
				if score['lyrics'][ub] == var['mu2_name']:
					usul_key = uk
					key_set = True

		usul = {'attribute_key':usul_key, 'mu2_name':score['lyrics'][ub], 
				'mertebe':score['denumerator'][ub],
				'number_of_pulses':score['numerator'][ub],
				'symbtr_internal_id':score['lns'][ub]}

		# compute the tempo from the next note
		tempo = []
		if usul['mu2_name'] == '(Serbest)':
			pass  # no tempo for non-metered score
		else:
			it = ub
			while not tempo:
				it += 1
				if score['code'][it] == 9:  # proper note
					tempo = computeTempoFromNote(score['numerator'][it], 
						score['denumerator'][it], score['duration'][it], 
						usul['mertebe'])

		rhythmic_structure.append({'usul':usul, 'tempo':{'value':tempo, 'unit':'bpm'}, 
			'startNote':start, 'endNote':end})

	return rhythmic_structure

def computeTempoFromNote(note_num, note_denum, note_dur, mertebe):
	sym_dur = float(note_num)/note_denum
	rel_dur_wrt_mertebe = mertebe * sym_dur * 0.001

	tempo = int(round(60.0 / (note_dur * rel_dur_wrt_mertebe)))
	
	return tempo