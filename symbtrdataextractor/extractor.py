# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
from symbtr import *

def extract(scorefile, metadata_source, extractAllLabels = False, 
    slugify = True, lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
        
    # get the metadata
    data = getMetadata(metadata_source)

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
        print "Unknown format"
        return -1

    data['sections'] = extractSection(score, slugify=slugify, 
        extractAllLabels=extractAllLabels,lyrics_sim_thres=lyrics_sim_thres,
        melody_sim_thres=melody_sim_thres)

    return {'data': data}

def getMetadata(source):
    data = dict()
    try:  # SymbTr name
        [data['makam'], data['form'], data['usul'], data['name'], 
            data['composer']] = source.split('--')
        data['tonic'] = getTonic(data['makam'])
    except ValueError:  # musicbrainz id
        try:
            data = getMetadataFromMusicBrainz(source)
        except ValueError:
            print('The metadata source input should either be the symbtrname '
                '(makam--form--usul--name--composer) or MusicBrainz work id')
    return data

def getTonic(makam):
    makam_tonic_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'makam.json')
    makam_tonic = json.load(open(makam_tonic_file, 'r'))

    return makam_tonic[makam]['kararSymbol']

def getMetadataFromMusicBrainz(work_mbid):
    pass
