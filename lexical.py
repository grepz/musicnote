#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

# TODO: Don't forget to handle upper case
def lev_distance(word1, word2):
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
def PhraseCheck(phrase1, phrase2):
     lst1, lst2 = re.split('[^\w]+', phrase1), re.split('[^\w]+', phrase2)
     if len(lst1) < len(lst2):
         lst1 = lst1 + ['']*(len(lst2) - len(lst1))
     elif len(lst2) < len(lst1):
         lst2 = lst2 + ['']*(len(lst1) - len(lst2))

     return reduce(lambda x,y: x + y, map(lambda x,y: lev_distance(x,y), lst1, lst2))
