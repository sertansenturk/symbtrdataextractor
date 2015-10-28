import csv
import string

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
