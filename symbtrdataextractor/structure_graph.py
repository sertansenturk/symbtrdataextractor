import Levenshtein
import networkx as nx

def normalizedLevenshtein(str1, str2):
    avLen = (len(str1) + len(str2)) * .5

    try:
        return Levenshtein.distance(str1, str2) / avLen
    except ZeroDivisionError: # both sections are instrumental
        return 0

def getCliques(dists, simThres):
    # cliques of similar nodes
    G_similar = nx.from_numpy_matrix(dists<=simThres)
    C_similar = nx.find_cliques(G_similar)


    # cliques of exact nodes
    G_exact = nx.from_numpy_matrix(dists<=0.001) # inexact matching
    C_exact = nx.find_cliques(G_exact)

    # convert the cliques to list of sets
    C_similar = sortCliques([set(s) for s in list(C_similar)])
    C_exact = sortCliques([set(s) for s in list(C_exact)])

    return {'exact': C_exact, 'similar': C_similar}

def sortCliques(cliques):
    min_idx = [min(c) for c in cliques]  # get the minimum in each clique

    # sort minimum indices to get the actual sort indices for the clique list
    sort_key = [i[0] for i in sorted(enumerate(min_idx), key=lambda x:x[1])]

    return [cliques[k] for k in sort_key]
