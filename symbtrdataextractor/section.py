from math import floor

from slugify_tr import slugify_tr
from symbtr import getTrueLyricsIdx
from structure_label import labelStructures, get_symbtr_labels
from offset import *

def extractSection(score, symbtrname, extract_all_labels=False, 
    lyrics_sim_thres=0.25, melody_sim_thres=0.25, print_warnings=True):
    all_labels = [l for sub_list in get_symbtr_labels().values() for l in sub_list] 
    struct_lbl = all_labels if extract_all_labels else get_symbtr_labels()['structure'] 

    measure_start_idx = findMeasureStartIdx(score['offset'],print_warnings=print_warnings)
    
    # Check lyrics information
    if all(l == '' for l in score['lyrics']):
        # empty lyrics field; we cannot really do anything wo symbolic analysis
        sections = []
    else:
        sections = getSections(score, struct_lbl)
        sections = locateSectionBoundaries(sections, score, all_labels, 
            measure_start_idx, print_warnings=print_warnings)

        # the refine section names according to the lyrics, pitch and durations
        sections = labelStructures(sections, score, lyrics_sim_thres,
            melody_sim_thres)

    validBool = validateSections(sections, score, set(all_labels)-set(struct_lbl), 
        symbtrname, print_warnings=print_warnings)

    # map the python indices in startNote and endNote to SymbTr index
    for se in sections:
        se['startNote'] = score['index'][se['startNote']]
        se['endNote'] = score['index'][se['endNote']]

    return sections, validBool 

def extractSectionFromXML(score):
    pass

def extractSectionFromMu2(score):
    pass

def extractSectionFromMusicBrainz(score):
    pass

def getSections(score, struct_lbl):
    sections = []
    for i, l in enumerate(score['lyrics']):
        if l in struct_lbl: # note the explicit structures
            sections.append({'name':l, 'slug':slugify_tr(l), 
                'startNote':i, 'endNote':[], 'lyrics':''})
        elif '  ' in l: # lyrics end marker
            # lyrics will be updated in locateSectionBoundaries
            sections.append({'name':u"VOCAL_SECTION", 
                'slug':u"VOCAL_SECTION",'startNote':[],'endNote':i,
                'lyrics':''})
    return sections

def locateSectionBoundaries(sections, score, struct_lbl, measure_start_idx, 
    print_warnings=True):

    real_lyrics_idx = getTrueLyricsIdx(score['lyrics'], struct_lbl, score['duration'])

    startNoteIdx = [s['startNote'] for s in sections] + [len(score['lyrics'])]
    endNoteIdx = [-1] + [s['endNote'] for s in sections]
    for se in reversed(sections): # start from the last section
        if se['slug'] == u'VOCAL_SECTION':
            # carry the 'endNote' to the next closest start
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['endNote']) - 1
            
            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

            # estimate the start of the lyrics sections
            try: # find the previous closest start
                prevClosestStartInd = max(x for x in startNoteIdx 
                    if x < se['endNote'])
            except ValueError: # no section label in lyrics columns
                prevClosestStartInd = -1

            try: # find the previous closest end
                prevClosestEndInd = max(x for x in endNoteIdx 
                    if x < se['endNote'])
            except ValueError: # no vocal sections
                prevClosestEndInd = -1

            # find where the lyrics of this section starts
            chkInd = max([prevClosestEndInd, prevClosestStartInd])
            nextLyricsStartInd = min(x for x in real_lyrics_idx if x > chkInd)
            nextLyricsMeasureOffset = floor(score['offset'][nextLyricsStartInd])

            # check if nextLyricsStartInd and prevClosestEndInd are in the 
            # same measure. Ideally they should be in different measures
            if (nextLyricsMeasureOffset == 
                floor(score['offset'][prevClosestEndInd])):
                if print_warnings:
                    print ("    " + str(nextLyricsMeasureOffset) + ':'
                        ' ' + score['lyrics'][prevClosestEndInd] + ' and' 
                        ' ' + score['lyrics'][nextLyricsStartInd] + ' '
                        'are in the same measure!')

                se['startNote'] = nextLyricsStartInd
            else: # The section starts on the first measure the lyrics start
                se['startNote'] = getMeasureOffsetId(nextLyricsMeasureOffset, 
                    score['offset'], measure_start_idx)

            # update startNoteIdx
            startNoteIdx = ([s['startNote'] for s in sections] + 
                [len(score['lyrics'])])

            # update lyrics
            section_lyrics_idx = ([rl for rl in real_lyrics_idx 
                if rl >= se['startNote'] and rl<= se['endNote']])
            syllables = [score['lyrics'][li] for li in section_lyrics_idx]
            se['lyrics'] = ''.join(syllables)
        else:  # instrumental
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['startNote']) - 1

            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

    # if the second note is not the startNote of a section
    # add an initial instrumental section
    # note starting from SymbTr 2.4, the first row always indicates the usul
    firstnoteidx = 1 if score['code'][0] in range(50,57) else 0
    if sections and not any(s['startNote'] == firstnoteidx for s in sections):
        sections.append({'name': u'INSTRUMENTAL_SECTION',
            'slug':u'INSTRUMENTAL_SECTION', 'startNote': 0, 
            'endNote': min([s['startNote'] for s in sections])-1})
    return sortSections(sections)

def sortSections(sections):
    # sort the sections
    sortIdx = [i[0] for i in sorted(enumerate([s['startNote'] 
        for s in sections]),  key=lambda x:x[1])]
    return [sections[s] for s in sortIdx]

def validateSections(sections, score, ignoreLabels, symbtrname, print_warnings=True):
    validBool = True  # treat some of these are warning; they'll be made stricter later
    if not sections: # check section presence
        if print_warnings:
            print symbtrname + ", Missing section info in lyrics."
    else: # check section continuity
        ends = [-1] + [s['endNote'] for s in sections]
        starts = [s['startNote'] for s in sections] + [len(score['offset'])]
        for s, e in zip(starts, ends):
            if not s - e == 1:
                print(symbtrname + ", " + str(e) + '->' + str(s) + ', '
                    'Gap between the sections')
                validBool = False

    for s in sections:
        # check whether section starts on the measure or not
        if (not isIntegerOffset(score['offset'][s['startNote']]) and 
            s['slug'] not in ignoreLabels) and print_warnings:
            print(symbtrname + ", " + str(s['startNote']) + ', ' + s['slug'] + ' '
                'does not start on a measure: ' + 
                str(score['offset'][s['startNote']]))
        # check if the end of a section somehow got earlier than its start
        if s['startNote'] > s['endNote']:
            print(symbtrname + ", " + str(s['startNote']) + '->'
                '' + str(s['endNote']) + ', ' + s['slug'] + ' '
                'ends before it starts: ' + 
                str(score['offset'][s['startNote']]))
            validBool = False

    # check if there are any structure labels with a space, e.g. it is not found
    all_labels = [l for sub_list in get_symbtr_labels().values() for l in sub_list] + ['.']
    for i, ll in enumerate(score['lyrics']):
        for label in all_labels:
            if (label + ' ') == ll or (label + '  ') == ll:  # invalid lyrics end 
                print symbtrname + ', ' + str(i) + ": Extra space in " + ll
                validBool = False

    return validBool