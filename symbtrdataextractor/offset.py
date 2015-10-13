def findMeasureStartIdx(offsets):
    measure_start_idx = []

    tol = 0.001
    for int_offset in range(0, int(max(offsets))+1):
        idx = min(i for i, o in enumerate(offsets) if o > int_offset - tol)
        measure_start_idx.append(idx)

    nonIntegerMeasureStart = ([offsets[i] for i in measure_start_idx 
        if not isIntegerOffset(offsets[i])])
    if nonIntegerMeasureStart:
        print "    " + "Some measures are skipped by the offsets"
        print nonIntegerMeasureStart
    
    return measure_start_idx

def isIntegerOffset(offset):
    # The measure changes when the offset is an integer
    # (Note that offset was shifted by one earlier for easier processing )
    # Since integer check in floating point math can be inexact,
    # we accept +- 0.001 
    return abs(offset - round(offset)) * 1000.0 < 1.0

def getMeasureOffsetId(measureOffset, offsets, measure_start_idx):
    measure_start_offsets = [offsets[m] for m in measure_start_idx]
    # do inexact integer matching
    dist = [abs(o - measureOffset) for o in measure_start_offsets]
    return measure_start_idx[dist.index(min(dist))]
