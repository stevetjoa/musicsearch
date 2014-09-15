#!/usr/bin/env python
#-*- coding:utf-8 -*-
import scipy
import pylab
import scipy.linalg as sl
import random
from collections import defaultdict
import h5py

def normalize(x):
    n = scipy.sqrt(scipy.inner(x,x))
    #n = sl.norm(x, scipy.inf)
    if n > 0:
        return x/n
    else:
        return x


class LSH(object):
    """
    Example:
    db = LSH(data, L, k)
    label = db.query(y)
    """    

    def __init__(self, L, k, M):
        """
        Initializes a list of L dictionaries of sets.
        SELF.DATA is a Numpy array.
        SELF.DATA[0] is one data point.
        SELF.TABLE is a list.
        SELF.TABLE[l] is a dictionary.
        SELF.TABLE[l][k] is a set of labels.
        """
        self.table = [defaultdict(set) for l in range(L)]
        self.k = k
        self.L = L
        self.M = M
        self.randomize()
        
    def randomize(self):
        self.projections = [scipy.randn(self.k, self.M) for l in range(self.L)]
        #self.projections = [scipy.random.standard_cauchy((self.k, self.M)) for l in range(self.L)]
        
    def keys(self, x):
        """
        Returns a list of keys for point x.
        """
        allkeys = []
        for P in self.projections:
            key = 0
            y = scipy.dot(P, x)
            for i in range(len(y)):
                if y[i]>0:
                    key += 1<<i
            allkeys.append(key)
        return allkeys
            
    def add(self, x, label):
        """
        Adds the label of point x to each table.
        """
        for l,key in enumerate(self.keys(x)):
            self.table[l][key].add(label)

    def query(self, x):
        """
        Returns all points that share a bin with x.
        """
        S = set()
        key = self.keys(x)
        for l in range(self.L):
            S = S.union(self.table[l][key[l]])
        return S
        
    def match(self, x, y):
        xkeys = self.keys(x)
        ykeys = self.keys(y)
        for xk,yk in zip(xkeys,ykeys):
            if xk == yk:
                return True
        return False
        
    def binsize(self, l, key):
        """
        Returns the number of elements in bin KEY in table L.
        """
        return len(self.table[l][key])
        
    def tablesize(self, l):
        """
        Returns the number of bins in table L.
        """
        return len(self.table[l])
        
    def overview(self):
        for l in range(self.L):
            print 'Table %d has %d bins:' % (l, self.tablesize(l)),
            print [len(self.table[l][b]) for b in self.table[l]]
            
#if __name__ == '__main__':
#    fig = pylab.figure()
#    ax = Axes3D(fig)

#    colors = ['r', 'b', 'k', 'y']
#    markers = ['o', 's', 'x', '^']
#    for key in range(2**k):
#        i = list(db.table[0][key])
#        ax.scatter3D(A[i,0], A[i,1], A[i,2], s=60, c=colors[key], marker=markers[key])
#    fig.show()
#    
