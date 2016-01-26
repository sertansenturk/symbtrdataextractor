import os
import json
from urlparse import urlparse

import musicbrainzngs as mb
mb.set_useragent("SymbTr metadata", "0.2", "compmusic.upf.edu")

def getSlug(scorename):
    splitted = scorename.split('--')
    return {'makam':splitted[0], 'form':splitted[1], 'usul':splitted[2], 
        'name':splitted[3], 'composer':splitted[4]}

def getMetadata(scorename, mbid='', get_recording_rels=False):
    if mbid:
        data = getMetadataFromMusicBrainz(mbid,
            get_recording_rels=get_recording_rels)
    else:
        data = {'makam':{},'form':{},'usul':{},'name':{},
            'composer':{},'lyricist':{}}

    data['symbtr'] = scorename

    slugs = getSlug(scorename)
    data['makam']['symbtr_slug'] = slugs['makam']
    data['makam']['attribute_key'] = getAttributeKey(data['makam']['symbtr_slug'], 'makam')

    data['form']['symbtr_slug'] = slugs['form']
    data['form']['attribute_key'] = getAttributeKey(data['form']['symbtr_slug'], 'form')

    data['usul']['symbtr_slug'] = slugs['usul']
    data['usul']['attribute_key'] = getAttributeKey(data['usul']['symbtr_slug'], 'usul')

    if 'work' in data.keys():
        data['work']['symbtr_slug'] = slugs['name']
    elif 'recording' in data.keys():
        data['recording']['symbtr_slug'] = slugs['name']
    else:
        pass
    if 'composer' in data.keys():
        data['composer']['symbtr_slug'] = slugs['composer']

    # get and validate the attributes
    makam = getMakam(data['makam']['symbtr_slug'])
    isMakamValid = validateAttribute(data['makam'], makam, scorename)

    form = getForm(data['form']['symbtr_slug'])
    isFormValid = validateAttribute(data['form'], form, scorename)

    usul = getUsul(data['usul']['symbtr_slug'])
    isUsulValid = validateAttribute(data['usul'], usul, scorename)

    isMetadataValid = isMakamValid and isFormValid and isUsulValid

    # get the tonic
    data['tonic'] = makam['karar_symbol']

    return data, isMetadataValid

def getAttributeKey(attr_str, attr_type):
    attr_dict = getAttributeDict(attr_type)
    for attr_key, attr_val in attr_dict.iteritems():
        if attr_val['symbtr_slug'] == attr_str:
            return attr_key

def validateAttribute(score_attribute, attribute_dict, scorename):
    isAttributeValid = True  # initialize
    if 'symbtr_slug' in score_attribute.keys():
        if not score_attribute['symbtr_slug'] ==  attribute_dict['symbtr_slug']:
            isAttributeValid = False
            print("    " + scorename + ', ' + score_attribute['symbtr_slug'] + ''
                ': The slug does not match.')

    if 'mu2_name' in score_attribute.keys():  # work
        try:  # usul
            mu2_name = ''
            for uv in attribute_dict['variants']:
                if uv['mu2_name'] == score_attribute['mu2_name']:  # found variant
                    mu2_name = uv['mu2_name']
                    if not uv['mertebe'] == score_attribute['mertebe']:
                        isAttributeValid = False
                        print("    " + scorename + ', ' + uv['mu2_name'] + ''
                            ': The mertebe of the score does not match.')
                    if not uv['num_pulses'] == score_attribute['number_of_pulses']:
                        isAttributeValid = False
                        print("    " + scorename + ', ' + uv['mu2_name'] + ''
                            ': The number of pulses in an usul cycle does not match.')
            if not mu2_name:  # no matching variant
                isAttributeValid = False
                print("    " + scorename + ', ' + score_attribute['mu2_name'] + ''
                    ': The Mu2 attribute does not match.')
        except KeyError:  # makam, form
            mu2_name = attribute_dict['mu2_name']
            if not score_attribute['mu2_name'] == mu2_name:  
                isAttributeValid = False
                print("    " + scorename + ', ' + score_attribute['mu2_name'] + ''
                    ': The Mu2 attribute does not match.')
    
    if 'mb_attribute' in score_attribute.keys():  # work
        skip_makam_slug = ['12212212','22222221','223','232223','262','3223323','3334','14_4']
        if score_attribute['symbtr_slug'] in skip_makam_slug:
            print("    " + scorename + ': The usul attribute is not stored in MusicBrainz.')
        else:
            if not score_attribute['mb_attribute'] == attribute_dict['dunya_name']:  
                # dunya_names are (or should be) a superset of the musicbainz attributes 
                isAttributeValid = False
                if score_attribute['mb_attribute']:
                    print("    " + scorename + ', ' + score_attribute['mb_attribute'] + ''
                        ': The MusicBrainz attribute does not match.')
                else:
                    print("    " + scorename + ': The MusicBrainz attribute does not exist.')
    
    if 'mb_tag' in score_attribute.keys():  # recording
        if not score_attribute['mb_tag'] in attribute_dict['mb_tag']:  
            isAttributeValid = False
            print("    " + scorename + ', ' + score_attribute['mb_tag'] + ''
                ': The MusicBrainz tag does not match.')

    return isAttributeValid

def getAttributeDict(attrstr):
    attrfile = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makam_data', attrstr + '.json')
    return json.load(open(attrfile, 'r'))

def getMakam(makam_slug):
    makam_dict = getAttributeDict('makam')

    for makam in makam_dict.values():
        if makam['symbtr_slug'] == makam_slug:
            return makam
    
    # no match
    return {}

def getForm(form_slug):
    form_dict = getAttributeDict('form')
    for form in form_dict.values():
        if form['symbtr_slug'] == form_slug:
            return form

    # no match
    return {}

def getUsul(usul_slug):
    usul_dict = getAttributeDict('usul')

    for usul in usul_dict.values():
        if usul['symbtr_slug'] == usul_slug:
            return usul

    # no match
    return {}

def getMetadataFromMusicBrainz(mbid, get_recording_rels = False):
    o = urlparse(mbid)
    if o.netloc:  # url supplied
        o_splitted = o.path.split('/')
        if o_splitted[1] == 'work':
            data = getWorkMetadataFromMusicBrainz(o_splitted[2], get_recording_rels = False)
        elif o_splitted[1] == 'recording':
            if get_recording_rels:
                print "    " + "Recording mbid is given. Ignoring get_recording_rels input"
            data = getRecordingMetadataFromMusicBrainz(o_splitted[1])
    else:  # mbid supplied
        try:  # assume mbid is a work
            data = getWorkMetadataFromMusicBrainz(mbid, get_recording_rels = False)
        except:  # assume mbid is a recording
            if get_recording_rels:
                print "    " + "Recording mbid is given. Ignoring get_recording_rels input"
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
