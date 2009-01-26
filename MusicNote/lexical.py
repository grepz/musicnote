# -*- coding: utf-8 -*-

#  lexical.py -- ondisk Music data crawler with a number of features
#
#  Copyright 2009 Stanislav M. Ivankin <stas@concat.info>
#
#  This file is part of musicnote.
#
#  musicnote is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  musicnote is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with musicnote.  If not, see <http://www.gnu.org/licenses/>.

import re, sys
from tools import *

def find_min (entity, lst):
    '''Find minimal distance of word in list of words'''
    score = lev_distance (entity, lst[0])

    def _find_min (entity, lst, score):
        if lst:
            score_new = lev_distance (entity, lst[0])
            return _find_min (entity, lst[1:],
                              (score_new < score and [score_new] or [score])[0])
        else:
            return score

    return _find_min (entity, lst[1:], score)

rus_utf8_trans_table = {
    u'а'  :  'a',    u'б'  :  'b',
    u'в'  :  'v',    u'г'  :  'g',
    u'д'  :  'd',    u'е'  :  'e',
    u'ё'  :  'yo',   u'ж'  :  'zh',
    u'з'  :  'z',    u'и'  :  'i',
    u'й'  :  'j',    u'к'  :  'k',
    u'л'  :  'l',    u'м'  :  'm',
    u'н'  :  'n',    u'о'  :  'o',
    u'п'  :  'p',    u'р'  :  'r',
    u'с'  :  's',    u'т'  :  't',
    u'у'  :  'u',    u'ф'  :  'f',
    u'х'  :  'h',    u'ц'  :  'c',
    u'ч'  :  'ch',   u'ш'  :  'sh',
    u'щ'  :  'sch',  u'ь'  :  '\'',
    u'ы'  :  'y',    u'э'  :  '`e',
    u'ю'  :  'yu',   u'я'  :  'ya'
    }

# TODO: Rewrite this function, make it fore usefull (Case condition
def translit_str (string):
    '''Transform utf-8 string of russian symbols to latin, by
    transliting them'''
    res = ''
    for x in string:
        x = x.lower()
        if x in rus_utf8_trans_table:
            res += rus_utf8_trans_table[x]
        else:
            res += x
    return res

def phrases_to_lists (phr1, phr2):
    '''Transform phrases to lists, make this lists of the same length'''
    match = re.compile('[^\w]+', re.UNICODE)
    lst1, lst2 = stretch_list (match.split(phr1),
                               match.split(phr2),
                               fill=' ')
    return lst1, lst2

def lev_distance(word1, word2, ignorecase=False):
    '''Find distance between words, used to guess errors between
    tags of the same entity'''
    if ignorecase:
        word1, word2 = word1.upper(), word2.upper()
    n, m = len(word1), len(word2)
    if n > m:
        word1, word2 = word2, word1
        n, m = m, n
    current_row = range(n+1)
    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*m
        for j in range(1,n+1):
            add, delete, change = (previous_row[j]+1,
                                   current_row[j-1]+1,
                                   previous_row[j-1])
            if word1[j-1] != word2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
            
    return current_row[n]

def total_phrase_diff (phr1, phr2):
    '''Calculate distance of every word in both phrases, then
    calculate sum of differences'''
    lst1, lst2 = phrases_to_lists (phr1, phr2)
    
    return reduce(lambda x,y: x + y,
                  map(lambda x,y: lev_distance(x,y),
                      lst1, lst2))

# TODO: Optimize, too many lists and iterations.
#def transform_phrase (phr1, phr2):
def reposition_list (lst1, lst2):
    '''Find closest words of lst1 and lst2 and reposition them in lst1
    to correspond each other'''
    lng = len (lst1)
    assert (lng == len (lst2))
    res_lst = [''] * lng

    # Simplier way to sort differences?
    def _dist_sort (x, y):
        if x[1]>y[1]:
            return 1
        elif x[1]==y[1]:
            return 0
        else: 
            return -1    
    # For every word in list1 generate list of differences against
    # words in list2 in form [n,m], where n in position of word in
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
            # Add list1 word index
            x[j] += [j]
        x.sort(cmp=_dist_sort)
        for fx in last:
            # Filter already used words
            x = filter (lambda x: x[2] != fx, x)
        last += [x[0][2]]
        res_lst[i] = lst1[x[0][2]]

    return res_lst

def calculate_diff_score ():
    pass

def filter_phrases (phr1, phr2):
    ''' Return True if phrases match against each other, score is
    calculated to guess the match condition'''
    lst1, lst2 = phrases_to_lists (phr1, phr2)
    lst1 = reposition_list (lst1, lst2)
    res = 0
    for x, y in zip(lst1, lst2):
        res += lev_distance (x, y, ignorecase=True)
    # TODO: Need to figure out how to calculate score
    if res <= len(lst1) * 2:
        return True
    else:
        return False

def assemble_groups (raw_list):
    '''Assemble similar phrases in groups, first phrase is phrase
    group leader'''
    def _assemble_groups (x, raw_list):
        if raw_list:
            # Restack elements, parse every element in list, and
            # concatenate it with matched phrases
            return _assemble_groups (
                x + [[raw_list[:1][0],
                      filter (lambda y: \
                              filter_phrases(raw_list[:1][0],y),raw_list[1:])]],
                raw_list[1:])
        else:
            return x
    return _assemble_groups ([], raw_list)

#print assemble_groups (["Therion singing",
#                        "THERION singing",
#                        "Therion sinnng",
#                        "In Flames",
#                        "fdsfsdfsdf",
#                        "Thir sinnng"])
