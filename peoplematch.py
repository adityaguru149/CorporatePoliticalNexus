import entitymatching as em
from fuzzywuzzy import fuzz as fwf
import pandas as pd
import csv
import re

def processName(s):
    s = re.sub('[\.\;\,\:]', ' ', s)
    s = s.replace('DUTTA', 'DATTA')
    s = s.replace('OU', 'AU')
    s = s.replace('OW', 'AU')
    s = s.replace('DHR', 'DHAR')
    s = s.replace('DHURY', 'DHARI')
    s = s.replace('DHURI', 'DHARI')
    # this combined with dh rule gives madari for madhuri
    s = s.replace('^DR ', '')
    s = s.replace('^MR ', '')
    s = s.replace('^MS ', '')
    s = s.replace('^MRS ', '')
    s = s.replace('^SMT ', '')
    s = s.replace('MED', 'MAD')
    s = s.replace(' BHAI', 'BHAI')
    s = s.replace('E', 'EE')
    s = s.replace('EE', 'I')
    s = s.replace('OO', 'U')
    # o and oo match issue
    s = s.replace('RAY', 'ROY')
    s  = re.sub(r'(.)\1+', r'\1', s)
    s = s.replace('WALA', 'WAL')
    #s = s.replace('AGRA', 'AGAR')
    s = s.replace('TH', 'T')
    s = s.replace('DH', 'D')
    s = s.replace('SH', 'S')
    s = s.replace('KH', 'K')
    # s = s.replace('CH', 'K')
    s = s.replace('CK', 'K')
    s = s.replace('BH', 'B')
    s = s.replace('GH', 'G')
    # first H then any of the above consonants also
    s = s.replace('PH', 'F')
    s = s.replace('X', 'KS')
    #s = s.replace('EI', 'I')
    #s = s.replace('IE', 'I')
    s = s.replace('IY', 'I')
    s = s.replace('Y', 'I')
    s = s.replace('W', 'V')
    s = s.replace('V', 'B')
    s = s.strip()
    return s


e = 0
ne = 0
c = pd.read_csv('allleven.csv')
newname = c['upper']
mcaname = c['cname']
mcadin = c['din']
mcacin = c['cin']
print(c.shape[0])
fnm = ['din', 'mcapname', 'upper', 'cin']
with open('mat.csv', 'w') as f:
    wf = csv.DictWriter(f, delimiter=',', fieldnames=fnm)
    wf.writeheader()
    for i in range(c.shape[0]):
        if i % 100000 == 0:
            print(i)
        n = processName(newname[i])
        m = processName(mcaname[i])
        # n_a_mid = re.sub(r'\BA+\B', r'', n)
        # m_a_mid = re.sub(r'\BA+\B', r'', m)
        n_sl = n.replace(' ', '')
        m_sl = m.replace(' ', '')
        if n == m:
            e += 1
            wf.writerow({'din':mcadin[i], 'mcapname':mcaname[i], 'upper':newname[i], 'cin':mcacin[i]})
        elif em.compare(n, m) or em.leven(n_sl, m_sl) < 2 or fwf.partial_ratio(n_sl,m_sl) == 100:
            ne +=1
            wf.writerow({'din':mcadin[i], 'mcapname':mcaname[i], 'upper':newname[i], 'cin':mcacin[i]})
print(i, e, ne, e+ne)
