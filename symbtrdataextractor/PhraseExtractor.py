from ScoreProcessor import ScoreProcessor
from StructureLabeler import StructureLabeler


class PhraseExtractor(object):
    """

    """
    def __init__(self, lyrics_sim_thres=0.75, melody_sim_thres=0.75,
                 extract_all_labels=False):
        """
        Class constructor

        Parameters
        ----------
        lyrics_sim_thres : float[0, 1], optional
            The similarity threshold for the lyrics of two sections/phrases
            to be regarded as similar. (the default is 0.75)
        melody_sim_thres : float[0, 1], optional
            The similarity threshold for the melody of two sections/phrases
            to be regarded as similar. (the default is 0.75)
        extract_all_labels : bool, optional
            True to extract all labels in written in the lyrics field
            regardless they are a structural marking etc., False to only
            extract the lyrics. (the default is False)
        """
        self.extract_all_labels = extract_all_labels
        self.lyrics_sim_thres = lyrics_sim_thres
        self.melody_sim_thres = melody_sim_thres

        self.phraseLabeler = StructureLabeler(
            lyrics_sim_thres=self.lyrics_sim_thres,
            melody_sim_thres=self.melody_sim_thres)

    def extract_annotated(self, score, sections=None):
        bound_codes = [51, 53, 54, 55]
        anno_codes = [53, 54, 55]

        first_note_idx = ScoreProcessor.get_first_note_index(score)

        # start bounds with the first note, ignore the control rows in the
        # start
        all_bounds = [first_note_idx] + [i for i, code in enumerate(
            score['code']) if code in bound_codes if i > first_note_idx]
        anno_bounds = [i for i, code in enumerate(score['code'])
                       if code in anno_codes]

        if anno_bounds:
            phrases = self.extract(all_bounds, score, sections=sections)
        else:
            phrases = []

        return phrases

    def extract_auto_segment(self, score, segment_note_bound_idx,
                             sections=None):
        # Boundaries start from 1, convert them to python indexing (0) by
        # subtracting 1
        try:
            auto_seg_bound_idx = [a - 1 for a in segment_note_bound_idx]

            if auto_seg_bound_idx:
                phrases = self.extract(auto_seg_bound_idx, score,
                                       sections=sections)
            else:
                phrases = []
        except TypeError:  # the json saved by MATLAB phrase segmentation sends
            # a special structure specifying the 0 dimensional array
            phrases = []

        return phrases

    def extract(self, bounds, score, sections=None):
        # add start and end if they are not already in the list
        firstnoteidx = ScoreProcessor.get_first_note_index(score)
        if firstnoteidx not in bounds:
            bounds = [firstnoteidx] + bounds

        # create the boundary outside the score idx
        bounds = bounds + [len(score['code'])]

        # remove consecutive boundaries
        phrase_bounds = (sorted([bounds[i]
                                for i in reversed(range(0, len(bounds) - 1))
                                if not bounds[i + 1] - bounds[i] == 1]) +
                         [len(score['code'])])

        # if the the last boundary is removed due to consecutive boundaries,
        # pop the first to the last and append the last
        if len(score['code']) - 1 in phrase_bounds:
            phrase_bounds = ([pb for pb in phrase_bounds
                              if not pb == len(score['code']) - 1] +
                             [len(score['code'])])

        all_labels = [l for sub_list in
                      StructureLabeler.get_symbtr_labels().values()
                      for l in sub_list]
        real_lyrics_idx = ScoreProcessor.get_true_lyrics_idx(
            score['lyrics'], all_labels, score['duration'])

        phrases = []
        for pp in range(0, len(phrase_bounds) - 1):
            start_note_idx = phrase_bounds[pp]
            end_note_idx = phrase_bounds[pp + 1] - 1

            # start and endNotes
            start_note = score['index'][start_note_idx]
            end_note = score['index'][end_note_idx]

            # cesni/flavor
            flavor = [score['lyrics'][start_note_idx + i]
                      for i, code in
                      enumerate(score['code'][start_note_idx:end_note_idx + 1])
                      if code == 54]

            # lyrics
            phrase_lyrics_idx = ([rl for rl in real_lyrics_idx
                                  if start_note <= rl <= end_note])
            syllables = [score['lyrics'][li] for li in phrase_lyrics_idx]
            lyrics = ''.join(syllables)

            # sections
            phrase_sections = []
            if sections:
                start_section_idx = [i for i, sec in enumerate(sections)
                                     if sec['start_note'] <= start_note <=
                                     sec['end_note']][0]
                end_section_idx = [i for i, sec in enumerate(sections)
                                   if sec['start_note'] <= end_note <=
                                   sec['end_note']][0]

                for idx, sec in zip(range(start_section_idx,
                                          end_section_idx + 1),
                                    sections[start_section_idx:
                                             end_section_idx + 1]):
                    phrase_sections.append(
                        {'section_idx': idx,
                         'melodic_structure': sec['melodic_structure'],
                         'lyric_structure': sec['lyric_structure']})

            if lyrics:
                name = u"VOCAL_PHRASE"
                slug = u"VOCAL_PHRASE"
            else:
                name = u"INSTRUMENTAL_PHRASE"
                slug = u"INSTRUMENTAL_PHRASE"

            phrases.append({'name': name, 'slug': slug, 'flavor': flavor,
                            'start_note': start_note, 'end_note': end_note,
                            'lyrics': lyrics, 'sections': phrase_sections})

        return self.phraseLabeler.label_structures(phrases, score)
