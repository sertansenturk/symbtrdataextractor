import os
import json

import musicbrainzngs as mb
mb.set_useragent("SymbTr metadata", "0.2", "compmusic.upf.edu")

def getMetadata(scorename, mbid='', get_recording_rels=False):
    isMetadataValid = True  # initialize valid metadata boolean flag
    if mbid:
        data = getMetadataFromMusicBrainz(mbid,
            get_recording_rels=get_recording_rels)
    else:
        data = {'makam':{},'form':{},'usul':{},'name':{},
            'composer':{},'lyricist':{}}

    data['symbtr'] = scorename

    scoreName_splitted = scorename.split('--')
    data['makam']['symbtr_slug'] = scoreName_splitted[0]
    data['form']['symbtr_slug'] = scoreName_splitted[1]
    data['usul']['symbtr_slug'] = scoreName_splitted[2]

    if 'composer' in data.keys():
        data['composer']['symbtr_slug'] = scoreName_splitted[4]

    # get the makam & validate
    makam = getMakam(data['makam']['symbtr_slug'])
    if 'symbtr_slug' in makam.keys():
        if not makam['symbtr_slug'] == data['makam']['symbtr_slug']:
            isMetadataValid = False
            print scorename + ': The makam slug and the filename makam slug does not match'
        if mbid:
            if ('mb_attribute' in data['makam'].keys() and  # work
                not data['makam']['mb_attribute'] == makam['dunya_name']):  
                # (dunya_names are (or should be) a superset of the musicbainz attributes)
                isMetadataValid = False
                print scorename + ': The makam slug in the filename and the MusicBrainz/Dunya name does not match.'
            elif ('mb_tag' in data['makam'].keys() and  # recording
                not data['makam']['mb_tag'] in makam['mb_tag']):  
                isMetadataValid = False
                print scorename + ': The makam slug in the filename and the MusicBrainz tag does not match.'
        # tonic
        data['tonic'] = makam['karar_symbol']
    else:
        isMetadataValid = False
        print scorename + ': The makam slug is not known'

    # get the form & validate
    form = getForm(data['form']['symbtr_slug'])
    if 'symbtr_slug' in form.keys():
        if not form['symbtr_slug'] == data['form']['symbtr_slug']:
            isMetadataValid = False
            print scorename + ': The form slug and the filename form slug does not match'
        if mbid:
            if ('mb_attribute' in data['form'].keys() and  # work
                not data['form']['mb_attribute'] == form['dunya_name']):  
                # (dunya_names are (or should be) a superset of the musicbainz attributes)
                isMetadataValid = False
                print scorename + ': The form slug in the filename and the MusicBrainz/Dunya name does not match.'
            elif ('mb_tag' in data['form'].keys() and  # recording
                not data['form']['mb_tag'] in form['mb_tag']):  
                isMetadataValid = False
                print scorename + ': The form slug in the filename and the MusicBrainz tag does not match.'
    else:
        isMetadataValid = False
        print scorename + ': The form slug is not known'

    # get the usul & validate
    usul = getUsul(data['usul']['symbtr_slug'])
    if 'symbtr_slug' in usul.keys():
        if not usul['symbtr_slug'] == data['usul']['symbtr_slug']:
            isMetadataValid = False
            print scorename + ': The usul slug and the filename usul slug does not match'
        # skip usul labels, which are not actualy a definite usul but a specific rhythmic structure 
        # in folk music, and hence not in musicbrainz
        usuls_not_in_mb = ['12212212', '22222221', '223', '232223', '262', '3223323', '3334', '14_4']   
        if usul['symbtr_slug'] not in usuls_not_in_mb and mbid:
            if ('mb_attribute' in data['usul'].keys() and  # work
                not data['usul']['mb_attribute'] == usul['dunya_name']):  
                # (dunya_names are (or should be) a superset of the musicbainz attributes)
                isMetadataValid = False
                print scorename + ': The usul slug in the filename and the MusicBrainz/Dunya name does not match.'
            elif ('mb_tag' in data['usul'].keys() and  # recording
                not data['usul']['mb_tag'] in usul['mb_tag']):  
                isMetadataValid = False
                print scorename + ': The usul slug in the filename and the MusicBrainz tag does not match.'
    else:
        isMetadataValid = False
        print scorename + ': The form slug is not known'

    return data, isMetadataValid

def getMakam(makam_slug):
    makam_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'makam.json')
    makam_dict = json.load(open(makam_file, 'r'))

    for makam in makam_dict.values():
        if makam['symbtr_slug'] == makam_slug:
            return makam
    
    # no match
    return {}

def getForm(form_slug):
    form_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'form.json')
    form_dict = json.load(open(form_file, 'r'))

    for form in form_dict.values():
        if form['symbtr_slug'] == form_slug:
            return form

    # no match
    return {}

def getUsul(usul_slug):
    usul_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', 'usul.json')
    usul_dict = json.load(open(usul_file, 'r'))

    for usul in usul_dict.values():
        if usul['symbtr_slug'] == usul_slug:
            return usul

    # no match
    return {}

def getMetadataFromMusicBrainz(mbid, get_recording_rels = False):
    try:  # assume mbid is a work
        data = getWorkMetadataFromMusicBrainz(mbid, get_recording_rels = False)
    except:  # assume mbid is a recording
        if get_recording_rels:
            print "Recording mbid is given. Ignoring get_recording_rels input"
        data = getRecordingMetadataFromMusicBrainz(mbid)
    return data

def getWorkMetadataFromMusicBrainz(mbid, get_recording_rels = False):
    included_rels = (['artist-rels', 'recording-rels'] 
        if get_recording_rels else ['artist-rels'])
    
    work = mb.get_work_by_id(mbid, includes=included_rels)['work']

    data = ({'makam':{},'form':{},'usul':{},
        'work':{'mbid':mbid},'composer':{},'lyricist':{}})

    data['work']['title'] = work['title']

    if 'attribute-list' in work.keys():
        w_attrb = work['attribute-list']

        makam = [a['attribute'] for a in w_attrb if 'Makam' in a['type']]
        data['makam'] = {'mb_attribute': makam[0] if len(makam) == 1 else makam}

        form = [a['attribute'] for a in w_attrb if 'Form' in a['type']]
        data['form'] = {'mb_attribute': form[0] if len(form) == 1 else form}

        usul = [a['attribute'] for a in w_attrb if 'Usul' in a['type']]
        data['usul'] = {'mb_attribute': usul[0] if len(usul) == 1 else usul}

    if 'language' in work.keys():
        data['language'] = work['language']

    if 'artist-relation-list' in work.keys():
        for a in work['artist-relation-list']:
            if a['type'] == 'composer':
                data['composer'] = {'name':a['artist']['name'],'mbid':a['artist']['id']}
            elif a['type'] == 'lyricist':
                data['lyricist'] = {'name':a['artist']['name'],'mbid':a['artist']['id']}

    if get_recording_rels:
        data['recordings'] = []
        if 'recording-relation-list' in work.keys():
            for r in work['recording-relation-list']:
                rr = r['recording']
                data['recordings'].append({'mbid':rr['id'], 'title':rr['title']})

    return data

def getRecordingMetadataFromMusicBrainz(mbid):
    rec = mb.get_recording_by_id(mbid, includes=['artist-rels', 'tags'])['recording']

    data = ({'makam':[],'form':[],'usul':[],'recording':{'mbid':mbid},'performers':[]})

    for t in rec['tag-list']:
        key, val = t['name'].split(': ')
        data[key].append({'mb_tag':val})

    data['makam'] = data['makam'][0] if len(data['makam']) == 1 else data['makam']
    data['form'] = data['form'][0] if len(data['form']) == 1 else data['form']
    data['usul'] = data['usul'][0] if len(data['usul']) == 1 else data['usul']

    for a in rec['artist-relation-list']:
        if a['type'] in ['instrument', 'vocal']:
            data['performers'].append({'name':a['artist']['name'],'mbid':a['artist']['id']})

    data['recording']['title'] = rec['title']

    return data
