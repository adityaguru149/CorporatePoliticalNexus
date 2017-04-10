import entitymatching as em
import pandas as pd
import pprint as pp
from collections import Counter


def findFrequentWords(strs, cutoff=2, elements=50, indexedWord=-1, start=""):
    c = Counter()
    # may give IndexError
    if indexedWord != -1:
        strs = [s.split()[indexedWord] for s in strs]
    for i in strs:
        c.update(i.split())
    d = dict(c)
    for k in d.keys():
        if c[k] < cutoff or not k.startswith(start):
            del c[k]
    return c.most_common(elements)


# our_db = pd.read_csv('export(1).csv')
# our_cnames = [em.processString(str) for str in our_db['n.name']]

all_comp = pd.read_csv('all_companies_background.csv')
new_cnames = [em.processString(str) for str in all_comp['Company Name']]
# c = findFrequentWords(new_cnames, elements=100, cutoff=10)
# print(c)

n_strs = [em.removeHashNSpace(n, hashOnly=True) for n in new_cnames]
f = findFrequentWords(n_strs, elements=10000, cutoff=1, indexedWord=-1, start="FERT")
pp.pprint(f)

for n, n2 in zip(n_strs, all_comp['Company Name']):
	if "FERT" in n:
		print(n, n2)
