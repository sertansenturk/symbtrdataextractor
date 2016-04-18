from symbtrdataextractor.metadata.musicbrainz import MusicBrainzMetadata
import json
import os

_curr_folder = os.path.dirname(os.path.abspath(__file__))


def test_musicbrainz_recording_request():
    mbid = '5cbd1b2d-d1ef-4627-a4d4-135a95de2b69'
    rec = 'http://musicbrainz.org/recording/' + mbid

    mbm = MusicBrainzMetadata()

    saved_data_file = os.path.join(_curr_folder, 'data', mbid + '.json')
    save_data = json.load(open(saved_data_file, 'r'))

    r_data = mbm.crawl_musicbrainz(rec)

    assert r_data == save_data, u'Crawling {0:s} yields a different ' \
                                u'result '.format(rec)
