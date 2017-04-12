#!/usr/bin/env python3
import jellyfish as jf
from fuzzywuzzy import fuzz as fwf
import re
from bisect import bisect_left

leven = jf.levenshtein_distance

# takes uppercase string returns it with abbreviations expanded
def expandAbbreviations(str):
    words = str.split()
    for i in range(len(words)):
        w = words[i]
        if w in ["PVT", "(P)"]:
            w = "PRIVATE"
        elif w in ["LTD", "LT"]:
            w = "LIMITED"
        elif w in ["GOV", "GOVT"]:
            w = "GOVERNMENT"
        elif w in ["COOP"]:
            w = "COOPERATIVE"
        elif w in ["CO"]:
            w = "CORPORATION"
        # elif w in ["LLC"]:
        #     w = "LIMITED LIABILITY COMPANY"
        elif w == "&":
            w = "AND"
        words[i] = w
    return " ".join(words)


# takes uppercase string returns it with words hashed
def hashAbbreviations(str):
    str = str.replace('WOUND UP', 'WOUNDUP')
    str = re.sub(r'PV$', r'PRIVATE', str)
    words = str.split()
    for i in range(len(words)):
        w = words[i]
        if w in ["PVT", "PRIVATE", "(P)", "PRIVAT", "PTE", "PV"]:
            w = "#PRIVATE"
        elif w in ["LTD", "LT", "LIMITED", "(L)", "LIM", "LIMI", "LIMITE"]:
            w = "#LIMITED"
        elif w in ["GOV", "GOVT", "GOVERNMENT", "(G)"]:
            w = "#GOVERNMENT"
        elif w in ["COOP", "COOPERATIVE"]:
            w = "#COOPERATIVE"
        elif w in ["CO", "CORPORATION", "(C)", "CORPN"]:
            w = "#CORPORATION"
        elif w in ["MANAGEMENT", "MGMT"]:
            w = "#MANAGEMENT"
        elif w in ["ORG", "ORGANISATION", "ORGANIZATION"]:
            w = "#ORGANIZATION"
        elif w in ["(INDUSTRIES)", "(INDUSTREIS)", "INDUSTRIES", "INDUSTREIS", "INDUSTRY", "INDS"]:
            w = "#INDUSTRIES"
        elif w in ["INTNL", "INTERNATIONAL", "INTERNATIO"]:
            w = "#INTERNATIONAL"
        elif w in ["INFRA", "INFRASTRUCTURE"]:
            w = "#INFRASTRUTURE"
        elif w in ["(INDIA)", "INDIA", "INDIA", "(I)"]:
            w = "#INDIA"
        # need logic for llc
        # elif w in ["LIMITED LIABILITY COMPANY"]:
        #     w = "LLC"
        elif w in ["(MERGED)", "MERGED"]:
            w = "#MERGED"
        elif w in ["(WOUNDUP)", "(WOUND-UP)", "(WOUND)", "[WOUNDUP]", "WOUNDUP", "WOUND-UP", "(WOUNDUP)"]:
            w = "#WOUNDUP"
        elif w in ["INVESTMENT", "INVESTMENTS", "INV", "INVMTS", "INVESMENTS", "INVESTMEN", "INVESTMES"]:
            w = "#INVESTMENT"
        elif w in ["FERTILIZER", "FERTILISER", "FERTILIZERS", "FERTILISERS", "FERTILIZE", "FERTILIZ", "FERTILISE", "FERTILIZE", "FERTLISE", "FERTLIZE"]:
            w = "#FERTILIZER"
        elif w == "&":
            w = "#AND"
        elif w == "THE":
            w = "#THE"
        words[i] = w
    return " ".join(words)


def processString(str):
    str = str.replace('.', ' ')
    str = re.sub(r"[ ]?\([ ]?", " (", str)
    str = re.sub(r"[ ]?\)[ ]?", ") ", str)
    str = str.replace("&", " & ")
    str = str.replace(".", ". ")
    str = re.sub("\s\s+", " ", str)
    str = str.strip()
    str = re.sub(r'\(.*?\)', lambda x: ''.join(x.group(0).split()), str)
    str  = re.sub(r'(.)\1+', r'\1', str)
    str = str.upper()
    str = hashAbbreviations(str)
    str = str.replace('-', '')
    str = str.replace('(', '')
    str = str.replace(')', '')
    return str


def hashed(s):
    return s.startswith('#')


# prototype definition
def removeHashNSpace(str, hashOnly=False):
    str = re.sub(re.compile(r"\#\w+"), "", str)
    str = re.sub("\s\s+", " ", str)
    str = str.strip()
    if not hashOnly:
        str = str.replace(" ", "")
    return str


def wordLevensteinFraction(str1, str2, index, countHashed=True):
    # need error handling when word not found
    if countHashed:
        w1 = str1.split(" ", index + 1)[index]
        w2 = str2.split(" ", index + 1)[index]
    else:
        w1 = [s for s in str1.split(" ") if not hashed(s)][index]
        w2 = [s for s in str2.split(" ") if not hashed(s)][index]
    return (1 - jf.levenshtein_distance(w1, w2) / max(len(w1), len(w2)))


def stringLevensteinFraction(s1, s2, recogHash=False):
    if recogHash:
        s1 = removeHashNSpace(s1)
        s2 = removeHashNSpace(s2)
    s1 = s1.replace(" ", "")
    s2 = s2.replace(" ", "")
    return (1 - jf.levenshtein_distance(s1, s2) / max(len(s1), len(s2)))


# w = ["a", "b", "c"]
# l = len(w)
# n = fact(l+1)
# [math.log(x, n) for x in range(2, l+2)]
# def fact(n):
#     return 1 if n<2 else n*fact(n-1)
def wordwiseJaroWinkler(str1, str2):
    w1 = str1.split()
    w2 = str2.split()
    if len(w1) >= len(w2):
        max_w = w1
        min_w = w2
    else:
        max_w = w2
        min_w = w1
    minlen = len(min_w)
    maxlen = len(max_w)
    result = 0
    last_m = 0
    for i, u in enumerate(max_w):
        max_mat = 0
        for j, v in enumerate(min_w[last_m:]):
            mat = jf.jaro_winkler(u, v)
            if max_mat < mat:
                max_mat = mat
                val = min(i, j)
            if mat == 1.0:
                last_m = j
                break
        result += (maxlen - val) * mat / maxlen
    return result / minlen + ((minlen - 1) * minlen) / (2 * minlen * maxlen)


def wordSetLevenstein(s1, s2, quick=False, part=True, recogHash=True):
    t1 = set(s1.split())
    t2 = set(s2.split())
    l_tmx = max(len(t1), len(t2))
    intn = t1.intersection(t2)
    ifrac = len(intn) / l_tmx
    # short circuit
    if quick and ifrac < 0.2:
        return ifrac
    d1 = sorted(t1.difference(intn))
    d2 = sorted(t2.difference(intn))
    if len(d1) < len(d2):
        dmax = d2
        dmin = d1
    else:
        dmax = d1
        dmin = d2
    if dmax == 0:
        return ifrac
    m = [max([stringLevensteinFraction(x, y) for x in dmax]) for y in dmin]
    h = len([s for s in dmax if hashed(s)]) if recogHash else 0
    n = 1 if recogHash else 0
    ln = (len(dmax) - h)
    if ln == 0:
        ln = 1
    if len(m) > 0:
        d_pts = sum(m) / ln
    elif part:
        def strLenSum(strLst):
            return sum(len(s) for s in strLst)
        l_str_tmx = max(map(strLenSum, (t1, t2)))
        d_pts = (strLenSum(intn) + n) / (l_str_tmx + h)
    else:
        d_pts = 0
    # print(s1, l_tmx, len(intn), len(dmax), len(dmin), sum(m), d_pts, h)
    return ifrac + d_pts * len(dmax) / l_tmx
# probably also need a word sequence leven


def fstwtdsetL(s1, s2):
    wsl = wordSetLevenstein(s1, s2)
    wlf1 = wordLevensteinFraction(s1, s2, 0)
    slf = stringLevensteinFraction(s1, s2, True)
    return wlf1 * 0.15 + wsl * 0.6 + 0.25 * slf


# limit -1 is for not limiting the output
def getMatches(str, chs=[], fn=wordSetLevenstein, cutoff=0.75, limit=1, max_exact=1, ifzip=True):
    result = list()
    scores = list()
    indices = list()
    got_exact = 0
    i_cs = chs.items() if isinstance(chs, dict) else enumerate(chs)
    for i, ch in i_cs:
        score = fn(str, ch)
        if score < cutoff:
            continue
        # assuming ascending order sorted
        x = bisect_left(scores, score)
        scores.insert(x, score)
        result.insert(x, ch)
        indices.insert(x, i)
        # print(scores)
        if limit != -1:
            scores = scores[-limit:]
            result = result[-limit:]
        if score == 1:
            got_exact += 1
            if got_exact == max_exact:
                break
    if ifzip:
        return list(zip(result, scores, indices))[::-1]
    else:
        return (result[::-1], scores[::-1], indices[::-1])


def spacelessPartialMatch(s1, s2):
    s1 = s1.replace(' ', '')
    s2 = s2.replace(' ', '')
    return fwf.partial_ratio(s1, s2) == 100


def compare(s1, s2, checkCT = 1):
    w1 = s1.split(" ")
    w2 = s2.split(" ")
    # if len(w1) == 0 or len(w2)==0:
    #     print(w1, w2)
    # elif len(w1[0][0])==0 or len(w2[0][0])==0:
    #     print(w1, w2)
    if len(w1) < len(w2):
        wmin = w1
        wmax = w2
    else:
        wmin = w2
        wmax = w1
    j = 1
    i = 0
    CT = consecutiveTranspositions
    flag = False
    # special case - need another flag for atleast 1 exact match
    while i < len(wmin):
        if i == 0:
            if CT(wmin[i], wmax[i], 1) or (wmin[i][0] == wmax[i][0] and (len(wmin[i]) == 1 or len(wmax[i]) == 1)):
                # print(wmin[0][0], wmax[0][0], (wmin[0][0] == wmax[0][0]))
                i += 1
                continue
            # might get extra correct but may be error rate may increase
            elif wmin[i][0] == wmax[i][0] and fwf.partial_ratio(wmin[i], wmax[i])==100:
                 # print(s1, s2)
                i += 1
                continue
            else:
                return False
        flag = False
        while j < len(wmax):
            try:
                if CT(wmin[i], wmax[j], 1) or (wmin[i][0] == wmax[j][0] and (len(wmin[i]) == 1 or len(wmax[j]) == 1 or fwf.partial_ratio(wmin[i], wmax[j])==100)):
                    flag = True
                    j += 1
                    break
                else:
                    j += 1
            except e:
                print("Got issue", str(e), wmin, wmax, wmin[i], wmax[j])
                exit(0)
        if not flag and j == len(wmax) and i < len(wmin):
            return False
        i += 1
    # print(i, j, flag)
    return True


def consecutiveTranspositions(s1, s2, ct=1):
    l1, l2 = len(s1), len(s2)
    ls2 = list(s2)
    if l1 != l2:
        return False
    for m in range(l1):
        if s1[m] != ls2[m]:
            n = m
            for n in range(m+1, min(m+ct+1, l2)):
                if s1[m] == ls2[n]:
                    break
            ct -= (n-m)
            if ct < 0 or n == m:
                return False
            # rearrange
            temp = ls2[m]
            for i in range(m, n):
                ls2[i] = ls2[i+1]
            ls2[n] = temp
    return True


if __name__ == '__main__':
    print(compare("aditya guru", "aditya g"))
    print(compare("aditya g", "aditya guru"))
    print(compare("aditya g", "aditya kumar guru"))
    print(compare("aditya guru", "aditya b"))
    print(compare("aditya kumar guru", "aditya b"))
    print(compare("bditya guru", "aditya b"))
    print(compare("JOSPEH VARGHESE", "JOSEPH VARGHESE"))
    print(processString("Payal Electronics(P)"))
    print(processString('Deepak Fertilizers & Petrochemicals Corp Ltd'))
    print(removeHashNSpace("Pay & Go #P #L"))
    # print(wordwiseJaroWinkler("DEEPAK AGRO SOLUTIONS #L", "DEEPAK GULF LLC"))
    # print(wordwiseJaroWinkler("MANJU AGRO #P #L", "MANJU SHREE PLANTATION #L"))
    print(wordSetLevenstein("ACTIVE CHEMICAL #P", "ACTIVE CHEMICALS #P #L"))
    print(wordSetLevenstein("KETAN PLASTICS #P #L",
                            "KETAN PLASTIC INDUSTRIES #P #L"))
    print(wordSetLevenstein("NOVA TUBES #P #L", "NOVA TELESEC #P #L"))
    print(stringLevensteinFraction("NOVA TUBES #P #L", "NOVA TELESEC #P #L"))
    print(stringLevensteinFraction("CENTURY TEXTILES #L","CENTURY TEXTILE & INDUSTRIES #L"))
    print(fstwtdsetL("TRENT", "TRENT #L"))
    print(fstwtdsetL("INDIA FOILS #L #M","INDIA FOILS #L"))
    # print(getMatches("DEEPAK PHENOLICS #L", ["DEEPAK PHENOLICS #L", "DPL", "XYZ"], limit=2, cutoff=0,max_exact=2))
    pass
# "BALAJI INSTALMENT SU", "BALAJI INFRASTRUCTURE & DEVELOPMENT COMPANY #L"
# "SHERATON INTNL INC", "SHERATON PROPERTIES & FINANCE #L"
