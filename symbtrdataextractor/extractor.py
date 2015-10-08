# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
from symbtr import *

import compmusic
import compmusic.dunya.makam as mk
compmusic.dunya.conn.set_token('b24315d957c8b5bb5fc78abed762764b2d34ca62')

def extract(scorefile, metadata_source, extractAllLabels = False, 
    lyrics_sim_thres = 0.25, melody_sim_thres = 0.25):
        
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
        raise IOError("Unknown format")

    data['sections'] = extractSection(score, extractAllLabels=extractAllLabels,
        lyrics_sim_thres=lyrics_sim_thres, melody_sim_thres=melody_sim_thres)

    return data

def getMetadata(source):
    data = dict()
    try:  # SymbTr name
        [data['makam'], data['form'], data['usul'], data['name'], 
            data['composer']] = source.split('--')
    except ValueError:  # musicbrainz id
        try:
            data = getMetadataFromMusicBrainz(source)
        except ValueError:
            print('The metadata source input should either be the symbtrname '
                '(makam--form--usul--name--composer) or MusicBrainz work id')
    data['tonic'] = getTonic(data['makam'])
    return data

def getTonic(makam):
    makam_tonic_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'makam.json')
    makam_tonic = json.load(open(makam_tonic_file, 'r'))

    return makam_tonic[makam]['kararSymbol']

def getMetadataFromMusicBrainz(work_mbid):
    work = mk.get_work(work_mbid)
    data = dict()

    data['makam'] = (work['makams'][0] if len(work['makams']) == 1
        else work['makams'])
    data['form'] = (work['forms'][0] if len(work['forms']) == 1
        else work['forms'])
    data['usul'] = (work['usuls'][0] if len(work['usuls']) == 1
        else work['usuls'])
    data['name'] = work['title']
    data['composer'] = (work['composers'][0] if len(work['composers']) == 1
        else work['composers'])
    data['mbid'] = work_mbid

    return data