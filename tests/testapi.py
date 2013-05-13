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
from bexceptions import *
import unittest

class TestAPIFunctions(unittest.TestCase):
    '''Test functions that communicate with the Wikisource API.'''
    
    def setUp(self):
        self.api = API()
    
    def tearDown(self):
        pass
    
# get_case_line()

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
    
# case_exists()
            
    def testExistingCase(self):
        self.assertTrue(self.api.case_exists("* [http://openjurist.org/60/us/393 60 U.S. 393] "
                                             "([[:Category:1790 works|1790]]) "
                                             "[[Dred Scott v. Sandford]]"), 
                        "Returned false for a case that exists on Wikisource.")
    
    def testNonexistentCase(self):
        self.assertFalse(self.api.case_exists("* [http://openjurist.org/67/us/17 67 U.S. 17] "
                                             "([[:Category:1851 works|1851]]) [[Silly case"
                                             "name that will never exist on Wikisource]]"), 
                        "Returned true for a case that does not exist on Wikisource.")

# filter_multiple

    def testAmbiguousCaseNumber(self):
        self.assertEqual(self.api.filter_multiple("BETHEL v. LLOYD",
                                               ['* 1 U.S. 2 (Pa. 1759) [[Hyam v. Edwards]]',
                                                '* [http://openjurist.org/1/us/2 1 U.S. 2] [[Bethel v. Lloyd]]',
                                                '* 1 U.S. 2 (Pa. 1759) [[Lewis v. Stammers]]']),
                         '* [http://openjurist.org/1/us/2 1 U.S. 2] [[Bethel v. Lloyd]]',
                         "Returned an incorrect match for a case matching several numbers.")
        
    def testAmbiguousCaseNumberAndName(self):
            self.assertIsNone(self.api.filter_multiple("DAVEY v. TURNER",
                                                      ['* [http://openjurist.org/1/us/11 1 U.S. 11] [[Hugh Davey et Ux. v. Peter Turner]]',
                                                       "* 1 U.S. 11 (Pa. 1764) [[King's Road]]",
                                                       '* 1 U.S. 11 (Pa. 1764) [[Davey v. Turner]]']),
                              "Did not return None for an ambiguous case number AND name.")
                                                      

if __name__ == '__main__':
    unittest.main()