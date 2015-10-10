# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
from symbtr import *
from metadata import *

def extract(scorefile, metadata_source, extractAllLabels = False, 
    lyrics_sim_thres = 0.25, melody_sim_thres = 0.25, 
    get_recording_rels = False):
        
    # get the metadata
    data = getMetadata(metadata_source, get_recording_rels = 
        get_recording_rels)

    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    # read the scre
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

    return data
