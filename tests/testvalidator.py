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


from validator import Validator
import os, unittest

__all__ = ['TestFileValidation']

class TestFileValidation(unittest.TestCase):
    '''Test functions that validate the input files.'''
    
    def setUp(self):
        self.v = Validator()
    
    def tearDown(self):
        try:
            os.remove('buffer.txt')
        except FileNotFoundError:
            pass
    
    def testGoodTitle(self):
        with open('buffer.txt', 'w', encoding='utf-8') as buffer:
            buffer.write('  = Foo v. Bar - Some other stuff = \n')
        self.assertTrue(self.v.validateTitle('buffer.txt'), 'Validator did not pass a good title.')
    
    def testPoorlyPlacedTitle(self):
        with open('buffer.txt', 'w', encoding='utf-8') as buffer:
            buffer.write(' There\'s text before my title!\n = But there is a title =\n')
        self.assertFalse(self.v.validateTitle('buffer.txt'), 'Validator passed a title that was not'
                         ' at the beginning of the file.')
        
    def testNoTitle(self):
        with open('buffer.txt', 'w', encoding='utf-8') as buffer:
            buffer.write(' There\s no title at all!\n')
        self.assertFalse(self.v.validateTitle('buffer.txt'), 'Validator passed a file with no'
                         ' title.')

if __name__ == "__main__":
    unittest.main()