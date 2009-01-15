#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, sys

l_print = lambda *x:sys.stdout.write(" ".join(map(str,x)) + '\n')

def cycle_list (lst, dir=1):
    if dir == 1:
        return [lst[len(lst) - 1]] + lst[:len(lst) - 1]
    else:
        return lst[1:] + [lst[0]]

def normalize_list (lst1, lst2):
    if len(lst1) < len(lst2):
        lst1 = lst1 + ['']*(len(lst2) - len(lst1))
    elif len(lst2) < len(lst1):
        lst2 = lst2 + ['']*(len(lst1) - len(lst2))

    return lst1, lst2

def transpose (m):
    lng = len(m)
    m_t = []
    for j in range(lng):
        row = []
        for i in range(lng):
            row.append(m[i][j])
        m_t += [row]
    return m_t

def find_min (entity, lst):
    score = lev_distance (entity, lst[0])

    def _find_min (entity, lst, score):
        if lst:
            score_new = lev_distance (entity, lst[0])
            return _find_min (entity, lst[1:], (score_new < score and [score_new] or [score])[0])
        else:
            return score

    return _find_min (entity, lst[1:], score)

# TODO: Don't forget to handle upper case
def lev_distance(word1, word2):
    """Find distance between words, used to guess errors between
    tags of the same entity
    """    
    n, m = len(word1), len(word2)
    if n > m:
        word1, word2 = word2, word1
        n, m = m, n
    current_row = range(n+1)
    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*m
        for j in range(1,n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if word1[j-1] != word2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
            
    return current_row[n]

def total_phrase_diff (phrase1, phrase2):
    match = re.compile('[^\w]+', re.UNICODE)
    lst1, lst2 = normalize_list (match.split(phrase1), match.split(phrase2))

    res = map(lambda x,y: lev_distance(x,y), lst1, lst2)
    
    return reduce(lambda x,y: x + y, res)

# TODO: Optimize, too many lists and iterations.
def PhraseCheck (phr1, phr2):
    match = re.compile('[^\w]+', re.UNICODE)
    lst1, lst2 = normalize_list (match.split(phr1), match.split(phr2))
    lng = len(lst1)
    res_lst = [''] * lng
    
    def _dist_sort (x, y):
        if x[1]>y[1]:
            return 1
        elif x[1]==y[1]:
            return 0
        else: 
            return -1
    
    # For every word in list1 generate list of differences against
    # words in list2 in form [ n, m ], where n in position of word in
    # list2, and m is its difference
    dist = []
    for elem1 in lst1:
        dist_inner = []
        for i, elem2 in enumerate (lst2):
            dist_inner += [[i, lev_distance (elem1, elem2)]]
        dist += [dist_inner]
    # Sort words, every column is related by it's index to word
    # position
    dist = transpose(dist)
    last = []
    for i,x in enumerate (dist):
        for j in range(lng):
            x[j] += [j]
        x.sort(cmp=_dist_sort)
        for fx in last:
            # Filter already used words
            x = filter (lambda x: x[2] != fx, x)
        last += [x[0][2]]
        res_lst[i] = lst1[x[0][2]]

    return res_lst
