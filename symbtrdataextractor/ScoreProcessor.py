import string
import os
import json


class ScoreProcessor(object):
    """

    """
    @staticmethod
    def get_true_lyrics(score_fragments):
        all_labels = [l for sub_list in
                      ScoreProcessor.get_symbtr_labels().values()
                      for l in sub_list]
        all_labels += ['.', '', ' ']
        for sf in score_fragments:
            real_lyrics_idx = ScoreProcessor.get_true_lyrics_idx(
                sf['lyrics'], all_labels, sf['durs'])
            sf['lyrics'] = u''.join([sf['lyrics'][i].replace(u' ', u'')
                                     for i in real_lyrics_idx])

    @staticmethod
    def get_true_lyrics_idx(lyrics, all_labels, dur):
        # separate the actual lyrics from other information in the lyrics
        # column
        real_lyrics_idx = []
        for i, l in enumerate(lyrics):
            # annotation/control rows, embellishments (rows w dur = 0) are
            # ignored
            if not (l in all_labels or l in ['.', '', ' '] or dur[i] == 0):
                real_lyrics_idx.append(i)
        return real_lyrics_idx

    @staticmethod
    def get_first_note_index(score):
        for ii, code in enumerate(score['code']):
            if code not in range(50, 57):
                return ii

    @staticmethod
    def get_symbtr_labels():
        symbtr_label_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'makam_data', 'symbTrLabels.json')
        symbtr_label = json.load(open(symbtr_label_file, 'r'))

        return symbtr_label

    @staticmethod
    def synth_melody(score, max_denum):
        melody = []
        for i, note in enumerate(score['notes']):
            num_samp = score['nums'][i] * max_denum / score['denums'][i]
            melody += num_samp * [note]
        return melody

    @staticmethod
    def mel2str(melody, unique_notes):
        # map each element in the melody to a unique ascii letter and
        # concatanate to a single string. This step converts the melody into
        # the format required by Levenhstein distance

        # define the ascii letters, use capital first
        ascii_letters = string.ascii_uppercase + string.ascii_lowercase
        return ''.join([ascii_letters[unique_notes.index(m)] for m in melody])
