#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

sys.path.append('..')

import unittest
from lexical import *

class WordCheck (unittest.TestCase):
    diff_cases = ((2,  ('Test',      'eTst')),
                  (2,  (u'Маголёт',  u'Могалёт')),
                  (1,  (u'Корова',   u'Карова')),
                  (3,  ('WakidzasI', 'Waki Dzasi')),
                  (18, ('i18n',      'internationalization')),
                  (3,  ('stubburn',  'tsuburn')))
    
    def testWordDiffs (self):
        print "Running words diff test"
        for diff, words in self.diff_cases:
            print words, lev_distance(words[0], words[1])
            self.assertEqual(diff, lev_distance(words[0], words[1]))


class PhraseCheck (unittest.TestCase):
    pos_cases = ((u'фсё врёт униттест этат ваш',
                   (u'врёт фсё, этат ваш униттест',
                    u'всё врёт, юниттест этот ваш')),
                  (u'йя пешу ниправильна с ашипками',
                   (u'ниправильна йя пешу с ашипками',
                    u'я пишу неправильно с ошибками')))
    
    def testWordPositions (self):
        print "Running words position in phrases test"
        for res, phrases in self.pos_cases:
            test = ' '.join(transform_phrase (phrases[0], phrases[1]))
            print ("'%s':'%s'") % (test, res)
            self.assertEqual(res, test)

    def testErrorCorrecting (self):
        pass

    def testFullPhraseCorrect (self):
        pass

if __name__ == '__main__':
    unittest.main()  
