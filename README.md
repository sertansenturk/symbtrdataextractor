symbtrmetadataextractor
===========

Introduction
------------
Python tools for extracting relevant data from SymbTr-scores

This repository contains to algorithms to extract metadata, related music knowledge and section information from [SymbTr-scores](https://github.com/MTG/SymbTr) and related information sources. 

Currently the algorithm is able to:
- Obtain the makam, usul, form, name and composer of the given SymbTr score
- Extract section boundaries from both the implicit and explicit section information given in the SymbTr scores. Analyse the melody and lyrics of each section independently and apply semiotic labeling to each section accordingly.
- Query relevant metadata from MusicBrainz, if the [MBID](https://musicbrainz.org/doc/MusicBrainz_Identifier) is supplied.

Usage
=======
All the relevant data can be easily obtained:

```python
from symbtrdataextractor import extractor

data = extractor.extract("scorefile", metadata_source, extractAllLabels=False, 
    slugify=True, lyrics_sim_thres=0.25, melody_sim_thres=0.25)
```

The inputs are:
```python
# scorefile: the filepath of the SymbTr score
# metadata_source :	either the MBID of the related work or the SymbTr-name 
#					(makam--form--usul--name--composer).
# extractAllLabels: whether to treat all (explicit) annotations in the lyrics as 
#					a section or not (e.g. ISTRUMENTATION labels). Default is False.
# slugify		  : whether to replace the Turkish characters with the ASCII 
#					equivalent and replace all special characters with "-". Default 
#				    is True.
# lyrics_sim_thres: The maximum similarity threshold for two lyric stuctures to be 
#					considered as variant of each other. Default is 0.25.
# melody_sim_thres: The maximum similarity threshold for two melodic stuctures to 
#					be considered as variant of each other. Default is 0.25.
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