#!/usr/bin/env python3
import pandas as pd
import jellyfish as jf
import entitymatching as em
import logging as lg
lg.basicConfig(filename='matches.log', level=lg.DEBUG)

# o_cols = ['n.name', 'n.cin']
# our_db = pd.read_csv('export.csv', usecols=o_cols)
# our_cnames = [em.processString(str) for str in our_db[o_cols[0]]]
# our_ids = our_db[o_cols[1]]
# our = dict(zip(our_ids, our_cnames))

m_cols = ['Company Name', 'CIN']
m_db = pd.read_csv('MCA_companies_CIN.csv', usecols=m_cols)
m_cnames = [em.processString(str) for str in m_db[m_cols[0]]]
m_ids = m_db[m_cols[1]]
our = dict(zip(m_ids, m_cnames))

n_cols = ['Company Name', 'CompanyId', 'Incorporation Year']
new_c = pd.read_csv(
    'all_companies_background.csv', usecols=n_cols, dtype={n_cols[2]: str})
new_cnames = [em.processString(str) for str in new_c[n_cols[0]]]
new_ids = new_c[n_cols[1]]
new_yrs = new_c[n_cols[2]]
# print(new_yrs[:10], pd.isnull(new_yrs[10]))

f = []
nf = []
conf = []
cnt = 0
for i, ncnm, yr in list(zip(new_ids, new_cnames, new_yrs))[:500]:
    choices, p_j, index_j = em.getMatches(
        ncnm, our, jf.jaro_winkler, 0.7, 250, 3, ifzip=False)
    cnt += 1
    lg.info("{} {} {}".format(str(cnt), str(i), str(len(choices))))
    dict_chs = dict(zip(index_j, choices))
    if len(choices) == 1 and p_j == 1:
    	best = choices, p_j, index_j
    else:
        best = em.getMatches(ncnm, dict_chs, em.fstwtdsetL, 0.85, 5, 2)
    val = [i, ncnm, yr]
    if len(best) > 0:
        ans, prob, k = best[0]
        # zip compare needed
        yr_mat = pd.isnull(yr) or (yr == k[8:12])
        not_cnfsd = len(best) == 1 or prob != best[1][1]
        p1 = em.wordLevensteinFraction(ans, ncnm, 0, False)
        # print(ncnm, prob, p1, yr_mat)
        if p1 == 1 and prob >= 0.9 and yr_mat and not_cnfsd:
            val.extend((ans, k, prob))
            f.append(val)
        else:
            # if prob is high then 1st word might have been spelling error
            for x in best:
                val.extend(x)
            conf.append(val)
    else:
        for x in list(zip(choices[:5], p_j[:5], index_j[:5])):
            val.extend(x)
        nf.append(val)

df = pd.DataFrame(f)
df.to_csv("f.csv", header=False, index=False)
df = pd.DataFrame(conf)
df.to_csv("conf.csv", header=False, index=False)
df = pd.DataFrame(nf)
df.to_csv("nf.csv", header=False, index=False)
