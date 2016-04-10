import warnings
from musicbrainzngs import ResponseError
from urlparse import urlparse
from makammusicbrainz.AudioMetadata import AudioMetadata
from makammusicbrainz.WorkMetadata import WorkMetadata


class MBMetadata(object):
    def __init__(self, get_recording_rels=False):
        self._audioMetadata = AudioMetadata(
            get_work_attributes=False, print_warnings=False)
        self._workMetadata = WorkMetadata(
            get_recording_rels=get_recording_rels, print_warnings=False)

    @property
    def get_recording_rels(self):
        return self._workMetadata.get_recording_rels

    @get_recording_rels.setter
    def get_recording_rels(self, value):
        self._workMetadata.get_recording_rels = value

    def get_metadata_from_musicbrainz(self, mbid):
        if mbid is None:  # empty mbid
            return {'makam': {}, 'form': {}, 'usul': {}, 'name': {},
                    'composer': {}, 'lyricist': {}}
        else:
            mbid = self._parse_mbid(mbid)
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

            self._add_mb_attributes(data)

            return data

    @staticmethod
    def _add_mb_attributes(data):
        # scores should have one attribute per type
        for attr in ['makam', 'form', 'usul']:
            if attr in data:
                data[attr] = data[attr][0]

    @staticmethod
    def _parse_mbid(mbid):
        o = urlparse(mbid)

        # if the url is given get the mbid, which is the last field
        o_splitted = o.path.split('/')
        mbid = o_splitted[-1]

        return mbid

    @staticmethod
    def validate_mb_attribute(attrib_dict, score_attrib, scorename):
        is_attribute_valid = True
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
    def validate_mb_attribute_tag(attrib_dict, score_attrib, scorename):
        is_attribute_valid = True
        has_mb_tag = 'mb_tag' in score_attrib.keys()
        if has_mb_tag and score_attrib['mb_tag'] not in attrib_dict['mb_tag']:
            is_attribute_valid = False
            warnings.warn(u'{0!s}, {1!s}: The MusicBrainz tag does not '
                          u'match.'.format(scorename,
                                           score_attrib['mb_tag']))
        return is_attribute_valid
