import os
import json
import warnings
from urlparse import urlparse
from makammusicbrainz.AudioMetadata import AudioMetadata
from makammusicbrainz.WorkMetadata import WorkMetadata
from musicbrainzngs import ResponseError


class MetadataExtractor(object):
    """

    """
    def __init__(self, get_recording_rels=False):
        self._audioMetadata = AudioMetadata(get_work_attributes=False,
                                            print_warnings=False)
        self._workMetadata = WorkMetadata(
            get_recording_rels=get_recording_rels, print_warnings=False)

    @property
    def get_recording_rels(self):
        return self._workMetadata.get_recording_rels

    @get_recording_rels.setter
    def get_recording_rels(self, value):
        self._workMetadata.get_recording_rels = value

    @staticmethod
    def get_slugs(scorename):
        splitted = scorename.split('--')
        return {'makam': splitted[0], 'form': splitted[1], 'usul': splitted[2],
                'name': splitted[3], 'composer': splitted[4]}

    def get_metadata(self, scorename, mbid=''):
        if mbid:
            data = self._get_metadata_from_musicbrainz(mbid)
        else:
            data = {'makam': {}, 'form': {}, 'usul': {}, 'name': {},
                    'composer': {}, 'lyricist': {}}

        data['symbtr'] = scorename

        slugs = MetadataExtractor.get_slugs(scorename)
        for attr in ['makam', 'form', 'usul']:
            self.add_attribute_slug(data, slugs, attr)

        if 'work' in data.keys():
            data['work']['symbtr_slug'] = slugs['name']
        elif 'recording' in data.keys():
            data['recording']['symbtr_slug'] = slugs['name']

        if 'composer' in data.keys():
            data['composer']['symbtr_slug'] = slugs['composer']

        # get and validate the attributes
        is_attr_meta_valid = self.validate_makam_form_usul(data, scorename)

        # get the tonic
        makam = MetadataExtractor._get_attr(data['makam']['symbtr_slug'],
                                            'makam')
        data['tonic'] = makam['karar_symbol']

        return data, is_attr_meta_valid

    @staticmethod
    def add_attribute_slug(data, slugs, attr):
        data[attr]['symbtr_slug'] = slugs[attr]
        data[attr]['attribute_key'] = MetadataExtractor. \
            _get_attribute_key(data[attr]['symbtr_slug'], attr)

    @staticmethod
    def validate_makam_form_usul(data, scorename):
        is_valid_list = []
        for attr in ['makam', 'form', 'usul']:
            is_valid_list.append(MetadataExtractor._validate_attribute(
                data, scorename, attr))

        return all(is_valid_list)

    @staticmethod
    def _get_attribute_key(attr_str, attr_type):
        attr_dict = MetadataExtractor.get_attribute_dict(attr_type)
        for attr_key, attr_val in attr_dict.iteritems():
            if attr_val['symbtr_slug'] == attr_str:
                return attr_key

    @staticmethod
    def _validate_attribute(data, scorename, attrib_name):
        score_attrib = data[attrib_name]

        attrib_dict = MetadataExtractor._get_attr(score_attrib['symbtr_slug'],
                                                  attrib_name)

        is_attribute_valid = MetadataExtractor._validate_slug(
            attrib_dict, score_attrib, scorename)

        is_attribute_valid = MetadataExtractor._validate_mu2_attribute(
            attrib_dict, is_attribute_valid, score_attrib, scorename)

        is_attribute_valid = MetadataExtractor._validate_mb_attribute(
            attrib_dict, is_attribute_valid, score_attrib, scorename)

        is_attribute_valid = MetadataExtractor._validate_mb_attribute_tag(
            attrib_dict, is_attribute_valid, score_attrib, scorename)

        return is_attribute_valid

    @staticmethod
    def _validate_mb_attribute(attrib_dict, is_attribute_valid, score_attrib,
                               scorename):
        if 'mb_attribute' in score_attrib.keys():  # work
            skip_makam_slug = ['12212212', '22222221', '223', '232223', '262',
                               '3223323', '3334', '14_4']
            if score_attrib['symbtr_slug'] in skip_makam_slug:
                warnings.warn(u'%s: The usul attribute is not stored in '
                              u'MusicBrainz.' % scorename)
            else:
                if not score_attrib['mb_attribute'] == \
                        attrib_dict['dunya_name']:
                    # dunya_names are (or should be) a superset of the
                    # musicbrainz attributes
                    is_attribute_valid = False
                    if score_attrib['mb_attribute']:
                        w_str = u'%s, %s: The MusicBrainz attribute does not' \
                                u' match.' % (scorename,
                                             score_attrib['mb_attribute'])
                        warnings.warn(w_str)
                    else:
                        warnings.warn(u'%s: The MusicBrainz attribute does'
                                      u' not exist.' % scorename)
        return is_attribute_valid

    @staticmethod
    def _validate_mu2_attribute(attrib_dict, is_attr_valid, score_attrib,
                                scorename):
        if 'mu2_name' in score_attrib.keys():  # work
            try:  # usul
                is_attr_valid, mu2_name = MetadataExtractor. \
                    _validate_mu2_usul(attrib_dict, is_attr_valid,
                                       score_attrib, scorename)

                if not mu2_name:  # no matching variant
                    is_attr_valid = False
                    warnings.warn(u'%s, %s: The Mu2 attribute does not match.'
                                  % (scorename, score_attrib['mu2_name']))

            except KeyError:  # makam, form
                is_attr_valid = MetadataExtractor._validate_mu2_makam_form(
                    attrib_dict, is_attr_valid, score_attrib, scorename)

        return is_attr_valid

    @staticmethod
    def _validate_mu2_makam_form(attrib_dict, is_attribute_valid, score_attrib,
                                 scorename):
        mu2_name = attrib_dict['mu2_name']
        if not score_attrib['mu2_name'] == mu2_name:
            is_attribute_valid = False
            warnings.warn(u'%s, %s: The Mu2 attribute does not match.'
                          % (scorename, score_attrib['mu2_name']))
        return is_attribute_valid

    @staticmethod
    def _validate_slug(attrib_dict, score_attrib, scorename):
        if 'symbtr_slug' in score_attrib.keys():
            if not score_attrib['symbtr_slug'] == attrib_dict['symbtr_slug']:
                warnings.warn(u'%s, %s: The slug does not match.'
                              % (scorename, score_attrib['symbtr_slug']))
                return False

        return True

    @staticmethod
    def _validate_mu2_usul(attrib_dict, is_attribute_valid,
                           score_attrib, scorename):
        mu2_name = ''
        for uv in attrib_dict['variants']:
            if uv['mu2_name'] == score_attrib['mu2_name']:
                mu2_name = uv['mu2_name']
                for v_key in ['mertebe', 'num_pulses']:
                    # found variant
                    if not uv[v_key] == score_attrib[v_key]:
                        is_attribute_valid = False

                        warnings.warn(u'%s, %s: The %s of the usul in the '
                                      u'score does not match.'
                                      % (scorename, uv['mu2_name'], v_key))

                    return is_attribute_valid, mu2_name

        assert mu2_name == '', 'The mu2 usul is not matched.'

    @staticmethod
    def _validate_mb_attribute_tag(attrib_dict, is_attribute_valid,
                                   score_attrib, scorename):
        if 'mb_tag' in score_attrib.keys():  # recording
            if not score_attrib['mb_tag'] in attrib_dict['mb_tag']:
                is_attribute_valid = False
                warnings.warn(u'%s, %s: The MusicBrainz tag does not match.'
                              % (scorename, score_attrib['mb_tag']))
        return is_attribute_valid

    @staticmethod
    def get_attribute_dict(attrstr):
        attrfile = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'makam_data', attrstr + '.json')
        return json.load(open(attrfile, 'r'))

    @staticmethod
    def validate_key_signature(key_signature, makam_slug, symbtr_name):
        attr_dict = MetadataExtractor.get_attribute_dict('makam')
        key_sig_makam = attr_dict[makam_slug]['key_signature']

        # the number of accidentals should be the same
        is_key_sig_valid = len(key_signature) == len(key_sig_makam)

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
            warnings.warn(u'%s: Key signature is different! %s -> %s'
                          % (symbtr_name, ' '.join(key_signature),
                             ' '.join(key_sig_makam)))

        return is_key_sig_valid

    @staticmethod
    def _get_attr(slug, attr_name):
        attr_dict = MetadataExtractor.get_attribute_dict(attr_name)

        for attr in attr_dict.values():
            if attr['symbtr_slug'] == slug:
                return attr

        # no match
        return {}

    def _get_metadata_from_musicbrainz(self, mbid):
        o = urlparse(mbid)
        if o.netloc:  # url supplied
            o_splitted = o.path.split('/')
            mbid = o_splitted[2]

        try:  # assume mbid is a work
            data = self._workMetadata.from_musicbrainz(mbid)
            data['work'] = {'title': data.pop("title", None),
                            'mbid': data.pop('mbid', None)}
        except ResponseError:  # assume mbid is a recording
            data = self._audioMetadata.from_musicbrainz(mbid)
            data['recording'] = {'title': data.pop("title", None),
                                 'mbid': data.pop('mbid', None)}
            if self.get_recording_rels:
                warnings.warn(u"Recording mbid is given. Ignored "
                              u"get_recording_rels boolean.")

        # scores should have one attribute per type
        for attr in ['makam', 'form', 'usul']:
            if len(data[attr]) == 1:
                data[attr] = data[attr][0]

        return data
