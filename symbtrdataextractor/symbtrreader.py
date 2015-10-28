import csv
import string
import pdb

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

def readMu2Score(scorefile):
    # TODO
    pass

def readMu2Header(scorefile):
    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header_row = next(reader, None)

        header = dict()
        for row in reader:
            code = int(row[0])
            if code == 50:
                header['makam'] = {'mu2_name':row[7]}
                header['key_signature'] = row[8].split('/')
            elif code == 51:
                header['usul'] = {'mu2_name':row[7], 'mertebe':int(row[3]), 
                    'number_of_pulses':int(row[2])}
            elif code == 52:
                header['tempo'] = {'value':int(row[4]), 'unit':'bpm'}
                if not int(row[3]) == header['usul']['mertebe']:
                    print '   Mertebe and tempo unit are different!'
            elif code == 57:
                header['form'] = {'mu2_name':row[7]}
            elif code == 58:
                header['composer'] = {'mu2_name':row[7]}
            elif code == 59:
                header['lyricist'] = {'mu2_name':row[7]}
            elif code == 60:
                header['mu2_title'] = row[7]
            elif code == 63:
                header['genre'] = row[7]
            elif code in range(50, 64): 
                print '   Unparsed code: ' + ' '.join(row)
            else:  # end of header
                break

    return header
