from symbtr import getTrueLyricsIdx
from structure_label import labelStructures, get_symbtr_labels

def extractAnnotatedPhrase(score, sections = [], lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    bound_codes = [51,53,54,55]

    all_bounds = [i for i, code in enumerate(score['code']) if code in bound_codes]
    if all_bounds:
        # add start and end if they are not already in the list
        if not 0 in all_bounds:
            all_bounds = [0] + all_bounds
        all_bounds = all_bounds + [len(score['code'])] # create the boundary outside the score idx

        phrase_bounds = sorted([all_bounds[i] for i in reversed(range(0, len(all_bounds)-1)) 
            if not all_bounds[i+1] - all_bounds[i] == 1]) + [len(score['code'])]
        
        # if the the last boundary is removed due to consecutive boundaries, pop the first to
        # the last and append the last
        if len(score['code'])-1 in phrase_bounds:
            phrase_bounds = ([pb for pb in phrase_bounds if not pb == len(score['code'])-1] + 
                [len(score['code'])])

        all_labels = [l for sub_list in get_symbtr_labels().values() for l in sub_list]
        real_lyrics_idx = getTrueLyricsIdx(score['lyrics'], all_labels, score['duration'])

        phrases = []
        for pp in range(0, len(phrase_bounds)-1):
            startNote_idx = phrase_bounds[pp]
            endNote_idx = phrase_bounds[pp+1]-1

            # start and endNotes
            startNote = score['index'][startNote_idx]
            endNote = score['index'][endNote_idx]

            # cesni/flavor
            flavor = [score['lyrics'][startNote_idx+i] 
                for i, code in enumerate(score['code'][startNote_idx:endNote_idx+1]) 
                if code == 54]

            # lyrics
            phrase_lyrics_idx = ([rl for rl in real_lyrics_idx 
                if rl >= startNote and rl<= endNote])
            syllables = [score['lyrics'][li] for li in phrase_lyrics_idx]
            lyrics = ''.join(syllables)

            # sections
            startSectionIdx = [i for i, sec in enumerate(sections) 
                if startNote >= sec['startNote'] and startNote <= sec['endNote']][0]
            endSectionIdx = [i for i, sec in enumerate(sections) 
                if endNote >= sec['startNote'] and endNote <= sec['endNote']][0]

            for idx, sec in zip(range(startSectionIdx,endSectionIdx+1), 
                sections[startSectionIdx:endSectionIdx+1]):

                phraseSections = [{'section_idx':idx, 'melodicStructure':
                    sec['melodicStructure'], 'lyricStructure':sec['lyricStructure']} ]

            if lyrics:
                name = u"VOCAL_SECTION"
                slug = u"VOCAL_SECTION"
            else:
                name = u"INSTRUMENTAL_SECTION"
                slug = u"INSTRUMENTAL_SECTION"

            phrases.append({'name':name, 'slug':slug,'startNote':startNote, 'endNote':endNote, 
                'lyrics':lyrics, 'sections':phraseSections, 'flavor':flavor})

        phrases = labelStructures(phrases, score, lyrics_sim_thres, melody_sim_thres)
    else:
        phrases = []

    return phrases