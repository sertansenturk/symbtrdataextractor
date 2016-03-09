import os
import json
from numpy import matrix
from ScoreProcessor import ScoreProcessor
from structure_graph import GraphOperations


class StructureLabeler(object):
    """

    """
    def __init__(self, lyrics_sim_thres=0.75, melody_sim_thres=0.75):
        self.lyrics_sim_thres = lyrics_sim_thres
        self.melody_sim_thres = melody_sim_thres

    @staticmethod
    def get_symbtr_labels():
        symbtr_label_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'makam_data', 'symbTrLabels.json')
        symbtr_label = json.load(open(symbtr_label_file, 'r'))

        return symbtr_label

    def label_structures(self, structures, score):
        # get the duration, pitch and lyrics related to the section
        score_fragments = []
        for s in structures:
            durs = score['duration'][s['start_note']:s['end_note'] + 1]
            nums = score['numerator'][s['start_note']:s['end_note'] + 1]
            denums = score['denumerator'][s['start_note']:s['end_note'] + 1]
            notes = score['comma53'][s['start_note']:s['end_note'] + 1]
            lyrics = score['lyrics'][s['start_note']:s['end_note'] + 1]

            score_fragments.append({'durs': durs, 'nums': nums,
                                    'denums': denums, 'notes': notes,
                                    'lyrics': lyrics})

        # get the lyric organization
        structures = self.get_lyric_organization(structures, score_fragments)

        # get the melodic organization
        structures = self.get_melodic_organization(structures, score_fragments)

        return structures

    def get_lyric_organization(self, structures, score_fragments):
        # Here we only check whether the lyrics are similar to others
        # We don't check whether they are sung on the same note / with
        # the same duration, or not. As a results, two structures having
        # exactly the same melody but different sylallable onset/offsets
        # would be considered the same. Nevertheless this situation
        # would occur in very rare occasions.
        # From the point of view of an audio-score alignment algorithm
        # using only melody, this function does not give any extra info
        # This part is done for future needs; e.g. audio-lyrics alignment

        if structures:
            # get the lyrics stripped of section information
            all_labels = [l for sub_list in self.get_symbtr_labels().values()
                          for l in sub_list]
            all_labels += ['.', '', ' ']
            for sf in score_fragments:
                real_lyrics_idx = ScoreProcessor.get_true_lyrics_idx(
                    sf['lyrics'], all_labels, sf['durs'])
                sf['lyrics'] = u''.join([sf['lyrics'][i].replace(u' ', u'')
                                         for i in real_lyrics_idx])

            dists = matrix([[GraphOperations.normalized_levenshtein(
                a['lyrics'], b['lyrics']) for a in score_fragments]
                            for b in score_fragments])

            cliques = GraphOperations.get_cliques(dists, self.lyrics_sim_thres)

            lyrics_labels = self.semiotize(cliques)

            # label the insrumental structures, if present
            for i in range(0, len(lyrics_labels)):
                if not score_fragments[i]['lyrics']:
                    structures[i]['lyric_structure'] = 'INSTRUMENTAL'
                else:
                    structures[i]['lyric_structure'] = lyrics_labels[i]

            # sanity check
            lyrics = [sc['lyrics'] for sc in score_fragments]
            for lbl, lyr in zip(lyrics_labels, lyrics):
                chk_lyr = ([lyrics[i] for i, x in enumerate(lyrics_labels)
                            if x == lbl])
                if not all(lyr == cl for cl in chk_lyr):
                    raise RuntimeError('Mismatch in lyrics_label: ' + lbl)

        else:  # no section information
            structures = []

        return structures

    def get_melodic_organization(self, structures, score_fragments):
        if structures:
            # remove annotation/control row; i.e. entries w 0 duration
            for sf in score_fragments:
                for i in reversed(range(0, len(sf['durs']))):
                    if sf['durs'][i] == 0:
                        sf['notes'].pop(i)
                        sf['nums'].pop(i)
                        sf['denums'].pop(i)
                        sf['durs'].pop(i)

            # synthesize the score according taking the shortest note as the
            # unit shortest note has the greatest denumerator
            max_denum = max(max(sf['denums']) for sf in score_fragments)
            melodies = [ScoreProcessor.synth_melody(sf, max_denum)
                        for sf in score_fragments]

            # convert the numbers in melodies to unique strings for Levenstein
            unique_notes = list(set(x for sf in score_fragments
                                    for x in sf['notes']))
            melodies_str = [ScoreProcessor.mel2str(m, unique_notes)
                            for m in melodies]

            dists = matrix([[GraphOperations.normalized_levenshtein(m1, m2)
                             for m1 in melodies_str] for m2 in melodies_str])

            cliques = GraphOperations.get_cliques(dists, self.melody_sim_thres)

            melody_labels = StructureLabeler.semiotize(cliques)

            # label the instrumental structures, if present
            all_labels = [l for sub_list in self.get_symbtr_labels().values()
                          for l in sub_list]
            for i in range(0, len(melody_labels)):
                if all(lbl not in structures[i]['name']
                       for lbl in ['VOCAL', 'INSTRUMENTAL']):
                    # if it's a mixture clique, keep the label altogether
                    mel_str = (
                        structures[i]['slug'] + '_' + melody_labels[i][1:]
                        if melody_labels[i][1].isdigit()
                        else structures[i]['slug'] + '_' + melody_labels[i])
                    structures[i]['melodic_structure'] = mel_str
                else:
                    structures[i]['melodic_structure'] = melody_labels[i]

            # sanity check
            for lbl, mel in zip(melody_labels, melodies):
                chk_mel = ([melodies[i] for i, x in enumerate(melody_labels)
                            if x == lbl])
                if not all(mel == cm for cm in chk_mel):
                    raise RuntimeError('Mismatch in melody_label: ' + lbl)

        else:  # no section information
            structures = []

        return structures

    @staticmethod
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
        # Currently we only use the simplest labels, e.g. A, A1, B and AB
        num_nodes = len(set.union(*cliques['exact']))
        labels = ['?'] * num_nodes  # labels to fill for each note

        sim_clq_it = [1] * len(cliques['similar'])  # idx to label similar
        # cliques
        mix_clq_it = dict()  # the index to label mixture cliques, if they
        # exist

        # define the upper case unicode letters for semiotic labeling
        unicode_letters = [unichr(i) for i in range(0, 1000)
                           if unicode.isupper(unichr(i))]

        # similar cliques give us the base structure
        basenames = [unicode_letters[i]
                     for i in range(0, len(cliques['similar']))]
        for ec in cliques['exact']:
            # find the similar cliques of which the currect exact clique is
            # a subset of
            in_cliques_idx = [i for i, x in enumerate(cliques['similar'])
                              if ec <= x]

            if len(in_cliques_idx) == 1:  # belongs to one similar clique
                for e in sorted(ec):  # label with basename + number
                    labels[e] = (basenames[in_cliques_idx[0]] +
                                 str(sim_clq_it[in_cliques_idx[0]]))
                sim_clq_it[in_cliques_idx[0]] += 1

            elif len(in_cliques_idx) > 1:
                # belongs to more than one similar clique
                mix_str = ''.join([basenames[i] for i in in_cliques_idx])
                if mix_str not in mix_clq_it.keys():
                    mix_clq_it[mix_str] = 1

                for e in ec:  # join the labels of all basenames
                    labels[e] = mix_str + str(mix_clq_it[mix_str])

                mix_clq_it[mix_str] += 1
            else:  # in no cliques; impossible
                raise RuntimeError("The exact clique is not in the similar "
                                   "cliques list. This shouldn't happen.")

        return labels
