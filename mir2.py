#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
mir.py: A simple, single-file package of music information retrieval
utilities for Python that emphasizes simplicity, modularity, and
visualizations.

Authors: Brennan Keegan, Steve Tjoa
Institution: Signals and Information Group, University of Maryland
Created: February 2, 2011
Last Modified: February 13, 2011

Basic functions:
wavread, micread, play
spectrogram, chromagram, instrogram
"""

import numpy
import scipy
import pylab
import matplotlib
import scipy.signal as ss
import scipy.linalg as sl
import scikits.audiolab as audiolab
#import mfcc
#import alsaaudio
import time
import os

### Audio I/O utilities ###

def wavread(filename):
    """
    wav, fs, nbits = wavread(filename)

    Read file FILENAME. WAV is a numpy array, FS is the sampling rate,
    and NBITS is the bit depth.
    """
    return audiolab.wavread(filename)

def micread(sec, fs=44100):
    """
    wav = micread(sec, fs=44100)

    Reads SEC seconds from the microphone at sampling rate FS.
    """
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)
    inp.setchannels(1)
    inp.setrate(fs)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(160)

    f = open('out.raw', 'wb')
    t0 = time.time()
    while time.time()-t0 < sec:
        l, data = inp.read()
        if l:
            f.write(data)

    x = scipy.fromfile('out.raw', dtype=scipy.int16)
    f.close()
    os.remove('out.raw')
    return x*2.0**-15

def play(wav, fs=44100):
    """
    play(wav, fs=44100)

    Play WAV at sampling rate FS.
    """
    audiolab.play(wav.T, fs)




### Gram class and subclasses ###

class Gram(object):

    def __init__(self, x, fs, framesz, hop, ch, func, tmin, tmax):
        self.fs = fs
        self.framesz = framesz
        self.hop = hop

        if x.ndim > 1:
            numch = x.shape[1]
            x = x[:,ch].squeeze()
        framesamp = int(fs*framesz)
        hopsamp = int(fs*hop)

        if tmin is None:
            self.tmin = 0
        else:
            self.tmin = tmin
        if tmax is None:
            self.tmax = float(x.shape[0])/fs
        else:
            self.tmax = tmax

        tminsamp = int(fs*self.tmin)
        tmaxsamp = int(fs*self.tmax)
        numsamp = tmaxsamp-tminsamp
        self.numframes = (numsamp-framesamp)/hopsamp + 1


        if func == scipy.fft:
            ymax = framesamp
        elif func == pc:
            ymax = int(hz2midi(fs/2))
        elif func == chroma:
            ymax = 12
        elif func == mfcc_fake:
            ymax = 32

        self.X = scipy.zeros([ymax, self.numframes])
        
        n = 0
        for i in range(tminsamp, tmaxsamp-framesamp, hopsamp):
            self.X[:,n] = func(x[i:i+framesamp])
            n = n + 1


    def plot(self, color=True, extent=None, ymax=None):
        #pylab.rcParams['text.usetex'] = True
        #pylab.rcParams['font.family'] = 'serif'

        if color:
            cm = None
        else:
            cm = pylab.cm.gray_r

        if ymax is None:
            img = pylab.imshow(self.X, aspect='auto', interpolation = 'nearest', origin='lower', extent=extent, cmap=cm)#, norm=LogNorm(vmin = 25, vmax = 50))        
        else:
            x = self.X.shape
            smax = int(float(ymax*x[0])/self.fs)
            Xtrunc = self.X[0:smax,]
            img = pylab.imshow(Xtrunc, aspect='auto', interpolation = 'nearest', origin='lower', extent=extent, cmap=cm)

        matplotlib.pyplot.show()
        pylab.xlabel('Time (seconds)')
        return img

def spectrogram(wav, fs, framesz, hop, ch=0, absolute=True, half=True, tmin=None, tmax=None):
    print tmin, tmax
    return Spectrogram(wav, fs, framesz, hop, ch, absolute, half, tmin, tmax)

class Spectrogram(Gram):

    def __init__ (self, x, fs, framesz, hop, ch, absolute, half, tmin, tmax):
        Gram.__init__(self, x, fs, framesz, hop, ch, scipy.fft, tmin, tmax)
        if absolute:
            self.X = scipy.absolute(self.X)
        if half:
            self.X = self.X[:self.X.shape[0]/2,:]

        #if self.fmax is None:
        #    self.fmax = self.fs

    def plot(self, title='Spectrogram', color=True, show=True, filename=None, fmax=None):
        if fmax == None:
            fmax = self.fs
        img = Gram.plot(self, color, extent=[self.tmin, self.tmax, 0, fmax], ymax = fmax)
        pylab.title(title)
        pylab.ylabel('Frequency (Hertz)')
        return img

def qspectrogram(wav, fs, framesz, hop, ch=0, absolute=True, half=False, tmin=None, tmax=None):
    return Qspectrogram(wav, fs, framesz, hop, ch, absolute, half, tmin, tmax)


class Qspectrogram(Gram):
    """

    """
    def __init__(self, x, fs, framesz, hop, ch, absolute, half, tmin, tmax):
        Gram.__init__(self, x, fs, framesz, hop, ch, pc, tmin, tmax)

        if absolute:
            self.X = scipy.absolute(self.X)
        if half:
            self.X = self.X[:self.X.shape[0]/2,]
    
    def plot(self, title='Constant Q Spectrogram', color=True, show=True, filename=None, fmax=None):
        img = Gram.plot(self, color, extent=[self.tmin, self.tmax, 0, int(hz2midi(self.fs/2))], ymax = fmax)
        pylab.title(title)
        pylab.ylabel('MIDI Note #')
        return img

def pc(wav, fs=44100):
    """
    p = pc(wav, fs)

    Returns pitch class vector of WAV with sampling rate FS.
    Like chroma, but unwrapped.
    """
    hi = int(hz2midi(fs/2))
    X = scipy.absolute(scipy.fft(wav))
    c = numpy.zeros(hi)
        
    if wav.ndim==2:
        X = X[:,0].squeeze()
        
    trange = X.shape
    N = trange[0]
        
    for p in range(hi):
        
        midi0 = p-0.5
        midi1 = p+0.5
        hz0 = float(midi2hz(midi0))
        hz1 = float(midi2hz(midi1))
        b0 = int(round(N*hz0/fs))
        b1 = int(round(N*hz1/fs))
        
                
        if b0 < (b1-1):
            c[p] = X[b0:b1].sum()
        else:
            c[p] = X[b0]

    return c



def chromagram(wav, fs, framesz, hop, ch=0, absolute=True, half=False, tmin=None, tmax=None):
    return Chromagram(wav, fs, framesz, hop, ch, absolute, half, tmin, tmax)

class Chromagram(Gram):
    def __init__ (self,wav,fs,framesz,hop,ch,absolute,half,tmin,tmax):
        if wav.ndim==2:
            wav = wav[:,0].squeeze()
        wavlen = wav.size

        if tmin is None:
            tmin = 0
        
        if (tmax != None) and wavlen > tmax*fs:
            wavlen = tmax*fs - tmin*fs

        tmin_samp = int(tmin*fs)
        tmax_samp = int(tmax*fs)
        framesz_samp = int(framesz*fs)
        hop_samp = int(hop*fs)
        numframes = int((wavlen-framesz_samp)/hop_samp + 1)
        X = scipy.zeros([12, numframes])
        n = tmin_samp
        for k in range(numframes):
            X[:,k] = chroma(wav[n:n+framesz_samp]*ss.hamming(framesz_samp), fs)
            n += hop_samp
        self.X = X    

    def plot(self, title='Chromagram', color=True, show=True, filename=None):
        pylab.clf()
        pylab.imshow(self.C, origin='lower', interpolation='nearest', aspect='auto')
        pylab.yticks(range(12), labels())
        
        pylab.colorbar(format='%.2f')
        pylab.title(title)
        pylab.ylabel('Pitch')
        if show:
            pylab.show()
        if filename:
            pylab.savefig(filename)
        
def chroma(wav, fs):
    """
    Return chroma vector of a WAV vector with sampling rate FS.
    Assumes single-column vector input.
    """
    c = pc(wav, fs)
    ch = scipy.zeros(12)
    for i in range(12):
        ch[i] = c[i::12].sum()
    return ch






def timbregram(x, fs, framesz,hop, ch=0, tmin=0,tmax=None):
    return Timbregram(x, fs, framesz, hop, ch, tmin, tmax)

class Timbregram(Gram):

    def __init__(self, x, fs, framesz, hop, ch, tmin, tmax):
        Gram.__init__(self, x, fs, framesz, hop, ch, mfcc_fake, tmin, tmax)
        self.Coeff_Num = 32

    def plot(self, title='Timbregram', color=True, show=True, filename=None, ymax=None):
        img = Gram.plot(self, color, extent=[self.tmin, self.tmax, 0, self.Coeff_Num], ymax = ymax)
        pylab.title(title)
        pylab.ylabel('MFCC Coefficients')
        return img
        
    
def mfcc_fake(x, fs=44100):
    c = scipy.randn(32)
    return c

class Scape(object):
 
    def __init__(self, x, fs, fsz_min, fsz_max, ch, func, tmin, tmax):
        
        self.fs = fs
        self.fsz_min = fsz_min
        self.fsz_max = fsz_max

        # If no max frame size is given, sets fsz_max to length of .wav file
        
        if fsz_max is None:
            self.fsz_max = float(len(x))/self.fs

        # If .wav file is more than 1 channel, just looks at channel ch of signal
        
        if x.ndim > 1:
            numch = x.shape[1]
            x = x[:,ch]

        # Finds the number of samples for the minimum frame using fsz_min
        # Next sets fsamp_min equal to the next smaller integer divisor of len(x)
        # i.e. if x has 100 samples and fsamp_min is 3 (won't divide 100 equally)
        # fsamp_min becomes 2, the next smallest integer to evenly divide len(x)
        
        fsamp_min = int(fs*self.fsz_min)
        fsamp_min = len(x)/(len(x)/fsamp_min)
        fsamp_max = len(x)
        
        self.fsamp_min = fsamp_min
        self.fsamp_max = fsamp_max

        # Sets tmin/tmax for cases in which the input is None

        if tmin is None:
            self.tmin = 0
        else:
            self.tmin = tmin
        
        if tmax is None:
            self.tmax = float(len(x))/self.fs
        else:
            self.tmax = tmax

        # Uses tmin/tmax to find their sample domain counterparts, tminsamp/tmaxsamp
        # Difference of tminsamp and tmaxsamp used to acquire
        # total number of samples in subset of signal
        
        tminsamp = int(fs*self.tmin)
        tmaxsamp = int(fs*self.tmax)
        numsamp = tmaxsamp - tminsamp
        self.maxnumframes = numsamp/fsamp_min

        # Finds all sample sizes that both 
        step =[]
        for i in range(1,len(x)):
            if (self.maxnumframes % i*fsamp_min) < 2*fsamp_min:
                step.append(i*fsamp_min)

        # Removes second to last entry of step
        step[-2:-1] = []

        
        inc = len(step)
        self.inc = inc
        self.step = step
        self.steplabels = [numpy.round(float(i)/fs,3) for i in self.step]
        self.X = numpy.zeros([inc,self.maxnumframes])
        
        n = 0
        for fsamp in step:
            m = 0
            for i in range(tminsamp, tmaxsamp - fsamp, fsamp):
                self.X[n,m:(m+fsamp/fsamp_min)] = func(x[i:i+fsamp])
                m += fsamp/fsamp_min
            print n
            n += 1


    def plot(self, color=True, extent=None, ymax=None):
        
        if color:
            cm = None
        else:
            cm = pylab.cm.gray_r
        
        img = pylab.imshow(self.X, aspect='auto', interpolation = 'nearest', vmin = 0, vmax = 11, origin='lower', extent=extent, cmap=cm)        

        pylab.show()
        pylab.xlabel('Time (seconds)')
        return img


def keyscape(x, fs, fsz_min=None, fsz_max=None, ch=None, tmin=None, tmax=None):
    return Keyscape(x, fs, fsz_min, fsz_max, ch, tmin, tmax)


class Keyscape(Scape):

    def __init__ (self, x, fs, fsz_min, fsz_max, ch, tmin, tmax):
        Scape.__init__(self, x, fs, fsz_min, fsz_max, ch, Key, tmin, tmax)

    def plot(self, title='Keyscape', color=True, show=True, filename=None, ymax=None):
        if ymax == None:
            ymax = self.inc
        img = Scape.plot(self, color, extent=[self.tmin, self.tmax, 0, ymax], ymax = ymax)
        pylab.yticks(numpy.arange(self.inc), self.steplabels )

        pylab.colorbar(img)
        
        pylab.title(title)
        pylab.ylabel('Frame Size (seconds)')
        return img


def Key(wav, fs = 44100):

    # Perform Chroma operation using the below parameters
    # to acquire the 0 to 11 pitch values in wav

    framesz = 0.040
    hop = 0.020
    fs = 44100

    wavlen = wav.size
    framesz_samp = int(framesz*fs)
    hop_samp = int(hop*fs)

    numframes = (wavlen - framesz_samp)/hop_samp + 1

    C = scipy.zeros([12, numframes])
    n = 0
    for k in range(numframes):
        C[:,k] = chroma(wav[n:n + framesz_samp]*ss.hamming(framesz_samp), fs)
        n += hop_samp

    # Adds energy in each pitch together
    
    C_trans = numpy.transpose(C)
    pitch_total = sum(C_trans)

    # Creates scale list which gives pitch spacing in Major scale (W W H W W W H)
    # Uses a mod 12 version of this spacing list to sum the energy found
    # at the corresponding pitch locations in the Major scale.
    
    # This process is performed for each key, yielding a length 12 array key_energy
    # with the total 'energy' found for each key in the signal
    
    p = 0
    total = 0
    key_energy = numpy.zeros(12)
    w = 1

    for p in range(12):
        scale = [p,p+2,p+4,p+5,p+7,p+9,p+11]
        modscale = [i%12 for i in scale]
        for q in modscale:
            if q == modscale[0]:
                w = 3
            if q == modscale[4]:
                w = 1
            total += w*pitch_total[q]
            w = 1
        key_energy[p] = total
        total = 0


    # Iterates over the 12 entries in key_energy
    # Returns the position where the highest 'energy' was found
    # i.e. C = 0, C# = 1, D = 2, ..., B = 11
    
    Emax = 0
    for i in range(12):
        if Emax < key_energy[i]:
            Emax = key_energy[i]
            keynum = i
            
    return keynum







### Feature extraction. ###



### Miscellaneous utilities. ###

def hz2midi(hz):
    """
    midi = hz2midi(hz)

    Converts frequency in Hertz to midi notation.
    """
    return 12*scipy.log2(hz/440.0) + 69

def midi2hz(midi):
    """
    hz = midi2hz(midi)

    Converts frequency in midi notation to Hertz.
    """
    return 440*2**((midi-69)/12.0)

def puretone(f0, T, fs=44100):
    """
    x, t = mir.puretone(f0, T, fs)

    Creates a pure tone at F0 Hertz, FS samples per second, for T seconds.
    Returns a numpy array X and its time index vector.
    >>>
    """
    t = scipy.arange(0,T,1.0/fs)
    return scipy.sin(2*scipy.pi*f0*t + scipy.rand()*scipy.pi*2), t

def labels(flat=False):
    if flat:
        return ['C',u'D\u266d','D',u'E\u266d','E','F',u'G\u266d','G',u'A\u266d','A',u'B\u266d','B']
    else:
        return ['C', 'C#','D','D#','E','F','F#','G','G#','A','A#','B']
        #return ['C',u'C\u266f','D',u'D\u266f','E','F',u'F\u266f','G',u'G\u266f','A',u'A\u266f','B']

def synpitch(midi, T, fs=44100):
    """
    Return a signal with pitch MIDI (in midi notation), duration T seconds,
    and sampling rate FS.
    """
    f0 = midi2hz(midi)
    f = f0
    P = 1
    x = puretone(f, fs, T)
    while f < fs/2:
        P *= 0.5
        f += f0
        x += P*puretone(f, fs, T)
    return x

def synpitchseq(notes, fs=44100):
    """
    NOTES is a list of tuples (MIDI, T). MIDI is the pitch (in midi notation)
    and T is the duration in seconds.
    """
    return scipy.concatenate([synpitch(midi, T, fs) for (midi, T) in notes])



def pc2key(c, pitches):
    """
    Given a pitch class vector, C, return the KEY associated.
    """
    key = 0
    for i, p in enumerate(pitches):
        if c[p-1] < c[p]:
            key += 1<<i
    return key

def pianoroll(pitches, phigh, show=True, figname=None):
    N = len(pitches)
    X = scipy.zeros([phigh, N])
    for i, frame in enumerate(pitches):
        for pitch in frame:
            X[pitch, i] = 1
    fig = pylab.figure(figsize=(16,4))
    ax = fig.add_axes([0.03,0.06,0.96,0.90])
    ax.imshow(X, origin='lower', aspect='auto', interpolation='nearest', cmap=pylab.cm.gray_r)
    ticks = range(12, phigh, 12)
    ax.set_yticks(ticks)
    ax.set_yticklabels(ticks)
    ax.set_xticks([])
    ax.set_ylim([48, 84])
    if show:
        fig.show()
    if figname:
        fig.savefig(figname)





x = 1000
