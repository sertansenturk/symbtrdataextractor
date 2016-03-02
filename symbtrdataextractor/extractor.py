from section import *
from phrase import *
from symbtrreader import *
from metadata import *
from rhythm import *
import os


def extract(scorefile, symbtrname='', mbid='', seg_note_idx=[],
            extract_all_labels=False, lyrics_sim_thres=0.25,
            melody_sim_thres=0.25, get_recording_rels=False,
            print_warnings=True):
    # get the metadata
    if not symbtrname:
        symbtrname = os.path.splitext(os.path.basename(scorefile))[0]
    data, isMetadataValid = getMetadata(symbtrname, mbid=mbid,
                                        get_recording_rels=get_recording_rels)

    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    # read the score
    if extension == ".txt":
        score, is_score_content_valid = readTxtScore(scorefile)
    elif extension == ".xml":
        score, is_score_content_valid = readXMLScore(scorefile)
    elif extension == ".mu2":
        score, is_score_content_valid = readMu2Score(scorefile)
    else:
        raise IOError("Unknown format")

    data['duration'] = {'value': sum(score['duration']) * 0.001, 'unit': 'second'}
    data['number_of_notes'] = len(score['duration'])

    data['sections'], is_section_data_valid = extractSection(score, symbtrname,
                                                             extract_all_labels=extract_all_labels,
                                                             lyrics_sim_thres=lyrics_sim_thres,
                                                             melody_sim_thres=melody_sim_thres,
                                                             print_warnings=print_warnings)

    anno_phrase = extractAnnotatedPhrase(score, sections=data['sections'],
                                         lyrics_sim_thres=lyrics_sim_thres, melody_sim_thres=melody_sim_thres)
    auto_phrase = extractAutoSegPhrase(score, sections=data['sections'],
                                       seg_note_idx=seg_note_idx, lyrics_sim_thres=lyrics_sim_thres,
                                       melody_sim_thres=melody_sim_thres)

    data['rhythmic_structure'] = extractRhythmicStructure(score)

    data['phrases'] = {'annotated': anno_phrase, 'automatic': auto_phrase}
    is_data_valid = all([isMetadataValid, is_section_data_valid, is_score_content_valid])

    return data, is_data_valid


def merge(txt_data, mu2_data, verbose=True):
    '''
    Merge the extracted data, precedence goes to key value pairs in latter dicts.
    '''
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
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in data_dicts:
        dict_cp = dictionary.copy()
        for key, val in dict_cp.iteritems():
            if not key in result.keys():
                result[key] = val
            elif not isinstance(result[key], dict):
                if not result[key] == val:
                    # overwrite
                    print '   ' + key + ' already exists! Overwriting...'
                    result[key] = val
            else:
                result[key] = dictmerge(result[key], val)

    return result
