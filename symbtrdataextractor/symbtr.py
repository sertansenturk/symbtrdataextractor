import csv
import string

def readTxtScore(scorefile):
    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header = next(reader, None)

        index_col = header.index('Sira')
        code_col = header.index('Kod')
        comma_col = header.index('Koma53')
        numerator_col = header.index('Pay')
        denumerator_col = header.index('Payda')
        duration_col = header.index('Ms')
        lyrics_col = header.index('Soz1')
        offset_col = header.index('Offset')

        score = {'index': [], 'code': [], 'comma': [], 'numerator': [],
                'denumerator': [], 'duration': [], 'lyrics': [], 
                'offset': []}
        for row in reader:
            score['index'].append(int(row[index_col]))
            score['code'].append(int(row[code_col]))
            score['comma'].append(int(row[comma_col]))
            score['numerator'].append(int(row[numerator_col]))
            score['denumerator'].append(int(row[denumerator_col]))
            score['duration'].append(int(row[duration_col]))
            score['lyrics'].append(row[lyrics_col].decode('utf-8'))
            score['offset'].append(float(row[offset_col]))

    # shift offset such that the first note of each measure has an integer offset
    score['offset'].insert(0, 0)
    score['offset'] = score['offset'][:-1]

    return score

def getTrueLyricsIdx(lyrics, all_labels, dur):
    # separate the actual lyrics from other information in the lyrics column
    real_lyrics_idx = []
    for i, l in enumerate(lyrics):  
        # annotation/control rows, embellishments (rows w dur = 0) are ignored
        if not (l in all_labels  or l in ['.', '', ' '] or dur[i] == 0):
            real_lyrics_idx.append(i)
    return real_lyrics_idx

def synthMelody(score, max_denum):
    melody = []
    for i, note in enumerate(score['notes']):
        numSamp = score['nums'][i] * max_denum / score['denums'][i]
        melody += numSamp*[note]
    return melody

def mel2str(melody, unique_notes):
    # map each element in the melody to a unique ascii letter and concatanate to
    # a single string. This step converts the melody into the format required by
    # Levenhstein distance

    # define the ascci letters, use capital first
    ascii_letters = string.ascii_uppercase + string.ascii_lowercase
    return ''.join([ascii_letters[unique_notes.index(m)] for m in melody])
