from symbtrdataextractor.GraphOperations import GraphOperations

def test_metric_exception():
    s1 = [0, 1, 2]
    s2 = [1, 2, 3]
    wrong_metric = 'barbara_streisand'
    try:
        GraphOperations.get_dist_matrix(s1, s2, wrong_metric)
        assert False, '"{0:s}" is not implemented and it should have failed ' \
                      'to produce a distance matrix'.format(wrong_metric)
    except ValueError:
        assert True
