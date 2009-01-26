# -*- coding: utf-8 -*-

#  tools.py -- ondisk Music data crawler with a number of features
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

__all__ = ['d_print', 'cycle_list', 'stretch_list', 'transpose']

l_print = lambda *x:sys.stdout.write(' '.join(map(str,x)) + '\n')

def d_print (verbose, fmt, *values):
    if verbose:
        print ('Debug: ' + fmt % values)

def cycle_list (lst, dir=1):
    '''Cycle list by one element to the dir, where dir == 1 means to
    the right, everything else - to the left'''
    if dir == 1:
        return [lst[len(lst) - 1]] + lst[:len(lst) - 1]
    else:
        return lst[1:] + [lst[0]]

def stretch_list (lst1, lst2, fill=None):
    '''Stretch lesser list to it\'s bigger brother, fill with fill
    empty cells'''
    if len(lst1) < len(lst2):
        lst1 = lst1 + [fill]*(len(lst2) - len(lst1))
    elif len(lst2) < len(lst1):
        lst2 = lst2 + [fill]*(len(lst1) - len(lst2))

    return lst1, lst2

def transpose (m):
    '''Transpose square matrix'''
    lng = len(m)
    m_t = []
    for j in range(lng):
        row = []
        for i in range(lng):
            row.append(m[i][j])
        m_t += [row]
    return m_t
