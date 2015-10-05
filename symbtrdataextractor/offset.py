def findMeasureStartIdx(offsets):
    measure_start_idx = []

    tol = 0.001
    for int_offsets in range(0, int(max(offsets))+1):
        measure_start_idx.append(min(i for i, o in enumerate(offsets) 
            if o > int_offsets - tol))

    if not all(isIntegerOffset(offsets[i]) for i in measure_start_idx):
        print "    " + "Some measures are skipped by the offsets"
    
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
    dist = [abs(o - offset) for o in measure_start_offsets]
    return measure_start_idx[dist.index(min(dist))]
