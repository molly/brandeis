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

from api import API
from exceptions import *
from urllib import parse, request
import unittest, json, re

__all__ = ['TestFileValidation']

class TestFileValidation(unittest.TestCase):
    '''Test functions that communicate with the Wikisource API.'''
    
    def setUp(self):
        self.api = API()
    
    def tearDown(self):
        pass
    
    def testBadRequest(self):
        with self.assertRaises(PageNotFound, msg='Validator passed a page that had no content.'):
            self.api.get_case_line('title', '800', '25')
            
    def testNormalRequest(self):
        self.assertTrue(self.api.get_case_line('Charles River Bridge v. Warren Bridge', '36', '420'),
                         'Could not find an existing entry.')
        
    def testFallbackRequest(self):
        self.assertTrue(self.api.get_case_line("Lessee of Pollard's Heirs v. Kibbe", '39', '353'),
                         'Could not find an existing entry using the fallback regex.')
        
    def testNotInList(self):
        with self.assertRaises(NoCaseInList, msg='Returned an entry for a non-existent case.'):
            self.api.get_case_line('CaseName', '39', '800')
        
if __name__ == '__main__':
    unittest.main()
            
    