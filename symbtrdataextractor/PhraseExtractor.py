from . ScoreProcessor import ScoreProcessor
from . StructureLabeler import StructureLabeler


class PhraseExtractor(object):
    """

    """
    def __init__(self, lyrics_sim_thres=0.75, melody_sim_thres=0.75,
                 crop_consecutive_bounds=True):
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
        crop_consecutive_bounds : bool, optional
            True to remove the first of the two consecutive boundaries,
            False otherwise. (the default is True)
        """
        self.lyrics_sim_thres = lyrics_sim_thres
        self.melody_sim_thres = melody_sim_thres
        self.crop_consecutive_bounds = crop_consecutive_bounds

        self.phraseLabeler = StructureLabeler(
            lyrics_sim_thres=self.lyrics_sim_thres,
            melody_sim_thres=self.melody_sim_thres)

    def extract_annotations(self, score, sections=None):
        # code 51 is the usul change and it always marks a phrase boundary
        bound_codes = [51, 53, 54, 55]
        anno_codes = [53, 54, 55]

        # get all boundaries starting with the first note
        all_bounds = self._get_all_bounds_in_score(bound_codes, score)

        # if there are only usul boundaries the score does not have anotations
        anno_bounds = [i for i, code in enumerate(score['code'])
                       if code in anno_codes]

        if anno_bounds:
            phrases = self._extract(all_bounds, score, sections=sections)
        else:
            phrases = []

        return phrases

    @staticmethod
    def _get_all_bounds_in_score(bound_codes, score):
        # start bounds with the first note
        first_note_idx = ScoreProcessor.get_first_note_index(score)

        all_bounds = [first_note_idx]
        for i, code in enumerate(score['code']):
            if code in bound_codes and i > first_note_idx:
                all_bounds.append(i)

        return all_bounds

    def extract_segments(self, score, segment_note_bound_idx, sections=None):
        try:
            if segment_note_bound_idx:
                segments = self._extract(segment_note_bound_idx, score,
                                         sections=sections)
            else:
                segments = []
        except TypeError:  # the json saved by MATLAB phrase segmentation sends
            # a special structure specifying the 0 dimensional array
            segments = []

        return segments

    def _extract(self, bounds, score, sections=None):
        # add the first and the last bound if they are not already given,
        # sort & tidy
        bounds = self._parse_bounds(bounds, score)

        all_labels = [l for sub_list in
                      StructureLabeler.get_symbtr_labels().values()
                      for l in sub_list]
        real_lyrics_idx = ScoreProcessor.get_true_lyrics_idx(
            score['lyrics'], all_labels, score['duration'])

        phrases = []
        for pp in range(0, len(bounds) - 1):
            start_note_idx = bounds[pp]
            end_note_idx = bounds[pp + 1] - 1

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
                start_section_idx = self._get_section_idx(sections, start_note)
                end_section_idx = self._get_section_idx(sections, end_note)

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

    @staticmethod
    def _get_section_idx(sections, note_idx):
        section_idx = [i for i, sec in enumerate(sections)
                       if sec['start_note'] <= note_idx <= sec['end_note']]

        assert len(section_idx) == 1, 'Unexpected indexing: the note should ' \
                                      'have been in a single section'

        return section_idx[0]

    def _parse_bounds(self, bounds, score):
        # add start and end if they are not already in the list
        first_bound_idx = ScoreProcessor.get_first_note_index(score)
        bounds = [first_bound_idx] + bounds

        # create the boundary outside the score idx
        last_bound_idx = len(score['code'])
        bounds = bounds + [last_bound_idx]

        # sort and tidy
        bounds = sorted(list(set(bounds)))

        # remove consecutive boundaries
        self._crop_consec_bounds(bounds, first_bound_idx)

        # check boundaries
        all_bounds_in_score = all(last_bound_idx >= b >= first_bound_idx
                                  for b in bounds)
        assert all_bounds_in_score, 'one of the bounds is outside the score.'

        return bounds

    def _crop_consec_bounds(self, bounds, first_bound_idx):
        if self.crop_consecutive_bounds:
            for i in reversed(range(0, len(bounds) - 1)):
                if bounds[i + 1] - bounds[i] == 1:
                    if bounds[i] == first_bound_idx:
                        # if there are two consecutive bounds in the start,
                        # pop the second
                        bounds.pop(i + 1)
                    else:
                        # if there are two consecutive bounds, pop the first
                        bounds.pop(i)
