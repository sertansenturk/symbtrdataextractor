import os
import json
from urlparse import urlparse
import musicbrainzngs as mb

mb.set_useragent("SymbTr metadata", "0.2", "compmusic.upf.edu")


class MetadataExtractor(object):
    """

    """
    def __init__(self, get_recording_rels=False):
        self.get_recording_rels = get_recording_rels

    @staticmethod
    def get_slugs(scorename):
        splitted = scorename.split('--')
        return {'makam': splitted[0], 'form': splitted[1], 'usul': splitted[2],
                'name': splitted[3], 'composer': splitted[4]}

    def get_metadata(self, scorename, mbid=''):
        if mbid:
            data = self.get_metadata_from_muscbrainz(mbid)
        else:
            data = {'makam': {}, 'form': {}, 'usul': {}, 'name': {},
                    'composer': {}, 'lyricist': {}}

        data['symbtr'] = scorename

        slugs = MetadataExtractor.get_slugs(scorename)
        data['makam']['symbtr_slug'] = slugs['makam']
        data['makam']['attribute_key'] = MetadataExtractor.get_attribute_key(
            data['makam']['symbtr_slug'], 'makam')

        data['form']['symbtr_slug'] = slugs['form']
        data['form']['attribute_key'] = MetadataExtractor.get_attribute_key(
            data['form']['symbtr_slug'], 'form')

        data['usul']['symbtr_slug'] = slugs['usul']
        data['usul']['attribute_key'] = MetadataExtractor.get_attribute_key(
            data['usul']['symbtr_slug'], 'usul')

        if 'work' in data.keys():
            data['work']['symbtr_slug'] = slugs['name']
        elif 'recording' in data.keys():
            data['recording']['symbtr_slug'] = slugs['name']
        else:
            pass
        if 'composer' in data.keys():
            data['composer']['symbtr_slug'] = slugs['composer']

        # get and validate the attributes
        makam = MetadataExtractor.get_makam(data['makam']['symbtr_slug'])
        is_makam_valid = MetadataExtractor.validate_attribute(
            data['makam'], makam, scorename)

        form = MetadataExtractor.get_form(data['form']['symbtr_slug'])
        is_form_valid = MetadataExtractor.validate_attribute(
            data['form'], form, scorename)

        usul = MetadataExtractor.get_usul(data['usul']['symbtr_slug'])
        is_usul_valid = MetadataExtractor.validate_attribute(
            data['usul'], usul, scorename)

        is_metadata_valid = is_makam_valid and is_form_valid and is_usul_valid

        # get the tonic
        data['tonic'] = makam['karar_symbol']

        return data, is_metadata_valid

    @staticmethod
    def get_attribute_key(attr_str, attr_type):
        attr_dict = MetadataExtractor.get_attribute_dict(attr_type)
        for attr_key, attr_val in attr_dict.iteritems():
            if attr_val['symbtr_slug'] == attr_str:
                return attr_key

    @staticmethod
    def validate_attribute(score_attrib, attrib_dict, scorename):
        is_attribute_valid = True  # initialize
        if 'symbtr_slug' in score_attrib.keys():
            if not score_attrib['symbtr_slug'] == attrib_dict['symbtr_slug']:
                is_attribute_valid = False
                print("    " + scorename + ', ' + score_attrib['symbtr_slug'] +
                      ': The slug does not match.')

        if 'mu2_name' in score_attrib.keys():  # work
            try:  # usul
                mu2_name = ''
                for uv in attrib_dict['variants']:
                    if uv['mu2_name'] == score_attrib['mu2_name']:
                        # found variant
                        mu2_name = uv['mu2_name']
                        if not uv['mertebe'] == score_attrib['mertebe']:
                            is_attribute_valid = False
                            print("    " + scorename + ', ' + uv['mu2_name'] +
                                  ': The mertebe of the score does not match.')
                        if not uv['num_pulses'] == \
                                score_attrib['number_of_pulses']:
                            is_attribute_valid = False
                            print("    " + scorename + ', ' + uv['mu2_name'] +
                                  ': The number of pulses in an usul cycle '
                                  'does not match.')
                if not mu2_name:  # no matching variant
                    is_attribute_valid = False
                    print("    " + scorename + ', ' +
                          score_attrib['mu2_name'] +
                          ': The Mu2 attribute does not match.')
            except KeyError:  # makam, form
                mu2_name = attrib_dict['mu2_name']
                if not score_attrib['mu2_name'] == mu2_name:
                    is_attribute_valid = False
                    print("    " + scorename + ', ' +
                          score_attrib['mu2_name'] +
                          ': The Mu2 attribute does not match.')

        if 'mb_attribute' in score_attrib.keys():  # work
            skip_makam_slug = ['12212212', '22222221', '223', '232223', '262',
                               '3223323', '3334', '14_4']
            if score_attrib['symbtr_slug'] in skip_makam_slug:
                print("    " + scorename + ': The usul attribute is not '
                                           'stored in MusicBrainz.')
            else:
                if not score_attrib['mb_attribute'] == \
                        attrib_dict['dunya_name']:
                    # dunya_names are (or should be) a superset of the
                    # musicbrainz attributes
                    is_attribute_valid = False
                    if score_attrib['mb_attribute']:
                        print("    " + scorename + ', ' +
                              score_attrib['mb_attribute'] +
                              ': The MusicBrainz attribute does not match.')
                    else:
                        print("    " + scorename + ': The MusicBrainz '
                                                   'attribute does not exist.')

        if 'mb_tag' in score_attrib.keys():  # recording
            if not score_attrib['mb_tag'] in attrib_dict['mb_tag']:
                is_attribute_valid = False
                print("    " + scorename + ', ' + score_attrib['mb_tag'] +
                      ': The MusicBrainz tag does not match.')

        return is_attribute_valid

    @staticmethod
    def get_attribute_dict(attrstr):
        attrfile = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'makam_data', attrstr + '.json')
        return json.load(open(attrfile, 'r'))

    @staticmethod
    def get_key_signature_from_makam_slug(makam_slug):
        attr_dict = MetadataExtractor.get_attribute_dict('makam')
        return attr_dict[makam_slug]['key_signature']

    @staticmethod
    def validate_key_signature(key_signature, makam_slug, symbtr_name):
        attr_dict = MetadataExtractor.get_attribute_dict('makam')
        key_sig_makam = attr_dict[makam_slug]['key_signature']
        is_key_sig_valid = True
        # the number of accidentals should be the same
        if len(key_signature) != len(key_sig_makam):
            is_key_sig_valid = False

        # the sequence should be the same, allow a single comma deviation
        # due to AEU theory and practice mismatch
        for k1, k2 in zip(key_signature, key_sig_makam):
            if k1 == k2:  # same note
                pass
            elif k1[:3] == k2[:3]:  # same note symbol
                if abs(int(k1[3:]) - int(k2[3:])) <= 1:  # 1 comma deviation
                    pass
                else:  # more than one comma deviation
                    is_key_sig_valid = False
            else:  # different notes
                is_key_sig_valid = False

        if not is_key_sig_valid:
            print("    " + symbtr_name +
                  ': Key signature is different! ' +
                  ' '.join(key_signature) +
                  ' -> ' + ' '.join(key_sig_makam))

        return is_key_sig_valid

    @staticmethod
    def get_makam(makam_slug):
        makam_dict = MetadataExtractor.get_attribute_dict('makam')

        for makam in makam_dict.values():
            if makam['symbtr_slug'] == makam_slug:
                return makam

        # no match
        return {}

    @staticmethod
    def get_form(form_slug):
        form_dict = MetadataExtractor.get_attribute_dict('form')
        for form in form_dict.values():
            if form['symbtr_slug'] == form_slug:
                return form

        # no match
        return {}

    @staticmethod
    def get_usul(usul_slug):
        usul_dict = MetadataExtractor.get_attribute_dict('usul')

        for usul in usul_dict.values():
            if usul['symbtr_slug'] == usul_slug:
                return usul

        # no match
        return {}

    def get_metadata_from_muscbrainz(self, mbid):
        data = {}  # initialize

        o = urlparse(mbid)
        if o.netloc:  # url supplied
            o_splitted = o.path.split('/')
            if o_splitted[1] == 'work':
                data = self.get_work_metadata_from_musicbrainz(o_splitted[2])
            elif o_splitted[1] == 'recording':
                if self.get_recording_rels:
                    print("    " + "Recording mbid is given. Ignoring "
                                   "get_recording_rels input")
                data = \
                    MetadataExtractor.get_recording_metadata_from_musicbrainz(
                        o_splitted[1])
        else:  # mbid supplied
            try:  # assume mbid is a work
                data = self.get_work_metadata_from_musicbrainz(mbid)
            except:  # assume mbid is a recording
                if self.get_recording_rels:
                    print("    " + "Recording mbid is given. Ignoring "
                                   "get_recording_rels input")
                data = \
                    MetadataExtractor.get_recording_metadata_from_musicbrainz(
                        mbid)
        return data

    def get_work_metadata_from_musicbrainz(self, mbid):
        included_rels = (['artist-rels', 'recording-rels']
                         if self.get_recording_rels else ['artist-rels'])

        work = mb.get_work_by_id(mbid, includes=included_rels)['work']

        data = ({'makam': {}, 'form': {}, 'usul': {},
                 'work': {'mbid': mbid}, 'composer': {}, 'lyricist': {}})

        data['work']['title'] = work['title']

        if 'attribute-list' in work.keys():
            w_attrb = work['attribute-list']

            makam = [a['attribute'] for a in w_attrb if 'Makam' in a['type']]
            data['makam'] = {'mb_attribute': makam[0]
                             if len(makam) == 1 else makam}

            form = [a['attribute'] for a in w_attrb if 'Form' in a['type']]
            data['form'] = \
                {'mb_attribute': form[0] if len(form) == 1 else form}

            usul = [a['attribute'] for a in w_attrb if 'Usul' in a['type']]
            data['usul'] = \
                {'mb_attribute': usul[0] if len(usul) == 1 else usul}

        if 'language' in work.keys():
            data['language'] = work['language']

        if 'artist-relation-list' in work.keys():
            for a in work['artist-relation-list']:
                if a['type'] == 'composer':
                    data['composer'] = {'name': a['artist']['name'],
                                        'mbid': a['artist']['id']}
                elif a['type'] == 'lyricist':
                    data['lyricist'] = {'name': a['artist']['name'],
                                        'mbid': a['artist']['id']}

        if self.get_recording_rels:
            data['recordings'] = []
            if 'recording-relation-list' in work.keys():
                for r in work['recording-relation-list']:
                    rr = r['recording']
                    data['recordings'].append({'mbid': rr['id'],
                                               'title': rr['title']})

        return data

    @staticmethod
    def get_recording_metadata_from_musicbrainz(mbid):
        rec = mb.get_recording_by_id(
            mbid, includes=['artist-rels', 'tags'])['recording']

        data = ({'makam': [], 'form': [], 'usul': [],
                 'recording': {'mbid': mbid}, 'performers': []})

        for t in rec['tag-list']:
            key, val = t['name'].split(': ')
            data[key].append({'mb_tag': val})

        data['makam'] = \
            data['makam'][0] if len(data['makam']) == 1 else data['makam']
        data['form'] = \
            data['form'][0] if len(data['form']) == 1 else data['form']
        data['usul'] = \
            data['usul'][0] if len(data['usul']) == 1 else data['usul']

        for a in rec['artist-relation-list']:
            if a['type'] in ['instrument', 'vocal']:
                data['performers'].append({'name': a['artist']['name'],
                                           'mbid': a['artist']['id']})

        data['recording']['title'] = rec['title']

        return data
