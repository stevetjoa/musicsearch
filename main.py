#!/usr/bin/env python
#-*- coding:utf-8 -*-
import scipy
import lsh
import mir
import os
from collections import defaultdict
import time
import pylab

class Search (object):

    def __init__(self, L=1, k=1):
        self.fs = 44100.0
        self.pmax = 96
        self.pmin = 36
        self.cqtsz = self.pmax - self.pmin
        self.segsz = 20
        self.M = self.cqtsz*self.segsz
        self.fftsz = 2**15
        self.hop = int(0.1*self.fs)
        self.db = lsh.LSH(L, k, self.M)
        
    def feature(self, x):
        return lsh.normalize(scipy.absolute(mir.cqt(x, self.fs, lo=self.pmin, hi=self.pmax)[0]))
        
    def add(self, x, fs, label):
        x = self.preprocess(x, fs)
        X = scipy.array([self.feature(x[i:i+self.fftsz])
                         for i in range(0, x.size-self.fftsz, self.hop)])
        h = scipy.hamming(7)[:,None]
        X = scipy.signal.convolve(X, h, mode='valid')
        for i in range(len(X)-self.segsz):
            self.db.add(X[i:i+self.segsz].reshape(-1), (label, i))
        
    def query(self, x, fs):
        t0 = time.clock()
        labels = set()
        x = self.preprocess(x, fs)
        X = scipy.array([self.feature(x[i:i+self.fftsz])
                         for i in range(0, x.size-self.fftsz, self.hop)])
        h = scipy.hamming(7)[:,None]
        X = scipy.signal.convolve(X, h, mode='valid')
        for i in range(len(X)-self.segsz):
            labels = labels.union( self.db.query(X[i:i+self.segsz].reshape(-1)) )
        
        print 'Query Time: ', (time.clock() - t0)
        return self.results(labels)
        
    def results(self, labels):
        r = defaultdict(int)
        for label in labels:
            r[label[0]] += 1
        return sorted(r.iteritems(), key=lambda x:x[1], reverse=True)
            
    def preprocess(self, x, fs):
        if x.ndim==2:
            x = x[:,0].squeeze()
        if int(fs) != int(self.fs):
            x = scipy.signal.resample(x, x.size*self.fs/fs)
            print 'Resampling to 44100'
        return x
    
if __name__ == '__main__':
    
    t0 = time.clock()
    s = Search(15, 32)
    for f in os.listdir('train'):
        x, fs, enc = mir.wavread('train/'+f)
        s.add(x, fs, f)
    print time.clock() - t0
    
    
    x, fs, enc = mir.wavread('test/steve02.wav')
    results = s.query(x, fs)
    
    
