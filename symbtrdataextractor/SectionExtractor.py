from math import floor

from slugify_tr import slugify_tr
from ScoreProcessor import ScoreProcessor
from structure_label import StructureLabeler
from OffsetProcessor import OffsetProcessor


class SectionExtractor(object):
    """

    """
    def __init__(self, lyrics_sim_thres=0.75, melody_sim_thres=0.75,
                 extract_all_labels=False, print_warnings=True):
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
        print_warnings : bool, optional
            True to display warnings, False otherwise. Note that the errors
            and the inconsistencies in the scores will be always displayed
            (the default is True)
        """
        self.extract_all_labels = extract_all_labels
        self.lyrics_sim_thres = lyrics_sim_thres
        self.melody_sim_thres = melody_sim_thres
        self.print_warnings = print_warnings

        self.offsetProcessor = OffsetProcessor(
            print_warnings=self.print_warnings)
        self.sectionLabeler = StructureLabeler(
            lyrics_sim_thres=self.lyrics_sim_thres,
            melody_sim_thres=self.melody_sim_thres)

    def extract(self, score, symbtrname):
        all_labels = [l for sub_list in
                      StructureLabeler.get_symbtr_labels().values()
                      for l in sub_list]
        struct_lbl = all_labels if self.extract_all_labels else \
            StructureLabeler.get_symbtr_labels()['structure']

        measure_start_idx, is_measure_start_valid = \
            self.offsetProcessor.find_measure_start_idx(
                score['offset'])

        # Check lyrics information
        if all(l == '' for l in score['lyrics']):
            # empty lyrics field; we cannot really do anything without
            # symbolic analysis
            sections = []
        else:
            sections = self._get_sections(score, struct_lbl)
            sections = self._locate_section_boundaries(
                sections, score, all_labels, measure_start_idx)

            # the refine section names according to the lyrics, pitch and durs
            sections = self.sectionLabeler.label_structures(sections, score)

        sections_valid = self._validate_sections(
            sections, score, set(all_labels) - set(struct_lbl), symbtrname)
        valid_bool = sections_valid and is_measure_start_valid

        # map the python indices in start_note and end_note to SymbTr index
        for se in sections:
            se['start_note'] = score['index'][se['start_note']]
            se['end_note'] = score['index'][se['end_note']]

        return sections, valid_bool

    def extract_from_musicxml(self, score):
        return NotImplemented

    def extract_from_mu2(self, score):
        return NotImplemented

    @staticmethod
    def _get_sections(score, struct_lbl):
        sections = []
        for i, l in enumerate(score['lyrics']):
            if l in struct_lbl:  # note the explicit structures
                sections.append({'name': l, 'slug': slugify_tr(l),
                                 'start_note': i, 'end_note': [],
                                 'lyrics': ''})
            elif '  ' in l:  # lyrics end marker
                # lyrics will be updated in locate_section_boundaries
                sections.append({'name': u"VOCAL_SECTION",
                                 'slug': u"VOCAL_SECTION", 'start_note': [],
                                 'end_note': i, 'lyrics': ''})
        return sections

    def _locate_section_boundaries(self, sections, score, struct_lbl,
                                   measure_start_idx):
        first_note_idx = ScoreProcessor.get_first_note_index(score)
        real_lyrics_idx = ScoreProcessor.get_true_lyrics_idx(
            score['lyrics'], struct_lbl, score['duration'])

        start_note_idx = [s['start_note'] for s in sections] + \
                         [len(score['lyrics'])]
        end_note_idx = [-1] + [s['end_note'] for s in sections]
        for se in reversed(sections):  # start from the last section
            if se['slug'] == u'VOCAL_SECTION':
                # carry the 'end_note' to the next closest start
                se['end_note'] = min(x for x in start_note_idx
                                     if x > se['end_note']) - 1

                # update end_note_idx
                end_note_idx = [-1] + [s['end_note'] for s in sections]

                # estimate the start of the lyrics sections
                try:  # find the previous closest start
                    prev_closest_start_ind = max(x for x in start_note_idx
                                                 if x < se['end_note'])
                except ValueError:  # no section label in lyrics columns
                    prev_closest_start_ind = -1

                try:  # find the previous closest end
                    prev_closest_end_ind = max(x for x in end_note_idx
                                               if x < se['end_note'])
                except ValueError:  # no vocal sections
                    prev_closest_end_ind = -1

                # find where the lyrics of this section starts
                chk_ind = max([prev_closest_end_ind, prev_closest_start_ind])
                next_lyrics_start_ind = min(x for x in real_lyrics_idx
                                            if x > chk_ind)
                next_lyrics_measure_offset = floor(
                    score['offset'][next_lyrics_start_ind])

                # check if next_lyrics_start_ind and prev_closest_end_ind are
                # in the same measure. Ideally they should be in different
                # measures
                if next_lyrics_measure_offset == floor(
                        score['offset'][prev_closest_end_ind]):
                    if self.print_warnings:
                        print("    " + str(next_lyrics_measure_offset) + ':' +
                              score['lyrics'][prev_closest_end_ind] + ' and ' +
                              score['lyrics'][next_lyrics_start_ind] +
                              ' are in the same measure!')

                    se['start_note'] = next_lyrics_start_ind
                else:  # The section starts on the first measure the lyrics
                    # start
                    se['start_note'] = max(
                        [OffsetProcessor.get_measure_offset_id(
                            next_lyrics_measure_offset, score['offset'],
                            measure_start_idx), first_note_idx])

                # update start_note_idx
                start_note_idx = ([s['start_note'] for s in sections] +
                                  [len(score['lyrics'])])

                # update lyrics
                section_lyrics_idx = ([rl for rl in real_lyrics_idx
                                       if se['start_note'] <= rl <=
                                       se['end_note']])
                syllables = [score['lyrics'][li] for li in section_lyrics_idx]
                se['lyrics'] = ''.join(syllables)
            else:  # instrumental
                se['end_note'] = min(x for x in start_note_idx
                                     if x > se['start_note']) - 1

                # update end_note_idx
                end_note_idx = [-1] + [s['end_note'] for s in sections]

        # if the first rows are control rows and the first section starts next
        if sections:
            first_note_idx = ScoreProcessor.get_first_note_index(score)

            first_sec = sections[0]
            first_sec_idx = -1
            for ii, sec in enumerate(sections):
                if sec['start_note'] < first_sec['start_note']:
                    first_sec = sec
                    first_sec_idx = ii

            # if there is a gap in the start, create a new section
            if first_sec['start_note'] > first_note_idx:
                sections.append({'name': u'INSTRUMENTAL_SECTION',
                                 'slug': u'INSTRUMENTAL_SECTION',
                                 'start_note': first_note_idx,
                                 'end_note': min([s['start_note']
                                                  for s in sections]) - 1})
        return self._sort_sections(sections)

    @staticmethod
    def _sort_sections(sections):
        # sort the sections
        sort_idx = [i[0] for i in sorted(enumerate([s['start_note']
                                                    for s in sections]),
                                         key=lambda x: x[1])]
        return [sections[s] for s in sort_idx]

    def _validate_sections(self, sections, score, ignore_labels, symbtrname):
        # treat some of these are warning; they'll be made stricter later
        valid_bool = True
        if not sections:  # check section presence
            if self.print_warnings:
                print "    " + symbtrname + ", Missing section info in lyrics."
        else:  # check section continuity
            first_note_idx = ScoreProcessor.get_first_note_index(score)

            ends = [first_note_idx - 1] + [s['end_note'] for s in sections]
            starts = [s['start_note'] for s in sections] + \
                     [len(score['offset'])]
            for s, e in zip(starts, ends):
                if not s - e == 1:
                    if self.print_warnings:
                        print("    " + symbtrname + ", " + str(e) + '->' +
                              str(s) + ', Gap between the sections')
                    valid_bool = False

        for s in sections:
            # check whether section starts on the measure or not
            starts_on_measure = not OffsetProcessor.is_integer_offset(
                score['offset'][s['start_note']]) \
                                and s['slug'] not in ignore_labels
            if starts_on_measure and self.print_warnings:
                print("    " + symbtrname + ", " + str(s['start_note']) +
                      ', ' + s['slug'] + ' does not start on a measure: ' +
                      str(score['offset'][s['start_note']]))
            # check if the end of a section somehow got earlier than its start
            if s['start_note'] > s['end_note']:
                print("    " + symbtrname + ", " + str(s['start_note']) +
                      '->' + str(s['end_note']) + ', ' + s['slug'] +
                      ' ends before it starts: ' +
                      str(score['offset'][s['start_note']]))
                valid_bool = False

        # check if there are any structure labels with a space
        # e.g. it is not found
        all_labels = [l for sub_list in
                      StructureLabeler.get_symbtr_labels().values()
                      for l in sub_list] + ['.']
        for i, ll in enumerate(score['lyrics']):
            for label in all_labels:
                # invalid lyrics end
                if (label + ' ') == ll or (label + '  ') == ll:
                    print("    " + symbtrname + ', ' + str(i) +
                          ": Extra space in " + ll)
                    valid_bool = False

        return valid_bool
