import json
import os

from symbtrdataextractor.dataextractor import DataExtractor
from symbtrdataextractor.reader.mu2 import Mu2Reader

_curr_folder = os.path.dirname(os.path.abspath(__file__))


def _basic_txt_extractor(score_name, use_name=True):
    txt_filename = os.path.join(_curr_folder, 'data', score_name + '.txt')
    symbtr_name = score_name if use_name is True else None

    # initialize the extractor
    extractor = DataExtractor(
        extract_all_labels=False, melody_sim_thres=0.7, lyrics_sim_thres=0.7,
        save_structure_sim=True, get_recording_rels=False, print_warnings=True)

    # extract txt_data
    txt_data, is_data_valid = extractor.extract(txt_filename,
                                                symbtr_name=symbtr_name)

    # compare with a previously saved result
    score_data_file = os.path.join(_curr_folder, 'data', score_name + '.json')
    saved_data = json.load(open(score_data_file))

    assert saved_data == txt_data, u"{0:s}: the result is different".format(
        score_name)
    assert is_data_valid, "The data is not valid (or the validations failed.)"


def test_with_instrumental():
    """
    Tests the result of a instrumental score
    """
    scorename = 'ussak--sazsemaisi--aksaksemai----neyzen_aziz_dede'

    _basic_txt_extractor(scorename)


def test_without_name():
    """
    Tests the result of a score without the symbtr_name input given
    """
    scorename = 'ussak--sazsemaisi--aksaksemai----neyzen_aziz_dede'

    _basic_txt_extractor(scorename, use_name=False)


def test_with_free_usul():
    """
    Tests the result of a score with free (serbest) usul
    """
    scorename = 'saba--miraciye--serbest--pes_heman--nayi_osman_dede'

    _basic_txt_extractor(scorename)


def test_with_phrase_annotation():
    """
    Tests the result of a score with phrase_annotations
    """
    scorename = 'huzzam--sarki--curcuna--guzel_gun_gormedi--haci_arif_bey'

    _basic_txt_extractor(scorename)


def test_with_vocal_section_starting_mid_measure():
    """
    Tests the result with the score of a vocal composition in which some of
    the lyrical lines start in middle of the measure
    """
    scorename = 'hicaz_humayun--beste--hafif--olmada_diller--abdulhalim_aga'

    _basic_txt_extractor(scorename)


def test_with_full_input():
    """
    Tests the result with complete information available, i.e. mbid, phrase
    annotation and user provided segmentation
    """
    # inputs
    scorename = 'kurdilihicazkar--sarki--agiraksak--ehl-i_askin--tatyos_efendi'

    txt_filename = os.path.join(_curr_folder, 'data', scorename + '.txt')

    mbid = 'b43fd61e-522c-4af4-821d-db85722bf48c'

    auto_seg_file = os.path.join(_curr_folder, 'data', scorename + '.autoSeg')
    auto_seg_bounds = json.load(open(auto_seg_file, 'r'))['boundary_noteIdx']

    mu2_filename = os.path.join(_curr_folder, 'data', scorename + '.mu2')

    # initialize the extractor
    extractor = DataExtractor(
        extract_all_labels=False, melody_sim_thres=0.75, lyrics_sim_thres=0.75,
        save_structure_sim=True, get_recording_rels=False, print_warnings=True)

    # extract txt_data
    txt_data, is_data_valid = extractor.extract(
        txt_filename, symbtr_name=scorename, mbid=mbid,
        segment_note_bound_idx=auto_seg_bounds)

    # extract mu2 header metadata
    mu2_header, header_row, is_header_valid = Mu2Reader.read_header(
        mu2_filename, symbtr_name=scorename)

    # merge
    data = DataExtractor.merge(txt_data, mu2_header)
    is_valid = is_data_valid and is_header_valid

    # compare with a previously saved result
    score_data_file = os.path.join(_curr_folder, 'data', scorename + '.json')
    saved_data = json.load(open(score_data_file))

    assert saved_data == data, u"{0:s}: the result is different".format(
        scorename)
    assert is_valid, "The data is not valid (or the validations failed.)"
