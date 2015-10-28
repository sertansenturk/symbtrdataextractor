# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
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

    return data
