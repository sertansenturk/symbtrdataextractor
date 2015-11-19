# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
from phrase import *
from symbtrreader import *
from metadata import *
import os

def extract(scorefile, symbtrname='', mbid='', 
    extractAllLabels=False, lyrics_sim_thres=0.25, 
    melody_sim_thres=0.25, get_recording_rels=False):
    
    # get the metadata
    if not symbtrname:
        symbtrname = os.path.splitext(os.path.basename(scorefile))[0]
    data = getMetadata(symbtrname, mbid=mbid,
        get_recording_rels=get_recording_rels)

    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    # read the score
    if extension == ".txt":
        score = readTxtScore(scorefile)
    elif extension == ".xml":
        score = readXMLScore(scorefile)
    elif extension == ".mu2":
        score = readMu2Score(scorefile)
    else:
        raise IOError("Unknown format")

    data['sections'] = extractSection(score, extractAllLabels=extractAllLabels,
        lyrics_sim_thres=lyrics_sim_thres, melody_sim_thres=melody_sim_thres)

    data['phrases'] = {'annotated':extractAnnotatedPhrase(score, 
        sections=data['sections'], lyrics_sim_thres=lyrics_sim_thres, 
        melody_sim_thres=melody_sim_thres)}

    return data

def merge(*data_dicts):
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
                # overwrite
                print '   ' + key + 'already exists! Overwriting...'
                result[key] = val
            else:
                result[key] = merge(result[key], val)

    return result

