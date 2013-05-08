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
        self.tokenizer = Tokenizer()
        self.base_token = "LexToken\({0}, '{1}',"
    
    def tearDown(self):
        pass
    
    def testTitle(self):
        title = "= Name of case - 1 U.S. 111 (2000) = \n"
        result = self.tokenizer.analyze(title)[0]
        self.assertEqual(result[0], 'TITLE',
                         'Title tokenizer returned incorrect token type.')
        self.assertEqual(result[1], 'Name of case - 1 U.S. 111 (2000)',
                         'Title tokenizer returned incorrect value.')

if __name__ == '__main__':
    unittest.main()