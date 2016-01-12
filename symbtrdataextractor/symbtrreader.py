import csv
import string
import os
from metadata import getSlug, getMakam, getForm, getUsul, validateAttribute

def readTxtScore(scorefile):
    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header = next(reader, None)

        index_col = header.index('Sira')
        code_col = header.index('Kod')
        note53_col = header.index('Nota53')
        noteAE_col = header.index('NotaAE')
        comma53_col = header.index('Koma53')
        commaAE_col = header.index('KomaAE')
        numerator_col = header.index('Pay')
        denumerator_col = header.index('Payda')
        duration_col = header.index('Ms')
        lyrics_col = header.index('Soz1')
        offset_col = header.index('Offset')

        score = {'index': [], 'code': [], 'note53': [], 'noteAE': [],
                'comma53': [], 'commaAE': [], 'numerator': [],
                'denumerator': [], 'duration': [], 'lyrics': [], 
                'offset': []}
        for row in reader:
            score['index'].append(int(row[index_col]))
            score['code'].append(int(row[code_col]))
            score['note53'].append(row[note53_col])
            score['noteAE'].append(row[noteAE_col])
            score['comma53'].append(int(row[comma53_col]))
            score['commaAE'].append(int(row[commaAE_col]))
            score['numerator'].append(int(row[numerator_col]))
            score['denumerator'].append(int(row[denumerator_col]))
            score['duration'].append(int(row[duration_col]))
            score['lyrics'].append(row[lyrics_col].decode('utf-8'))
            score['offset'].append(float(row[offset_col]))

    # shift offset such that the first note of each measure has an integer offset
    score['offset'].insert(0, 0)
    score['offset'] = score['offset'][:-1]

    # validate
    isScoreValid = validateTxtScore(score, os.path.splitext(os.path.basename(scorefile))[0])

    return score, isScoreValid

def validateTxtScore(score, scorename):
    isRestValid = True
    isDurationValid = True
    isIndexValid = True
    dur_dict = {}
    for ii in range(0, len(score['index'])):
        if score['duration'][ii] > 0:  # note or rest
            # check rest
            if (-1 in [score['comma53'][ii], score['commaAE'][ii]] or 
                any(rs in [score['note53'][ii], score['noteAE'][ii]] for rs in ['Es', 'Sus', ''])):
                # it should be rest, validate
                if not (score['comma53'][ii] == -1 and 
                    score['commaAE'][ii] == -1 and
                    score['note53'][ii] == 'Es' and
                    score['noteAE'][ii] == 'Es' and
                    score['code'][ii] == 9):
                    isScoreValid = False
                    print scorename + ' ' + str(score['index'][ii]) + ': Invalid Rest'

            # note duration
            dursym = str(score['numerator'][ii]) + '_' + str(score['denumerator'][ii]) 
            if dursym in dur_dict.keys():
                dur_dict[dursym] = list(set([score['duration'][ii]] + dur_dict[dursym]))
            else:
                dur_dict[dursym] = [score['duration'][ii]]

    #for key, val in dur_dict.items():
    #    if not len(val)==1:
    #        print scorename + ": " + key + " note has multiple duration values; " + ', '.join([str(v) for v in val])
    #        isDurationValid = False  # USUL/TEMPO CHANGES ARE NOT HANDLED, DON'T ASSIGN FALSE YET

    # note index
    for ii in range(0, len(score['index'])-1):
        if not score['index'][ii+1] - score['index'][ii] == 1:
            print scorename + ": " + str(score['index'][ii]) + ", note index jump."
            isIndexValid = False
    isScoreValid = isRestValid and isDurationValid and isIndexValid
    return isScoreValid

def readMu2Score(scorefile):
    # TODO
    pass

def readMu2Header(scorefile, symbtrname=''):
    if not symbtrname:
        symbtrname = os.path.splitext(os.path.basename(scorefile))[0]

    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        headerRow = [unicode(cell, 'utf-8') for cell in next(reader, None)]

        header = dict()
        isTempoUnitValid = True
        for rowtemp in reader:
            row = [unicode(cell, 'utf-8') for cell in rowtemp]
            code = int(row[0])
            if code == 50:
                header['makam'] = {'mu2_name':row[7]}
                header['key_signature'] = row[8].split('/')
            elif code == 51:
                header['usul'] = {'mu2_name':row[7], 'mertebe':int(row[3]), 
                    'number_of_pulses':int(row[2])}
            elif code == 52:
                try:
                    header['tempo'] = {'value':int(row[4]), 'unit':'bpm'}
                except ValueError:  # the bpm might be a float for low tempo
                    header['tempo'] = {'value':float(row[4]), 'unit':'bpm'}
                if not int(row[3]) == header['usul']['mertebe']:
                    if not header['usul']['mu2_name'] == '(Serbest)':  # ignore serbest usul
                        print symbtrname + ': Mertebe and tempo unit are different!'
                        isTempoUnitValid = False
            elif code == 56:
                header['usul']['subdivision'] = {'mertebe':int(row[3]), 
                    'number_of_pulses':int(row[2])}
            elif code == 57:
                header['form'] = {'mu2_name':row[7]}
            elif code == 58:
                header['composer'] = {'mu2_name':row[7]}
            elif code == 59:
                header['lyricist'] = {'mu2_name':row[7]}
            elif code == 60:
                header['title'] = {'mu2_title':row[7]}
            elif code == 62:
                header['genre'] = 'folk' if row[7] == 'E' else 'classical'
            elif code == 63:
                header['notation'] = row[7]
            elif code in range(50, 64): 
                print '   Unparsed code: ' + ' '.join(row)
            else:  # end of header
                break

    # get the metadata
    slugs = getSlug(symbtrname)
    header['makam']['symbtr_slug'] = slugs['makam']
    header['form']['symbtr_slug'] = slugs['form']
    header['usul']['symbtr_slug'] = slugs['usul']
    header['title']['symbtr_slug'] = slugs['name']
    header['composer']['symbtr_slug'] = slugs['composer']

    # validate the header content
    makam = getMakam(header['makam']['symbtr_slug'])
    isMakamValid = validateAttribute(header['makam'], makam, symbtrname)

    form = getForm(header['form']['symbtr_slug'])
    isFormValid = validateAttribute(header['form'], form, symbtrname)

    usul = getUsul(header['usul']['symbtr_slug'])
    isUsulValid = validateAttribute(header['usul'], usul, symbtrname)

    isHeaderValid = isTempoUnitValid and isMakamValid and isFormValid and isUsulValid

    return header, headerRow, isHeaderValid
