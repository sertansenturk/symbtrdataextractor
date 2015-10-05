# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
from symbtr import *

#dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

def extract(scorefile, symbtrname, useMusicBrainz = False, extractAllLabels = False, 
    slugify = True, lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
    # get the data in the score name, works if the name of the 
    # file has not been changed
    symbtrdict = symbtrname.split('--')
    data = dict()
    try:
        [data['makam'], data['form'], data['usul'], data['name'], 
            data['composer']] = symbtrname.split('--')
        data['tonic'] = getTonic(data['makam'])

        if isinstance(data['composer'], list):
            print 'The symbtrname is not in the form "makam--form--usul--name--composer"'
            data = dict()
    except ValueError:
        print 'The symbtrname is not in the form "makam--form--usul--name--composer"'
        
    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    if extension == ".txt":
        score = readTxtScore(scorefile)
    elif extension == ".xml":
        score = readXMLScore(scorefile)
    elif extension == ".mu2":
        score = readMu2Score(scorefile)
    else:
        print "Unknown format"
        return -1

    data['sections'] = extractSection(score, slugify=slugify, 
        extractAllLabels=extractAllLabels,lyrics_sim_thres=lyrics_sim_thres,
        melody_sim_thres=melody_sim_thres)

    if useMusicBrainz:
        extractSectionFromMusicBrainz

    return {'data': data}

def getTonic(makam):
    makam_tonic_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'makam.json')
    makam_tonic = json.load(open(makam_tonic_file, 'r'))

    return makam_tonic[makam]['kararSymbol']
