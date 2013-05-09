# -*- coding: utf-8  -*-
# Brandeis - A tool to convert plaintext court cases (from the lochner
# tool: http://gitorious.org/lochner/) to wikitext.
# 
# Copyright (C) 2013 Molly White
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tokenizer import Tokenizer
from bexceptions import *
import unittest

class TestTokenizer(unittest.TestCase):
    '''Test tokenizer module.'''
    
    def setUp(self):
        self.test_dict = {'respondent': 'Person 2',
                           'abbr': 'U.S.',
                           'petitioner': 'Person 1',
                           'volume': '111',
                           'number': '1 U.S. 111',
                           'page': '111',
                           'title': 'Person One v. Person Two',
                           'date': '2000',
                           'full_title': '= Person One v. Person Two - 1 U.S. 111 (2000) ='}
        self.tokenizer = Tokenizer(self.test_dict)
        self.base_token = "LexToken\({0}, '{1}',"
    
    def tearDown(self):
        pass
    
    def testFullTitle(self):
        content = "= Person One v. Person Two - 1 U.S. 111 (2000) = \n"
        result = self.tokenizer.analyze(content)[0]
        self.assertEqual(result[0], 'FULL_TITLE',
                         'Title tokenizer returned incorrect token type.')
        self.assertEqual(result[1], 'Person One v. Person Two - 1 U.S. 111 (2000)',
                         'Title tokenizer returned incorrect value.')
    
    def testShortTitle(self):
        content = "\n\nPerson One v. Person Two\n\n"
        result = self.tokenizer.analyze(content)[0]
        self.assertEqual(result[0], 'SHORT_TITLE',
                         'Short title tokenizer returned incorrect token type.')
        self.assertEqual(result[1], 'Person One v. Person Two',
                         'Short title tokenizer returned incorrect value.')
        
    def testTerm(self):
        content = "\n\nJanuary Term, 1999\n\n"
        result = self.tokenizer.analyze(content)[0]
        self.assertEqual(result[0], 'TERM',
                         'Term tokenizer returned incorrect token type.')
        self.assertEqual(result[1], 'January Term, 1999',
                         'Term tokenizer returned incorrect value.')

if __name__ == '__main__':
    unittest.main()