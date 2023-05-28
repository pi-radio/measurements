#!/usr/bin/env python3

import skrf as rf
import glob
import re
from collections import defaultdict
from itertools import combinations

from pylab import *

r = re.compile("(?P<begin>.*)_P1_(?P<P1>[^_]+)_P2_(?P<P2>[^_]+)_(?P<end>[^\\.]*).s2p")

sweeps = defaultdict(dict)

freq = None

for fn in glob.glob("*.s2p"):
    m = r.match(fn)
    (begin, p1, p2, end) = (m["begin"], m["P1"], m["P2"], m["end"])

    n = rf.Network(fn)

    if freq is None:
        freq = n.frequency
        
    sweeps[p1][p2] = n

    n = n.copy()

    n.renumber([0, 1],[1,0])
    
    sweeps[p2][p1] = n

media = rf.DefinedGammaZ0(freq, z0=50, gamma=1j*freq.w/rf.c)

ports = [ 'INP', 'INN', 'OUTP', 'OUTN' ]

print(f"Ports: {ports}")

cmb = list(combinations([0, 1, 2, 3], 2))

print(cmb)

composite = media.match(nports=4)

for a, b in cmb:
    print(f"Stuffing {ports[a]}<->{ports[b]}")

    ntwrk = sweeps[ports[a]][ports[b]]
    
    for i, m in enumerate([a, b]):
        for j, n in enumerate([a, b]):
            composite.s[:,m,n] = ntwrk.s[:,i,j]

print(composite)

composite.write_touchstone(f"{begin}_{end}.s4p")

#composite.s31.plot_s_db()

#plt.show()

composite.se2gmm(p=2)

composite.write_touchstone(f"{begin}_{end}_mixed_mode.s4p", r_ref=100)


composite.s21.plot_s_db()

plt.show()
