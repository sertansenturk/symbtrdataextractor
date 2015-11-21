from symbtr import getTrueLyricsIdx
from structure_label import labelStructures, get_symbtr_labels

def extractAnnotatedPhrase(score, sections = [], lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    bound_codes = [51,53,54,55]
    anno_codes = [53,54,55]

    all_bounds = [i for i, code in enumerate(score['code']) if code in bound_codes]
    anno_bounds = [i for i, code in enumerate(score['code']) if code in anno_codes]
    if anno_bounds:
        phrases = extractPhrases(all_bounds, score, sections = sections, lyrics_sim_thres = 0.25, 
            melody_sim_thres = 0.25)
    else:
        phrases = []

    return phrases

def extractAutoSegPhrase(score, autoSegBounds, sections = [], lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    # Boundaries start from 1, convert them to python indexing (0) by subtracting 1
    autoSegBound_idx = [a-1 for a in autoSegBounds]

    if autoSegBound_idx:
        phrases = extractPhrases(autoSegBound_idx, score, sections = sections, lyrics_sim_thres = 0.25, 
            melody_sim_thres = 0.25)
    else:
        phrases = []

    return phrases

def extractPhrases(bounds, score, sections = [], lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    # add start and end if they are not already in the list
    if not 0 in bounds:
        bounds = [0] + bounds
    bounds = bounds + [len(score['code'])] # create the boundary outside the score idx
    
    # remove consecutive boundaries
    phrase_bounds = sorted([bounds[i] for i in reversed(range(0, len(bounds)-1)) 
        if not bounds[i+1] - bounds[i] == 1]) + [len(score['code'])]
    
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
        if sections:
            startSectionIdx = [i for i, sec in enumerate(sections) 
                if startNote >= sec['startNote'] and startNote <= sec['endNote']][0]
            endSectionIdx = [i for i, sec in enumerate(sections) 
                if endNote >= sec['startNote'] and endNote <= sec['endNote']][0]

            for idx, sec in zip(range(startSectionIdx,endSectionIdx+1), 
                sections[startSectionIdx:endSectionIdx+1]):

                phraseSections = [{'section_idx':idx, 'melodicStructure':
                    sec['melodicStructure'], 'lyricStructure':sec['lyricStructure']} ]
        else:
            phraseSections = []

        if lyrics:
            name = u"VOCAL_PHRASE"
            slug = u"VOCAL_PHRASE"
        else:
            name = u"INSTRUMENTAL_PHRASE"
            slug = u"INSTRUMENTAL_PHRASE"

        phrases.append({'name':name, 'slug':slug,'startNote':startNote, 'endNote':endNote, 
            'lyrics':lyrics, 'sections':phraseSections, 'flavor':flavor})

    return labelStructures(phrases, score, lyrics_sim_thres, melody_sim_thres)
