import warnings


class MusicBrainzMetadata(object):
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
        if 'mb_tag' in score_attrib.keys():  # recording
            if not score_attrib['mb_tag'] in attrib_dict['mb_tag']:
                is_attribute_valid = False
                warnings.warn(u'%s, %s: The MusicBrainz tag does not match.'
                              % (scorename, score_attrib['mb_tag']))
        return is_attribute_valid
