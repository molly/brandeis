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
from exceptions import *
import os, unittest

__all__ = ['TestFileValidation']

class TestFileValidation(unittest.TestCase):
    '''Test functions that validate the input files.'''
    
    def setUp(self):
        pass
    
    def tearDown(self):
        self.buffer.close()
    
    def testGoodTitlePlacement(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write('  = Foo v. Bar - Some other stuff = \n')
        v = Validator('buffer.txt')
        try:
            v.validateTitlePlacement()
        except:
            self.fail('Validator did not pass a good title.')
    
    def testPoorlyPlacedTitle(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write(' There\'s text before my title!\n = But there is a title =\n')
        v = Validator('buffer.txt')
        with self.assertRaises(BadTitle, msg='Validator passed a title that was not at the '
                               'beginning of the file.'):
            v.validateTitlePlacement()
        
    def testNoTitle(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write(' There\s no title at all!\n')
        v = Validator('buffer.txt')
        with self.assertRaises(BadTitle, msg='Validator passed a file with no title.'):
            v.validateTitlePlacement()
    
    def testGoodTitleParts(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write('= Foo v. Bar - 100 U.S. 200 (2013) =')
        v = Validator('buffer.txt')
        try:
            v.validateTitleParts()
        except:
            self.fail('Validator did not pass a title with good parts.')
    
    def testIdentifyCaseGroup(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write('= Group of Cases - 100 U.S. 200 (2013) =')
        v = Validator('buffer.txt')
        with self.assertRaises(ValidatorError, msg='Validator failed to identify a group of cases'
                               ' as such.'):
            v.validateTitleParts()
    
    def testBadTitleDate(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write('= Foo v. Bar - 100 U.S. 200 (203) =')
        v = Validator('buffer.txt')
        with self.assertRaises(BadTitle, msg='Validator passed a title containing an improperly'
                         'formatted date.'):
            v.validateTitleParts()
        
    def testBadTitleNumber(self):
        with open('buffer.txt', 'w', encoding='utf-8') as self.buffer:
            self.buffer.write('= Foo v. Bar - U.S. 200 (2013) =')
        v = Validator('buffer.txt')
        with self.assertRaises(BadTitle, msg='Validator passed a title containing an improperly'
                         'formatted case number.'):
            v.validateTitleParts()

if __name__ == "__main__":
    unittest.main()
    try:
        os.remove('buffer.txt')
    except:
        pass