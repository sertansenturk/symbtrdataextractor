[![DOI](https://zenodo.org/badge/21104/sertansenturk/symbtrdataextractor.svg)](https://zenodo.org/badge/latestdoi/21104/sertansenturk/symbtrdataextractor) [![Build Status](https://travis-ci.org/sertansenturk/symbtrdataextractor.svg?branch=master)](https://travis-ci.org/sertansenturk/symbtrdataextractor) [![codecov.io](https://codecov.io/github/sertansenturk/symbtrdataextractor/coverage.svg?branch=master)](https://codecov.io/github/sertansenturk/symbtrdataextractor?branch=master) [![Code Climate](https://codeclimate.com/github/sertansenturk/symbtrdataextractor/badges/gpa.svg)](https://codeclimate.com/github/sertansenturk/symbtrdataextractor) [![GitHub version](https://badge.fury.io/gh/sertansenturk%2Fsymbtrdataextractor.svg)](https://badge.fury.io/gh/sertansenturk%2Fsymbtrdataextractor)

symbtrdataextractor
===========
Python tools for extracting relevant (meta)data from SymbTr-scores

Introduction
------------

This repository contains to algorithms to extract metadata, related music knowledge and section information from [SymbTr-scores](https://github.com/MTG/SymbTr) and related information sources. 

Currently you can:
- Obtain the makam, usul, form, name and composer of the given SymbTr score
- Extract section boundaries from both the implicit and explicit section information given in the SymbTr scores
- Extract annotated phrase boundaries in the SymbTr scores
- Add user provided segment boundaries in the SymbTr scores
- Analyse the melody and the lyrics of the sections, phrase annotations and user provided segments, and apply semiotic labels
- Query relevant metadata from MusicBrainz, if the [MBID](https://musicbrainz.org/doc/MusicBrainz_Identifier) is supplied.
- Read the metadata stored in the header of the mu2 file.

If you are using this code for academic purposes please cite the software as:

> Sertan Senturk. (2016). symbtrdataextractor: symbtrdataextractor v2.0.0. Zenodo. 10.5281/zenodo.50033

Usage
----------
##### Extracting (meta)data from the txt-score:

```python
from symbtrdataextractor.dataextractor import DataExtractor

extractor = DataExtractor(
    melody_sim_thres=0.7, lyrics_sim_thres=0.7, save_structure_sim=True,
    extract_all_labels=False, crop_consec_bounds=True,
    get_recording_rels=False, print_warnings=True)
"""
Inputs
----------
melody_sim_thres  : (optional) the maximum similarity threshold for two melodic
                    stuctures to be considered as variant of each other. The
                    default is 0.75.
lyrics_sim_thres  : (optional) the maximum similarity threshold for two lyric
                    stuctures to be considered as variant of each other. The
                    default is 0.75.
save_structure_sim : (optional) boolean to add the melodic and lyrics similarity 
                    between each section and segment to the output or not
extract_all_labels: (optional) boolean to treat all (explicit) annotations in
                    the lyrics as a section or not (e.g. INSTRUMENTATION labels).
                    The default is False.
crop_consec_bounds: (optional) remove the first of the two consecutive boundaries
                    inside the user given segmentation boundaries
get_recording_rels: (optional) boolean to extract the relevant recording relations
                    from MusicBrainz. The default is False.
print_warnings    : (optional) boolean to print possible warnings during reading
                    the scores. Note that errors will always be printed. The
                    default is True
"""

txt_data, is_data_valid = extractor.extract(txt_filename, symbtr_name=scorename,
                                            segment_note_bound_idx=auto_seg_bounds,
                                            mbid=mbid)
"""
Inputs
----------
txt_filename            : the filepath of the SymbTr-txt score
symbtr_name             : (optional) the SymbTr-name in the
                          "makam--form--usul--name--composer" format.
mbid                    : (optional) the work or recording mbid of the
                          composition/performance related to the score
segment_note_bound_idx  : (optional) user provided segment boundaries.
                          NOTE - the indexing should start from 1, as this is
                          the convention in the SymbTr-txt scores.
                          TIP - makam-symbolic-phrase-segmentation package
                          (https://github.com/MTG/makam-symbolic-phrase-segmentation)
                          can be used to segment the SymbTr-txt scores
                          automatically.
"""
```

**Important note**: For the sake of consistency with the indexing in the
SymbTr-txt scores, the output note indices **start from 1, not 0!** Likewise,
```segment_note_bound_idx``` input should also obey to the 1 indexing
convention, otherwise the semiotic labels will be wrong.

##### Extracting metadata stored in the mu2 headers:
```python
from symbtrdataextractor.reader.mu2 import Mu2Reader
mu2_header, header_row, is_header_valid = Mu2Reader.read(
    mu2_filename, symbtr_name=scorename)

"""
Inputs
----------
mu2filename       : the filepath of the mu2 score
symbtr_name       : (optional) the SymbTr-name in the
                    "makam--form--usul--name--composer" format.
"""
```

For an interactive demo please refer to [extractsymbtrdata.ipynb](https://github.com/sertansenturk/symbtrdataextractor/blob/master/extractsymbtrdata.ipynb)

Installation
----------

If you want to install symbtrmetadataextractor, it is recommended to install symbtrmetadataextractor and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install the repository like this instead:

    pip install -e .

Now you can install the rest of the dependencies:

    pip install -r requirements

Authors
-------
Sertan Senturk
contact@sertansenturk.com

Reference
-------
Thesis
