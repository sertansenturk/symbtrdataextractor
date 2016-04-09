import csv
import os


class SymbTrReader(object):
    def __init__(self):
        """
        Class constructor
        """
        pass

    @classmethod
    def read_txt_score(cls, score_file, symbtr_name=None):
        """
        Reader method for the SymbTr-txt scores

        Parameters
        ----------
        score_file : str
            The path of the SymbTr score
        symbtr_name : str, optional
            The name of the score in SymbTr naming convention
            (makam--form--usul--name--composer).
        Returns
        ----------
        dict
            A dictionary of the read SymbTr-txt score, where each key is the
            name of a column in the SymbTr-txt
        bool
            True if the read SymbTr-txt score is valid, False otherwise
        """
        if symbtr_name is None:
            symbtr_name = os.path.splitext(os.path.basename(score_file))[0]

        with open(score_file, "rb") as f:
            reader = csv.reader(f, delimiter='\t')

            header = next(reader, None)

            index_col = header.index('Sira')
            code_col = header.index('Kod')
            note53_col = header.index('Nota53')
            noteAE_col = header.index('NotaAE')
            comma53_col = header.index('Koma53')
            commaAE_col = header.index('KomaAE')
            numerator_col = header.index('Pay')
            denumerator_col = header.index('Payda')
            duration_col = header.index('Ms')
            lns_col = header.index('LNS')
            bas_col = header.index('Bas')
            lyrics_col = header.index('Soz1')
            offset_col = header.index('Offset')

            score = {'index': [], 'code': [], 'note53': [], 'noteAE': [],
                     'comma53': [], 'commaAE': [], 'numerator': [],
                     'denumerator': [], 'duration': [], 'lyrics': [],
                     'offset': [], 'lns': [], 'bas': []}
            for row in reader:
                score['index'].append(int(row[index_col]))
                score['code'].append(int(row[code_col]))
                score['note53'].append(row[note53_col])
                score['noteAE'].append(row[noteAE_col])
                score['comma53'].append(int(row[comma53_col]))
                score['commaAE'].append(int(row[commaAE_col]))
                score['numerator'].append(int(row[numerator_col]))
                score['denumerator'].append(int(row[denumerator_col]))
                score['duration'].append(int(row[duration_col]))
                score['lns'].append(int(row[lns_col]))
                score['bas'].append(int(row[bas_col]))
                score['lyrics'].append(row[lyrics_col].decode('utf-8'))
                score['offset'].append(float(row[offset_col]))

        # shift offset such that the first note of each measure has an
        # integer offset
        score['offset'].insert(0, 0)
        score['offset'] = score['offset'][:-1]

        # validate
        is_score_valid = cls._validate_txt_score(score, symbtr_name)

        return score, is_score_valid

    @staticmethod
    def _validate_txt_score(score, score_name):
        """
        Validation method for the SymbTr-txt score

        Parameters
        ----------
        score : dict
            A dictionary of the read SymbTr-txt score, where each key is a row
        score_name : str, optional
            The name of the score in SymbTr naming convention
            (makam--form--usul--name--composer).
        Returns
        ----------
        bool
            True if the read SymbTr-txt score is valid, False otherwise
        """
        is_rest_valid = True
        is_duration_valid = True
        is_index_valid = True
        start_usul_row = True
        dur_dict = {}
        for ii in range(0, len(score['index'])):
            # check usul row in the start
            if ii == 0 and not score['code'][ii] == 51:
                print("    " + score_name + ' Missing the usul row in the '
                                            'start')
                start_usul_row = False

            if score['duration'][ii] > 0:  # note or rest
                # check rest
                if (-1 in [score['comma53'][ii], score['commaAE'][ii]] or
                        any(rs in [score['note53'][ii], score['noteAE'][ii]]
                            for rs in ['Es', 'Sus', ''])):
                    # it should be rest, validate
                    if not (score['comma53'][ii] == -1 and
                            score['commaAE'][ii] == -1 and
                            score['note53'][ii] == 'Es' and
                            score['noteAE'][ii] == 'Es' and
                            score['code'][ii] == 9):
                        is_rest_valid = False
                        print("    " + score_name + ' ' +
                              str(score['index'][ii]) + ': Invalid Rest')

                # note duration
                dursym = (str(score['numerator'][ii]) + '_' +
                          str(score['denumerator'][ii]))
                if dursym in dur_dict.keys():
                    dur_dict[dursym] = list(set([score['duration'][ii]] +
                                                dur_dict[dursym]))
                else:
                    dur_dict[dursym] = [score['duration'][ii]]

        # for key, val in dur_dict.items():
        #    if not len(val)==1:
        #        print("    " + scorename + ": " + key +
        #              " note has multiple duration values; " +
        #              ', '.join([str(v) for v in val]))
        #        # USUL/TEMPO CHANGES ARE NOT HANDLED, DON'T ASSIGN FALSE YET
        #        is_duration_valid = True

        # note index
        for ii in range(0, len(score['index']) - 1):
            if not score['index'][ii + 1] - score['index'][ii] == 1:
                print("    " + score_name + ": " + str(score['index'][ii]) +
                      ", note index jump.")
                is_index_valid = False

        is_score_valid = (start_usul_row and is_rest_valid and
                          is_duration_valid and is_index_valid)
        return is_score_valid
