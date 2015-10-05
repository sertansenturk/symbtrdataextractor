import os
import json
from math import floor

from slugify_tr import slugify_tr
from symbtr import getTrueLyricsIdx
from structure_labeler import labelSections, get_symbtr_labels
from offset import *

import pdb

def extractSection(score, slugify = True, extractAllLabels=False, 
    lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    all_labels = [l for sub_list in get_symbtr_labels().values() for l in sub_list] 
    struct_lbl = all_labels if extractAllLabels else get_symbtr_labels()['structure'] 

    measure_start_idx = findMeasureStartIdx(score['offset'])
    
    sections = []
    # Check lyrics information
    if all(l == '' for l in score['lyrics']):
        # empty lyrics field; we cannot really do anything wo symbolic analysis
        sections = []
    else:
        sections = getSections(score, struct_lbl, slugify=slugify)
        sections = locateSectionBoundaries(sections, score, all_labels, 
            measure_start_idx)

        # the refine section names according to the lyrics, pitch and durations
        sections = labelSections(sections, score, lyrics_sim_thres,
            melody_sim_thres)

    validateSections(sections, score, measure_start_idx, 
        set(all_labels)- set(struct_lbl))

    # map the python indices in startNote and endNote to SymbTr index
    for se in sections:
        se['startNote'] = score['index'][se['startNote']]
        se['endNote'] = score['index'][se['endNote']]

    return sections

def extractSectionFromXML(score, slugify = True):
    pass

def extractSectionFromMu2(score, slugify = True):
    pass

def extractSectionFromMusicBrainz(score, slugify = True):
    pass

def getSections(score, struct_lbl, slugify=True):
    sections = []
    for i, l in enumerate(score['lyrics']):
        if l in struct_lbl: # note the explicit structures
            sections.append({'name':slugify_tr(l) if slugify else l, 
                'startNote':i, 'endNote':[]})
        elif '  ' in l: # lyrics end marker
            sections.append({'name':"LYRICS_SECTION", 'startNote':[], 
                'endNote':i})
    return sections

def locateSectionBoundaries(sections, score, struct_lbl, measure_start_idx):
    real_lyrics_idx = getTrueLyricsIdx(score['lyrics'], struct_lbl, score['duration'])

    startNoteIdx = [s['startNote'] for s in sections] + [len(score['lyrics'])]
    endNoteIdx = [-1] + [s['endNote'] for s in sections]
    for se in reversed(sections): # start from the last section
        #print se['name'] + ' ' + str(se['startNote']) + ' ' + str(se['endNote'])

        if se['name'] == 'LYRICS_SECTION':
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
            if nextLyricsMeasureOffset == floor(score['offset'][prevClosestEndInd]):
                print ("    " + str(nextLyricsMeasureOffset) + ':'
                ' ' + score['lyrics'][prevClosestEndInd] + ' and' 
                ' ' + score['lyrics'][nextLyricsStartInd] + ' '
                'are in the same measure!')

                se['startNote'] = nextLyricsStartInd
            else: # The section starts on the first measure the lyrics start
                pdb.set_trace()
                se['startNote'] = getMeasureOffsetId(nextLyricsMeasureOffset, 
                    score['offset'], measure_start_idx)

            # update startNoteIdx
            startNoteIdx = ([s['startNote'] for s in sections] + 
                [len(score['lyrics'])])
        else:  # instrumental
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['startNote']) - 1

            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

    # if the first note is not the startNote of a section
    # add an initial instrumental section
    if sections and not any(s['startNote'] == 0 for s in sections):
        sections.append({'name': 'INSTRUMENTAL_SECTION','startNote': 0, 
            'endNote': min([s['startNote'] for s in sections])-1})

        #print(' ' + se['name'] + ' ' + str(se['startNote']) + ' '
        #    '' + str(se['endNote']))
    return sortSections(sections)

def sortSections(sections):
    # sort the sections
    sortIdx = [i[0] for i in sorted(enumerate([s['startNote'] 
        for s in sections]),  key=lambda x:x[1])]
    return [sections[s] for s in sortIdx]

def validateSections(sections, score, masdeasure_start_idx, ignoreLabels):
    if not sections: # check section presence
        print "    Missing section info in lyrics."
    else: # check section continuity
        ends = [-1] + [s['endNote'] for s in sections]
        starts = [s['startNote'] for s in sections] + [len(score['offset'])]
        for s, e in zip(starts, ends):
            if not s - e == 1:
                print("    " + str(e) + '->' + str(s) + ', '
                    'Gap between the sections')

    for s in sections:
        # check whether section starts on the measure or not
        if (not isIntegerOffset(score['offset'][s['startNote']]) and 
            s['name'] not in ignoreLabels):
            print("    " + str(s['startNote']) + ', ' + s['name'] + ' '
                'does not start on a measure: ' + 
                str(score['offset'][s['startNote']]))
        # check if the end of a section somehow got earlier than its start
        if s['startNote'] > s['endNote']:
            print("    " + str(s['startNote']) + '->'
                '' + str(s['endNote']) + ', ' + s['name'] + ' '
                'ends before it starts: ' + 
                str(score['offset'][s['startNote']]))
