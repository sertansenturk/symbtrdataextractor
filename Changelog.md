#### symbtrmetadataextractor 2.0.0-alpha.6
- Froze requirements

#### symbtrmetadataextractor 2.0.0-alpha.5
- All the output note indices are given in 1-indexing to comply with SymbTr-txt scores
- ```segment_note_bound_idx``` parameter to ```SymbTrDataExtractor``` is expected to be given in **1-indexing** (not the "Pythonic" 0-indexing) to comply with the note indices in the SymbTr-txt scores
- Fixed the index shift (and hence erroneous semiotic labels) in the SegmentExtractor
- Fixed boundary cropping if there are groups of boundaries greater than 2 boundaries
- Improved unittests

#### symbtrmetadataextractor 2.0.0-alpha.4
 - Improvements in code quality
 - Redesigned output format for annotated phrase and user-provided segmentations

#### symbtrmetadataextractor 2.0.0-alpha.3
 - Musicbrainz metadata is now fetched using makammusicbrainz repository

#### symbtrmetadataextractor 2.0.0-alpha.2
 - Changed the Levenshtein normalization to the max length of the two strings.

#### symbtrmetadataextractor 2.0.0-alpha.1
 - Added key signature checking in the mu2_headers

#### symbtrmetadataextractor 2.0.0-alpha
 - Refactoring code according to PEP8 standarts
 - Moved all methods to newly created classes
 - Added basic unittests
 - Added documentation for the main classes (SymbTrDataExtractor and SymbTrReader)

#### symbtrmetadataextractor v1.0
 - First public release
