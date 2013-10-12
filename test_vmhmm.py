from __future__ import print_function, division
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pp
import numpy as np
from vmhmm import VonMisesHMM, inverse_mbessel_ratio, circwrap
from sklearn.hmm import GaussianHMM
try:
    from munkres import Munkres
except ImportError:
    print('https://pypi.python.org/pypi/munkres/ for hungarian algorithim', file=sys.stderr)
    raise
    

def test_1():
    vm = VonMisesHMM(n_components=5)
    gm = GaussianHMM(n_components=5)
    X1 = np.random.randn(100,2)
    yield lambda: vm.fit([X1])
    yield lambda: gm.fit([X1])
    
def test_2():
    vm = VonMisesHMM(n_components=2)
    vm.means_ = [[0, 0], [np.pi, np.pi]]
    vm.kappas_ = [[5, 5], [4, 5]]
    vm.transmat_ = [[0.9, 0.1], [0.1, 0.9]]

    gm = GaussianHMM(n_components=2, covariance_type='diag')
    gm.means_ = [[0, 0], [1, 1]]
    gm.covars_ = [[0.1, 0.1], [0.2, 0.2]]
    gm.transmat_ = [[0.9, 0.1], [0.1, 0.9]]

    vx, vs = vm.sample(500)
    gx, gs = gm.sample(500)

    pp.clf()
    pp.scatter(gx[:,0], gx[:,1], c=gs)
    pp.savefig('test_2_gm.png')
    pp.clf()
    pp.scatter(vx[:,0], vx[:,1], c=vs)
    pp.savefig('test_2_vm.png')

def test_3():
    "The inverse function is really the inverse of the forward function"
    np.random.seed(42)
    y = np.random.random(size=100)
    x = inverse_mbessel_ratio(y)
    y2 = inverse_mbessel_ratio.bessel_ratio(x)
    np.testing.assert_array_almost_equal(y, y2, decimal=4)
    
def test_4():
    "The accelerated spline call is correct"
    np.random.seed(42)
    y = np.random.random(size=100)
    x1 = inverse_mbessel_ratio(y)
    x2 = np.exp(inverse_mbessel_ratio._spline(y))
    np.testing.assert_array_equal(x1, x2)

def test_5():
    "The C and python implementations of fitinvkappa are equivalent"
    vm = VonMisesHMM(n_components=13)
    vm.kappas_ = np.random.randn(13, 7)
    posteriors = np.random.randn(100, 13)
    obs = np.random.randn(100, 7)
    means = np.random.randn(13, 7)

    invkappa1 = vm._py_fitinvkappa(posteriors, obs, means)
    invkappa2 = vm._c_fitinvkappa(posteriors, obs, means)
    np.testing.assert_array_equal(invkappa1, invkappa2)


def test_7():
    "Sample from a VMHMM and then fit to it"
    n_components = 2
    vm = VonMisesHMM(n_components=n_components)
    means = np.array([[0, 0, 0], [np.pi, np.pi, np.pi]])
    kappas = np.array([[1, 2, 3], [2, 3, 4]])
    transmat = np.array([[0.9, 0.1], [0.1, 0.9]])
    vm.means_ = means
    vm.kappas_ = kappas
    vm.transmat_ = transmat
    x, s = vm.sample(1000)

    vm = VonMisesHMM(n_components=2)
    vm.fit([x])
    
    mappingcost = np.zeros((n_components, n_components))
    for i in range(n_components):
        for j in range(n_components):
            mappingcost[i, j] = np.sum(circwrap(vm.means_[i, :] - means[j, :])**2)
    
    mapping = Munkres().compute(mappingcost)
    means_ = np.array([vm.means_[j, :] for i, j in mapping])
    kappas_ = np.array([vm.kappas_[j, :] for i, j in mapping])
    transmat_ = vm.transmat_

    print('means\n', means, '\nmeans_\n', means_)
    print('kappas\n', kappas, '\nkappas_\n', kappas_)
    print('transmat\n', transmat, '\ntransmat_\n', transmat_)
    
    assert np.all(np.abs(kappas - kappas_) < 0.5)
    assert np.all(circwrap(means - means_) < 0.25)
    

    
    
    
    
    