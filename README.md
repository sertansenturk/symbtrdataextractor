symbtrmetadataextractor
===========

Introduction
------------
Python tools for extracting relevant data from SymbTr-scores

This repository contains to algorithms to extract metadata, related music knowledge and section information from [SymbTr-scores](https://github.com/MTG/SymbTr) and related information sources. 

Currently the algorithm is able to:
- Obtain the makam, usul, form, name and composer of the given SymbTr score
- Extract section boundaries from both the implicit and explicit section information given in the SymbTr scores. Analyse the melody and lyrics of each section independently and apply semiotic labeling to each section accordingly.
- Extract annotated phrase boundaries in the SymbTr-txt scores.
- Add [automatically computed phrase boundaries](https://github.com/MTG/makam-symbolic-phrase-segmentation) in the SymbTr-txt scores.
- Query relevant metadata from MusicBrainz, if the [MBID](https://musicbrainz.org/doc/MusicBrainz_Identifier) is supplied.
- Read the metadata stored in the header of the mu2 file.

Usage
=======
All the relevant data can be easily obtained:

```python
from symbtrdataextractor import extractor

data = extractor.extract(txtfilename, symbtrname=scorename, mbid='', 
                        extractAllLabels=False, get_recording_rels=False, 
                        seg_note_idx=[], melody_sim_thres=0.25, 
                        lyrics_sim_thres=0.25)
                        
mu2header = symbtrreader.readMu2Header(mu2filename)
```

The inputs for extractor.extract are:
```python
# txtfilename       : the filepath of the SymbTr-txt score
# symbtrname        : the SymbTr-name in the "makam--form--usul--name--composer" format.
# mbid              : the work ro recording mbid of the composition/performance related to the score
# extract_all_labels: whether to treat all (explicit) annotations in the lyrics as 
#					a section or not (e.g. INSTRUMENTATION labels). Default is False.
# get_recording_rels: boolean to extract the relevant recording relations from MusicBrainz
# seg_note_idx      : automatic segmentation boundaries (e.g. computed by 
#                   [makam-symbolic-phrase-segmentation](https://github.com/MTG/makam-symbolic-phrase-segmentation))
# melody_sim_thres  : The maximum similarity threshold for two melodic stuctures to 
#					be considered as variant of each other. Default is 0.25.
# lyrics_sim_thres  : The maximum similarity threshold for two lyric stuctures to be 
#					considered as variant of each other. Default is 0.25.
```

The input for symbtrreader.readMu2Header is:
```python
# mu2filename       : the filepath of the mu2 score
```

Installation
============

If you want to install symbtrmetadataextractor, it is recommended to install symbtrmetadataextractor and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install compmusic like this instead

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
