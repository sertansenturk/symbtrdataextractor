#### symbtrmetadataextractor v2.1.0
- Melodic organization is not replaced by the instrumental section names anymore
- Added melodic and lyrics similarity to output
- Default similarity threshold is lowered to 0.7 from 0.75
- Fixed typos (lyric -> lyrics) in variable names and output dictionary keys.
- Improved warnings

#### symbtrmetadataextractor v2.0.0
- Fixed a bug in section sorting  when there is a start note in the 0th index ([58f3bd4](https://github.com/sertansenturk/symbtrdataextractor/commit/58f3bd413b548c11a7144a603afa42bad654a347))
- Finalized code quality improvements
* Tested the extractor on the latest [SymbTr commit](https://github.com/MTG/SymbTr/commit/37bfb44fdf6fc3eb95acfe3ef484caefb4627f94)

#### symbtrmetadataextractor v2.0.0-alpha.6
- Froze requirements

#### symbtrmetadataextractor v2.0.0-alpha.5
- All the output note indices are given in 1-indexing to comply with SymbTr-txt scores
- ```segment_note_bound_idx``` parameter to ```SymbTrDataExtractor``` is expected to be given in **1-indexing** (not the "Pythonic" 0-indexing) to comply with the note indices in the SymbTr-txt scores
- Fixed the index shift (and hence erroneous semiotic labels) in the SegmentExtractor
- Fixed boundary cropping if there are groups of boundaries greater than 2 boundaries
- Improved unittests

#### symbtrmetadataextractor v2.0.0-alpha.4
 - Improvements in code quality
 - Redesigned output format for annotated phrase and user-provided segments

#### symbtrmetadataextractor v2.0.0-alpha.3
 - Musicbrainz metadata is now fetched using makammusicbrainz repository

#### symbtrmetadataextractor v2.0.0-alpha.2
 - Changed the Levenshtein normalization to the max length of the two strings.

#### symbtrmetadataextractor v2.0.0-alpha.1
 - Added key signature checking in the mu2_headers

#### symbtrmetadataextractor v2.0.0-alpha
 - Refactoring code according to PEP8 standarts
 - Moved all methods to newly created classes
 - Added basic unittests
 - Added documentation for the main classes (SymbTrDataExtractor and SymbTrReader)

#### symbtrmetadataextractor v1.0
 - First public release
