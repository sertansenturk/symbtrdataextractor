from .SectionExtractor import SectionExtractor
from .PhraseExtractor import PhraseExtractor
from .SymbTrReader import SymbTrReader
from .MetadataExtractor import MetadataExtractor
from .RhythmicFeatureExtractor import RhythmicFeatureExtractor
import os


class SymbTrDataExtractor(object):
    """
    The class to extract the relevant information from a SymbTr score.

    The information include:
        * Obtain the makam, usul, form, name and composer of the given SymbTr
    score
        * Extract section boundaries from both the implicit and explicit
    section information given in the SymbTr scores. Analyse the melody and the
    lyrics of each section independently and apply semiotic labeling to each
    section accordingly.
        * Extract phrases from the annotated phrase boundaries in the SymbTr
    scores.
        * Add and analyze phrases in the SymbTr-txt scores from computed
    boundaries.
        * Query relevant metadata from MusicBrainz, if the MBID is supplied.

    Currently only the SymbTr-txt scores are supported. MusicXML and mu2
    support can be added, if demanded.
    """
    _version = "1.1"
    _sourcetype = "txt"
    _slug = "symbtrdataextractor"

    def __init__(self, lyrics_sim_thres=0.75, melody_sim_thres=0.75,
                 extract_all_labels=False, get_recording_rels=False,
                 print_warnings=True):
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
        get_recording_rels : bool, optional
            True to query the recording relations related to the score from
            MusicBrainz False otherwise. When calling the extract method the
            relevant (work) MBID should be supplied. If the supplied MBID
            belongs to a recording, this flag will not provide to extra
            information, since the recording metadata will be crawled anyways.
            (the default is False)
        print_warnings : bool, optional
            True to display warnings, False otherwise. Note that the errors
            and the inconsistencies in the scores will be always displayed
            (the default is True)
        """
        self._lyrics_sim_thres = lyrics_sim_thres
        self._melody_sim_thres = melody_sim_thres
        self._extract_all_labels = extract_all_labels
        self._get_recording_rels = get_recording_rels
        self._print_warnings = print_warnings

        self._metadataExtractor = MetadataExtractor(
            get_recording_rels=self._get_recording_rels)

        self._sectionExtractor = SectionExtractor(
            lyrics_sim_thres=self._lyrics_sim_thres,
            melody_sim_thres=self._melody_sim_thres,
            extract_all_labels=self._extract_all_labels,
            print_warnings=self._print_warnings)

        self._phraseExtractor = PhraseExtractor(
            lyrics_sim_thres=self._lyrics_sim_thres,
            melody_sim_thres=self._melody_sim_thres,
            extract_all_labels=self._extract_all_labels)

    # getter and setters
    @property
    def lyrics_sim_thres(self):
        return self._lyrics_sim_thres

    @lyrics_sim_thres.setter
    def lyrics_sim_thres(self, value):
        self._chk_sim_thres_val(value)
        self._lyrics_sim_thres = value

    @property
    def melody_sim_thres(self):
        return self._melody_sim_thres

    @melody_sim_thres.setter
    def melody_sim_thres(self, value):
        self._chk_sim_thres_val(value)
        self._melody_sim_thres = value

    @staticmethod
    def _chk_sim_thres_val(value):
        if not 0 <= value <= 1:
            raise ValueError('The similarity threshold should be a float '
                             'between [0, 1]')

    @property
    def extract_all_labels(self):
        return self._extract_all_labels

    @extract_all_labels.setter
    def extract_all_labels(self, value):
        self._chk_bool(value)
        self._extract_all_labels = value

    @property
    def print_warnings(self):
        return self._print_warnings

    @print_warnings.setter
    def print_warnings(self, value):
        self._chk_bool(value)
        self._print_warnings = value

    @property
    def get_recording_rels(self):
        return self._get_recording_rels

    @get_recording_rels.setter
    def get_recording_rels(self, value):
        self._chk_bool(value)
        self._get_recording_rels = value

    @staticmethod
    def _chk_bool(value):
        if isinstance(value, type(True)):
            raise ValueError('The property should be a boolean')

    def extract(self, score_file, symbtr_name=None, mbid=None,
                segment_note_bound_idx=None):
        """
        Extracts the relevant (meta)data from the SymbTr score.

        Parameters
        ----------
        score_file : str
            The path of the SymbTr score
        symbtr_name : str, optional
            The name of the score in SymbTr naming convention
            (makam--form--usul--name--composer). Needed if the filename does
            not obey this convention. If not provided the method will
            attempt to recover the symbtr_name from the score_file input.
            (the default is None, which implies the name will be recovered
            from symbtr_file)
        mbid : str, optional
            The `MBID <https://musicbrainz.org/doc/MusicBrainz_Identifier>`_
            relevant to the SymbTr score. For the score of a composition the
            work mbid of the composition should be supplied. For the score
            of a transcribed recording the identifier should be a recording
            MBID. The MBID can either be given as the 36 character uuid
            (83291c8a-4ef1-4ffc-8b50-3fc03890f5a4) or as an html link
            (https://musicbrainz.org/work/83291c8a-4ef1-4ffc-8b50
            -3fc03890f5a4). In the first case the method will try to find
            whether the MBID belongs to a work or a recording automatically.
            (the default is None)
        segment_note_bound_idx : list[ind], optional
            Boundary indices obtained from automatic phrase segmentation.
            Currently this parameter is only supported for the SymbTr-txt
            scores. For automatic segmentation from the SymbTr-txt
            scores, you can use the `makam-symbolic-phrase-segmentation
            <https://github.com/MTG/makam-symbolic-phrase-segmentation>`_
            package. (the default is None)

        Returns
        ----------
        dict
            A dictionary storing all the relevant (meta)data
        bool
            True if the information bout the score is all valid/consistent,
            False otherwise

        Raises
        ------
        ValueError
            If either of melody_sim_thres or lyrics_sim_thres imputs is
            outside [0,1]
        """
        if symbtr_name is None:
            symbtr_name = os.path.splitext(os.path.basename(score_file))[0]

        # get the metadata
        data, is_metadata_valid = self._metadataExtractor.get_metadata(
            symbtr_name, mbid=mbid)

        # get the extension to determine the SymbTr-score format
        extension = os.path.splitext(score_file)[1]

        # read the score
        score, is_score_content_valid = self._read_score(
            extension, score_file, symbtr_name)

        data['duration'] = {'value': sum(score['duration']) * 0.001,
                            'unit': 'second'}
        data['number_of_notes'] = len(score['duration'])

        data['sections'], is_section_data_valid = self._sectionExtractor. \
            extract(score, symbtr_name)

        anno_phrase = self._phraseExtractor.extract_annotated(
            score, sections=data['sections'])
        auto_phrase = self._phraseExtractor.extract_auto_segment(
            score, segment_note_bound_idx, sections=data['sections'])

        data['rhythmic_structure'] = \
            RhythmicFeatureExtractor.extract_rhythmic_structure(score)

        data['phrases'] = {'annotated': anno_phrase, 'automatic': auto_phrase}
        is_data_valid = all([is_metadata_valid, is_section_data_valid,
                             is_score_content_valid])

        return data, is_data_valid

    @staticmethod
    def _read_score(extension, score_file, symbtr_name):
        if extension == ".txt":
            score, is_score_content_valid = SymbTrReader.read_txt_score(
                score_file, symbtr_name=symbtr_name)
        elif extension == ".xml":
            score, is_score_content_valid = SymbTrReader.read_musicxml_score(
                score_file, symbtr_name=symbtr_name)
        elif extension == ".mu2":
            score, is_score_content_valid = SymbTrReader.read_mu2_score(
                score_file, symbtr_name=symbtr_name)
        else:
            raise IOError("Unknown format")
        return score, is_score_content_valid

    @classmethod
    def merge(cls, data1, data2, verbose=True):
        """
        Merge the extracted score data from different formats (txt, mu2,
        MusicXML), the precedence goes to key value pairs in latter dicts.

        Parameters
        ----------
        data1 : dict
            The data extracted from SymbTr score
        data2 : dict
            The data extracted from SymbTr-mu2 file (or header)
        verbose : bool
            True to to print the warnings in the merge process, False otherwise

        Returns
        ----------
        dict
            Merged data extracted from the SymbTr scores
        """
        data1_dict = data1.copy()
        data2_dict = data2.copy()

        if 'work' in data1_dict.keys():
            data2_dict['work'] = data2_dict.pop('title')
        elif 'recording' in data1_dict.keys():
            data2_dict['recording'] = data2_dict.pop('title')
        else:
            if verbose:
                print('   Unknown title target.')
            data2_dict.pop('title')

        return cls._dictmerge(data1_dict, data2_dict)

    @staticmethod
    def _dictmerge(*data_dicts):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.

        Parameters
        ----------
        *data_dicts : *dict
            Dictionaries of variable number to merge

        Returns
        ----------
        dict
            Merged dictionaries
        """
        result = {}
        for dictionary in data_dicts:
            dict_cp = dictionary.copy()
            for key, val in dict_cp.iteritems():
                if key not in result.keys():
                    result[key] = val
                elif not isinstance(result[key], dict):
                    if not result[key] == val:
                        # overwrite
                        print('   ' + key + ' already exists! Overwriting...')
                        result[key] = val
                else:
                    result[key] = SymbTrDataExtractor._dictmerge(
                        result[key], val)

        return result
