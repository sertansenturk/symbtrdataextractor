import json
import os

from symbtrdataextractor.SymbTrDataExtractor import SymbTrDataExtractor
from symbtrdataextractor.reader.Mu2Reader import Mu2Reader

_curr_folder = os.path.dirname(os.path.abspath(__file__))


def test_with_vocal_section_starting_mid_measure():
    """
    Tests the result with the score of a vocal composition in which some of
    the lyrical lines start in middle of the measure
    """
    # inputs
    scorename = 'hicaz_humayun--beste--hafif--olmada_diller--abdulhalim_aga'

    txt_filename = os.path.join(_curr_folder, 'data', scorename + '.txt')

    # initialize the extractor
    extractor = SymbTrDataExtractor(
        extract_all_labels=False, melody_sim_thres=0.75, lyrics_sim_thres=0.75,
        get_recording_rels=False, print_warnings=True)

    # extract txt_data
    txt_data, is_data_valid = extractor.extract(txt_filename,
                                                symbtr_name=scorename)

    # compare with a previously saved result
    score_data_file = os.path.join(_curr_folder, 'data', scorename + '.json')
    saved_data = json.load(open(score_data_file))

    assert saved_data == txt_data and is_data_valid


def test_full_input():
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
    extractor = SymbTrDataExtractor(
        extract_all_labels=False, melody_sim_thres=0.75, lyrics_sim_thres=0.75,
        get_recording_rels=False, print_warnings=True)

    # extract txt_data
    txt_data, is_data_valid = extractor.extract(
        txt_filename, symbtr_name=scorename, mbid=mbid,
        segment_note_bound_idx=auto_seg_bounds)

    # extract mu2 header metadata
    mu2_header, header_row, is_header_valid = Mu2Reader.read_header(
        mu2_filename, symbtr_name=scorename)

    # merge
    data = SymbTrDataExtractor.merge(txt_data, mu2_header)
    is_valid = is_data_valid and is_header_valid

    # compare with a previously saved result
    score_data_file = os.path.join(_curr_folder, 'data', scorename + '.json')
    saved_data = json.load(open(score_data_file))

    assert saved_data == data and is_valid
