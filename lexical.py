#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

def cycle_list (lst, dir=1):
    if dir == 1:
        return [lst[len(lst) - 1]] + lst[:len(lst) - 1]
    else:
        return lst[1:] + [lst[0]]

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


# TODO: This is dummy function, the idea is:
# Try to find errored written words, Then try to swap words
# Концерты Визбора | Визбор - Концерты
def PhraseCheck(phrase1, phrase2):
    match = re.compile('[^\w]+', re.UNICODE)
    lst1, lst2 = match.split(phrase1), match.split(phrase2)
    if len(lst1) < len(lst2):
        lst1 = lst1 + ['']*(len(lst2) - len(lst1))
    elif len(lst2) < len(lst1):
        lst2 = lst2 + ['']*(len(lst1) - len(lst2))
    res = map(lambda x,y: lev_distance(x,y), lst1, lst2)
    print res
    return reduce(lambda x,y: x + y, res)

# Idiotizm:
def PhraseCheck(phrase1, phrase2):
    match = re.compile('[^\w]+', re.UNICODE)
    lst1, lst2 = match.split(phrase1), match.split(phrase2)
    
    if len(lst1) < len(lst2):
        lst1 = lst1 + ['']*(len(lst2) - len(lst1))
    elif len(lst2) < len(lst1):
        lst2 = lst2 + ['']*(len(lst1) - len(lst2))

    res = reduce(lambda x,y: x + y,
                 map(lambda x,y: lev_distance(x,y), lst1, lst2))
    for x in xrange(len(lst1)):
         lst_tmp = cycle_list(lst1)
         res_tmp = reduce(lambda x,y: x + y,
                          map(lambda x,y: lev_distance(x,y), lst_tmp, lst2))
         if (res_tmp < res):
             lst1 = lst_tmp
    return lst1
         
        

res = PhraseCheck(u'Концерты - тут Визбор былв', u'Концерты Визбора были тут')
print u' '.join(res)
