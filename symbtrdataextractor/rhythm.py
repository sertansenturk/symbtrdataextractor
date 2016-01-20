from metadata import getAttributeDict
import copy 

def extractRhythmicStructure(score):
	usul_bounds = [ii for ii, code in enumerate(score['code']) if code == 51]

	rhythmic_structure = []
	for ii, ub in enumerate(usul_bounds):
		start = ub
		if ii < len(usul_bounds)-1:
			end = usul_bounds[ii+1]  
		else:  # end of file
			end = len(score['code'])

		usul = {'mu2_name':score['lyrics'][ii],'mertebe':score['denumerator'][ii],
				'number_of_pulses':score['numerator'][ii], 'symbtr_internal':score['lns'][ii]}

		# compute the tempo from the next note
		tempo = []
		it = ii+1
		while not tempo:
			if score['code'][it] == 9:  # proper note
				tempo = computeTempoFromNote(score['numerator'][it], score['denumerator'][it], 
					score['duration'][it],usul['mertebe'])
			else:
				it += 1

		rhythmic_structure.append({'usul':usul, 'tempo':tempo, 
			'start_note':start, 'end_note':end})

	return rhythmic_structure

def computeTempoFromNote(note_num, note_denum, note_dur, mertebe):
	sym_dur = float(note_num)/note_denum
	rel_dur_wrt_mertebe = mertebe * sym_dur * 0.001
	tempo = int(round(60.0 / (note_dur * rel_dur_wrt_mertebe)))
	
	return tempo