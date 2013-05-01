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


from caseparser import Validator
import unittest

__all__ = ['TestFileValidation', 'TestParser']

class TestFileValidation(unittest.TestCase):
    '''Test functions that validate the input files.'''
    
    def setUp(self):
        self.v = Validator()
        pass
    
    def tearDown(self):
        pass
    
    def testTitle(self):
        good_file = '  = Foo v. Bar - Some other stuff = '
        bad_file = ' There\'s text before my title! = But there is a title ='
        bad_file2 = ' There\s no title at all!'
        self.failUnless(self.v.validateTitle(good_file), 'Validator did not pass a good title.')
        self.failIf(self.v.validateTitle(bad_file), 'Validator passed a title that was not at the beginning of the file.')
        self.failIf(self.v.validateTitle(bad_file2), 'Validator passed a file with no title.')
        
class TestParser(unittest.TestCase):
    '''Test functions that parse the plain text to wikitext.'''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testParseTitle(self):
        pass


if __name__ == "__main__":
    unittest.main()