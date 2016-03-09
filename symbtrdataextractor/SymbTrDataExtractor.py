from section import extract_section
from phrase import extract_annotated_phrase, extract_auto_seg_phrase
from SymbTrReader import read_mu2_score, read_txt_score, read_musicxml_score
from metadata import get_metadata
from rhythm import extract_rhythmic_structure
import os


class SymbTrDataExtractor:
    _version = "1.1"
    _sourcetype = "txt"
    _slug = "symbtrdataextractor"

    def __init__(self, extract_all_labels=False, lyrics_sim_thres=0.25,
                 melody_sim_thres=0.25, get_recording_rels=False):
        self.extract_all_labels = extract_all_labels
        self.lyrics_sim_thres = lyrics_sim_thres
        self.melody_sim_thres = melody_sim_thres
        self.get_recording_rels = get_recording_rels

    def extract(self, score_file, symbtr_name=None, mbid=None,
                segment_note_bound_idx=None, print_warnings=True):
        if not symbtr_name:
            symbtr_name = os.path.splitext(os.path.basename(score_file))[0]
        
        # get the metadata
        data, is_metadata_valid = get_metadata(
            symbtr_name, mbid=mbid,
            get_recording_rels=self.get_recording_rels)

        # get the extension to determine the SymbTr-score format
        extension = os.path.splitext(score_file)[1]

        # read the score
        if extension == ".txt":
            score, is_score_content_valid = read_txt_score(score_file)
        elif extension == ".xml":
            score, is_score_content_valid = read_musicxml_score(score_file)
        elif extension == ".mu2":
            score, is_score_content_valid = read_mu2_score(score_file)
        else:
            raise IOError("Unknown format")

        data['duration'] = {'value': sum(score['duration']) * 0.001,
                            'unit': 'second'}
        data['number_of_notes'] = len(score['duration'])

        data['sections'], is_section_data_valid = extract_section(
            score, symbtr_name, extract_all_labels=self.extract_all_labels,
            lyrics_sim_thres=self.lyrics_sim_thres,
            melody_sim_thres=self.melody_sim_thres,
            print_warnings=print_warnings)

        anno_phrase = extract_annotated_phrase(
            score, sections=data['sections'],
            lyrics_sim_thres=self.lyrics_sim_thres,
            melody_sim_thres=self.melody_sim_thres)
        auto_phrase = extract_auto_seg_phrase(
            score, sections=data['sections'],
            seg_note_idx=segment_note_bound_idx,
            lyrics_sim_thres=self.lyrics_sim_thres,
            melody_sim_thres=self.melody_sim_thres)

        data['rhythmic_structure'] = extract_rhythmic_structure(score)

        data['phrases'] = {'annotated': anno_phrase, 'automatic': auto_phrase}
        is_data_valid = all([is_metadata_valid, is_section_data_valid,
                             is_score_content_valid])

        return data, is_data_valid

    @staticmethod
    def merge(txt_data, mu2_data, verbose=True):
        """
        Merge the extracted data, precedence goes to key value pairs in latter
        dicts.
        :param txt_data: data extracted from SymbTr-txt file
        :param mu2_data: data extracted from SymbTr-mu2 file
        :param verbose: boolean to print the process or not
        """
        txt_dict = txt_data.copy()
        mu2_dict = mu2_data.copy()

        if 'work' in txt_dict.keys():
            mu2_dict['work'] = mu2_dict.pop('title')
        elif 'recording' in txt_dict.keys():
            mu2_dict['recording'] = mu2_dict.pop('title')
        else:
            if verbose:
                print '   Unknown title target.'
            mu2_dict.pop('title')

        return dictmerge(txt_dict, mu2_dict)


def dictmerge(*data_dicts):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
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
                    print '   ' + key + ' already exists! Overwriting...'
                    result[key] = val
            else:
                result[key] = dictmerge(result[key], val)

    return result
