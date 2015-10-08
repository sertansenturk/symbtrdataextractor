import os 
import json
from numpy import matrix
import string

from symbtr import getTrueLyricsIdx, synthMelody, mel2str
from section_graph import normalizedLevenshtein, getCliques

def get_symbtr_labels(): 
    symbtr_label_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'symbTrLabels.json')
    symbtr_label = json.load(open(symbtr_label_file, 'r'))

    return symbtr_label

def labelSections(sections, score, lyrics_sim_thres, 
    melody_sim_thres):
    # get the duration, pitch and lyrics related to the section
    scoreFragments = []
    for s in sections:
        durs = score['duration'][s['startNote']:s['endNote']+1]
        nums = score['numerator'][s['startNote']:s['endNote']+1]
        denums = score['denumerator'][s['startNote']:s['endNote']+1]
        notes = score['comma'][s['startNote']:s['endNote']+1]
        lyrics = score['lyrics'][s['startNote']:s['endNote']+1]

        scoreFragments.append({'durs':durs, 'nums': nums, 
            'denums':denums, 'notes':notes, 'lyrics':lyrics})

    # get the lyric organization
    sections = getLyricOrganization(sections, scoreFragments, 
        lyrics_sim_thres)

    # get the melodic organization
    section = getMelodicOrganization(sections, scoreFragments, 
        melody_sim_thres)

    return sections

def getLyricOrganization(sections, scoreFragments, lyrics_sim_thres):
    # Here we only check whether the lyrics are similar to others
    # We don't check whether they are sung on the same note / with 
    # the same duration, or not. As a results, two sections having
    # exactly the same melody but different sylallable onset/offsets
    # would be considered the same. Nevertheless this situation 
    # would occur in very rare occasions.
    # From the point of view of an audio-score alignment algorithm 
    # using only melody, this function does not give any extra info
    # This part is done for future needs; e.g. audio-lyrics alignment

    if sections:
        # get the lyrics stripped of section information
        all_labels = [l for sub_list in get_symbtr_labels().values() for l in sub_list] 
        all_labels += ['.', '', ' ']
        for sf in scoreFragments:
            real_lyrics_idx = getTrueLyricsIdx(sf['lyrics'], all_labels, 
                sf['durs'])
            sf['lyrics'] = u''.join([sf['lyrics'][i].replace(u' ',u'') 
                for i in real_lyrics_idx])
         
        dists = matrix([[normalizedLevenshtein(a['lyrics'],b['lyrics'])
            for a in scoreFragments] for b in scoreFragments])

        cliques = getCliques(dists, lyrics_sim_thres)

        lyrics_labels = semiotize(cliques)

        # label the insrumental sections, if present
        for i in range(0, len(lyrics_labels)):
            if not scoreFragments[i]['lyrics']:
                sections[i]['lyricStructure'] = 'INSTRUMENTAL'
            else:
                sections[i]['lyricStructure'] = lyrics_labels[i]

        # sanity check
        lyrics = [sc['lyrics'] for sc in scoreFragments]
        for lbl, lyr in zip(lyrics_labels, lyrics):
            chk_lyr = ([lyrics[i] for i, x in enumerate(lyrics_labels) 
                if x == lbl])
            if not all(lyr == cl for cl in chk_lyr):
                print '   Mismatch in lyrics_label: ' + lbl        
    else:  # no section information
        sections = []

    return sections

def getMelodicOrganization(sections, scoreFragments, melody_sim_thres):
    if sections:
        # remove annotation/control row; i.e. entries w 0 duration
        for sf in scoreFragments:
            for i in reversed(range(0, len(sf['durs']))):
                if sf['durs'][i] == 0:
                    sf['notes'].pop(i)
                    sf['nums'].pop(i)
                    sf['denums'].pop(i)
                    sf['durs'].pop(i)

        # synthesize the score according taking the shortest note as the unit
        # shortest note has the greatest denumerator
        max_denum = max(max(sf['denums']) for sf in scoreFragments)
        melodies = [synthMelody(sf, max_denum) for sf in scoreFragments]
        
        # convert the numbers in melodies to unique strings for Levenstein
        unique_notes = list(set(x for sf in scoreFragments 
            for x in sf['notes']))
        melodies_str = [mel2str(m, unique_notes) for m in melodies]
        
        dists = matrix([[normalizedLevenshtein(m1, m2)
            for m1 in melodies_str] for m2 in melodies_str])
        
        cliques = getCliques(dists, melody_sim_thres)

        melody_labels = semiotize(cliques)

        # label the insrumental sections, if present
        all_labels = [l for sub_list in get_symbtr_labels().values() for l in sub_list]
        for i in range(0, len(melody_labels)):
            if sections[i]['name'] not in ['LYRICS_SECTION', 'INSTRUMENTAL_SECTION']:
                # if it's a mixture clique, keep the label altogether
                sections[i]['melodicStructure'] = (sections[i]['slug'] +
                    '_'+melody_labels[i][1:] if melody_labels[i][1].isdigit()
                    else sections[i]['slug'] + '_' + melody_labels[i])
            else:
                sections[i]['melodicStructure'] = melody_labels[i]

        # sanity check
        for lbl, mel in zip(melody_labels, melodies):
            chk_mel = ([melodies[i] for i, x in enumerate(melody_labels) 
                if x == lbl])
            if not all(mel == cm for cm in chk_mel):
                print '   Mismatch in melody_label: ' + lbl
    else:  # no section information
        sections = []

    return sections

def semiotize(cliques):
    # Here we follow the annotation conventions explained in:
    #
    # Frederic Bimbot, Emmanuel Deruty, Gabriel Sargent, Emmanuel Vincent. 
    # Semiotic structure labeling of music pieces: Concepts, methods and 
    # annotation conventions. 13th International Society for Music 
    # Information Retrieval Conference (ISMIR), Oct 2012, Porto, Portugal. 
    # 2012. <hal-00758648> 
    # https://hal.inria.fr/file/index/docid/758648/filename/bimbot_ISMIR12.pdf
    #
    # Currently we only make use of the simplest labels, e.g. A, A1, B and AB
    
    num_nodes = len(set.union(*cliques['exact']))
    labels = ['?'] * num_nodes  # labels to fill for each note

    sim_clq_it = [1] * len(cliques['similar'])  # the index to label similar cliques
    mix_clq_it = dict()  # the index to label mixture cliques, if they exist

    # define the ascci letters for semiotic labeling; use capital first
    ascii_letters = string.ascii_uppercase + string.ascii_lowercase

    # similar cliques give us the base structure
    basenames = [ascii_letters[i] for i in range(0,len(cliques['similar']))]
    for ec in cliques['exact']:
        
        # find the similar cliques of which the currect exact clique is subset of 
        in_cliques_idx = [i for i, x in enumerate(cliques['similar']) if ec <= x]

        if len(in_cliques_idx) == 1: # belongs to one similar clique
            for e in sorted(ec):  # label with basename + number
                labels[e]=(basenames[in_cliques_idx[0]]+
                    str(sim_clq_it[in_cliques_idx[0]]))
            sim_clq_it[in_cliques_idx[0]] += 1

        elif len(in_cliques_idx) > 1: # belongs to more than one similar clique
            mix_str = ''.join([basenames[i] for i in in_cliques_idx])
            if mix_str not in mix_clq_it.keys():
                mix_clq_it[mix_str] = 1

            for e in ec:  # join the labels of all basenames 
                labels[e]=mix_str + str(mix_clq_it[mix_str])
            
            mix_clq_it[mix_str] += 1
        else: # in no cliques; impossible
            print ("   The exact clique is not in the similar cliques list. "
                "This shouldn't happen.")
    return labels
