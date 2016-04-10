import warnings


class Mu2Metadata(object):
    @staticmethod
    def validate_mu2_attribute(score_attrib, attrib_dict, scorename):

        is_attr_valid = True
        if 'mu2_name' in score_attrib.keys():  # work
            try:  # usul
                mu2_name, is_attr_valid = Mu2Metadata._validate_mu2_usul(
                    score_attrib, attrib_dict, scorename)

                if not mu2_name:  # no matching variant
                    is_attr_valid = False
                    warnings.warn(u'{0!s}, {1!s}: The Mu2 attribute does not '
                                  u'match.'.format(scorename,
                                                   score_attrib['mu2_name']))

            except KeyError:  # makam, form
                is_attr_valid = Mu2Metadata._validate_mu2_makam_form(
                    score_attrib, attrib_dict, scorename)

        return is_attr_valid

    @staticmethod
    def _validate_mu2_makam_form(score_attrib, attrib_dict, scorename):
        mu2_name = attrib_dict['mu2_name']
        if not score_attrib['mu2_name'] == mu2_name:
            warnings.warn(u'{0!s}, {1!s}: The Mu2 attribute does not match.'.
                          format(scorename, score_attrib['mu2_name']))
            return False

        return True

    @staticmethod
    def _validate_mu2_usul(score_attrib, attrib_dict, scorename):
        mu2_name = ''
        is_usul_valid = True
        for uv in attrib_dict['variants']:
            if uv['mu2_name'] == score_attrib['mu2_name']:
                mu2_name = uv['mu2_name']
                for v_key in ['mertebe', 'num_pulses']:
                    # found variant
                    if not uv[v_key] == score_attrib[v_key]:
                        is_usul_valid = False

                        warnings.warn(
                            u'{0:s}, {1:s}: The {2:s} of the usul in the '
                            u'score does not match.'
                            .format(scorename, uv['mu2_name'], v_key))

                    return is_usul_valid, mu2_name

        return mu2_name, is_usul_valid
