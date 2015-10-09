# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'

from section import *
from symbtr import *

import musicbrainzngs as mb
mb.set_useragent("SymbTr metadata", "0.1", "compmusic.upf.edu")

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

def getMetadata(source, get_recording_rels = False):
    try:  # only SymbTr-name is given
        data = ({'makam':dict(),'form':dict(),'usul':dict(),'name':dict(),
            'composer':dict(),'lyricist':dict()})
        scoreName_splitted = source.split('--')
        data['symbTr'] = source
        data['composer']['symbtr_slug'] = scoreName_splitted[4]
    except AttributeError:  # dictionary given, SymbTr name and mbid
        scoreName_splitted = source['name'].split('--')  
        data = getMetadataFromMusicBrainz(source['uuid'],
            get_recording_rels=get_recording_rels)
        data['symbTr'] = source['name']

    data['makam']['symbtr_slug'] = scoreName_splitted[0]
    data['form']['symbtr_slug'] = scoreName_splitted[1]
    data['usul']['symbtr_slug'] = scoreName_splitted[2]

    data['tonic'] = getTonic(data['makam']['symbtr_slug'])
    return data

def getTonic(makam):
    makam_tonic_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'makam.json')
    makam_tonic = json.load(open(makam_tonic_file, 'r'))

    return makam_tonic[makam]['kararSymbol']

def getMetadataFromMusicBrainz(uuid, get_recording_rels = False):
    if uuid['type'] == 'work':
        included_rels = (['artist-rels', 'recording-rels'] 
            if get_recording_rels else ['artist-rels'])
        
        work = mb.get_work_by_id(uuid['mbid'], 
            includes=included_rels)['work']

        work_attributes = work['attribute-list']
        data = ({'makam':dict(),'form':dict(),'usul':dict(),
            'work':{'mbid':uuid['mbid']},'composer':dict(),'lyricist':dict()})

        makam = [a['attribute'] for a in work_attributes if 'Makam' in a['type']]
        data['makam'] = {'name': makam[0] if len(makam) == 1 else makam}

        form = [a['attribute'] for a in work_attributes if 'Form' in a['type']]
        data['form'] = {'name': form[0] if len(form) == 1 else form}

        usul = [a['attribute'] for a in work_attributes if 'Usul' in a['type']]
        data['usul'] = {'name': usul[0] if len(usul) == 1 else usul}

        data['work']['title'] = work['title']

        for a in work['artist-relation-list']:
            if a['type'] == 'composer':
                data['composer'] = {'name':a['artist']['name'],'mbid':a['artist']['id']}
            elif a['type'] == 'lyricist':
                data['lyricist'] = {'name':a['artist']['name'],'mbid':a['artist']['id']}

        if get_recording_rels:
            data['recordings'] = []
            if work['recording-relation-list']:
                for r in work['recording-relation-list']:
                    rr = r['recording']
                    data['recordings'].append({'mbid':rr['id'], 'title':rr['title']})
            else:
                pass
    elif uuid['type'] == 'recording':
        rec = mb.get_recording_by_id(uuid['mbid'], includes=['artist-rels', 'tags'])['recording']

        data = ({'makam':[],'form':[],'usul':[],'recording':{'uuid':uuid['mbid']},'performers':[]})

        for t in rec['tag-list']:
            key, val = t['name'].split(': ')
            data[key].append({'name':val})

        data['makam'] = data['makam'][0] if len(data['makam']) == 1 else data['makam']
        data['form'] = data['form'][0] if len(data['form']) == 1 else data['form']
        data['usul'] = data['usul'][0] if len(data['usul']) == 1 else data['usul']

        for a in rec['artist-relation-list']:
            if a['type'] in ['instrument', 'vocal']:
                data['performers'].append({'name':a['artist']['name'],'mbid':a['artist']['id']})

        data['work']['title'] = rec['title']
    return data