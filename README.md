symbtrdataextractor
===========
Python tools for extracting relevant (meta)data from SymbTr-scores

Introduction
------------

This repository contains to algorithms to extract metadata, related music knowledge and section information from [SymbTr-scores](https://github.com/MTG/SymbTr) and related information sources. 

Currently you can:
- Obtain the makam, usul, form, name and composer of the given SymbTr score
- Extract section boundaries from both the implicit and explicit section information given in the SymbTr scores. Analyse the melody and lyrics of each section independently and apply semiotic labeling to each section accordingly.
- Extract phrases from the annotated phrase boundaries in the SymbTr-txt scores.
- Add and analyze phrases in the SymbTr-txt scores from [computed boundaries](https://github.com/MTG/makam-symbolic-phrase-segmentation).
- Query relevant metadata from MusicBrainz, if the [MBID](https://musicbrainz.org/doc/MusicBrainz_Identifier) is supplied.
- Read the metadata stored in the header of the mu2 file.

Usage
=======
Extracting (meta)data from the txt-score:

```python
from symbtrdataextractor.SymbTrDataExtractor import SymbTrDataExtractor

extractor = SymbTrDataExtractor(extract_all_labels=False, melody_sim_thres=0.75, 
                                lyrics_sim_thres=0.75, get_recording_rels=False,
                                print_warnings=True)
"""
Inputs
----------
extract_all_labels: (optional) boolean to treat all (explicit) annotations in the lyrics as 
                    a section or not (e.g. INSTRUMENTATION labels). The default is False.
get_recording_rels: (optional) boolean to extract the relevant recording relations from MusicBrainz.
                    The default is False.
melody_sim_thres  : (optional) the maximum similarity threshold for two melodic stuctures to 
                    be considered as variant of each other. The default is 0.75.
lyrics_sim_thres  : (optional) the maximum similarity threshold for two lyric stuctures to be 
                    considered as variant of each other. The default is 0.75.
print_warnings    : (optional) boolean to print possible warnings during reading the scores. 
                    Note that errors will always be printed. The default is True
"""

txt_data, is_data_valid = extractor.extract(txt_filename, symbtr_name=scorename, mbid=mbid, 
                                            segment_note_bound_idx=auto_seg_bounds)
"""
Inputs
----------
txt_filename            : the filepath of the SymbTr-txt score
symbtr_name             : (optional) the SymbTr-name in the "makam--form--usul--name--composer" format.
mbid                    : (optional) the work or recording mbid of the composition/performance related 
                          to the score
segment_note_bound_idx  : (optional) automatic segmentation boundaries (e.g. computed by 
                          https://github.com/MTG/makam-symbolic-phrase-segmentation)
"""
```

Extracting metadata stored in the mu2 headers: 
```python
from symbtrdataextractor.SymbTrReader import SymbTrReader
mu2_header, header_row, is_header_valid = SymbTrReader.read_mu2_header(mu2_filename, symbtr_name=scorename)

"""
Inputs
----------
mu2filename       : the filepath of the mu2 score
symbtr_name       : (optional) the SymbTr-name in the "makam--form--usul--name--composer" format.
"""
```

For an interactive demo please refer to [extractsymbtrdata.ipynb](https://github.com/sertansenturk/symbtrdataextractor/blob/master/extractsymbtrdata.ipynb)

Installation
============

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
