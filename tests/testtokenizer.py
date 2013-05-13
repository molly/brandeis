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
                           'full_title': 'Person One v. Person Two - 1 U.S. 111 (2000)'}
        self.tokenizer = Tokenizer(self.test_dict)
        self.base_token = "LexToken\({0}, '{1}',"
    
    def tearDown(self):
        pass
    
    def testJavaScript(self):
        content = '<script>I\'m Javascript!</script>'
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match Javascript.')
        self.assertEqual(result[0], 'JAVASCRIPT',
                         'Javascript tokenizer returned incorrect token type.')
        self.assertEqual(result[1], '<script>I\'m Javascript!</script>',
                         'Javascript tokenizer returned incorrect value.')
    
    def testIgnoredTag(self):
        content = "<div class=\"htmlclass\">"
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match ignored tag.')
        self.assertEqual(result[0], 'IGNORED_TAG',
                         'Ignored tag tokenizer returned incorrect token type.')
        self.assertEqual(result[1], 'div',
                         'Ignored tag tokenizer returned incorrect value.')
        
    def testLink(self):
        content = "<a class=\"page-name\">90</a>"
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match link.')
        self.assertEqual(result[0], 'LINK',
                         'Link tokenizer returned incorrect token type.')
        self.assertEqual(result[1], ('class="page-name"', '90'),
                         'Link tokenizer returned incorrect value.')
        
    def testComment(self):
        content = "<!-- I'm useless information! -->"
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match comment.')
        self.assertEqual(result[0], 'COMMENT',
                         'Comment tokenizer returned incorrect token type.')
        self.assertEqual(result[1], '<!-- I\'m useless information! -->',
                         'Comment tokenizer returned incorrect value.')
        
    def testTitle(self):
        content = "<h1>" + self.test_dict['full_title'] + "</h1>"
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match title.')
        self.assertEqual(result[0], 'TITLE',
                         'Title tokenizer returned incorrect token type.')
        self.assertEqual(result[1], 'Person One v. Person Two - 1 U.S. 111 (2000)',
                         'Title tokenizer returned incorrect value.')
                
    def testNewline(self):
        content = "\n"
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match newline.')
        self.assertEqual(result[0], 'NEWLINE',
                         'Newline tokenizer returned incorrect token type.')
        self.assertEqual(result[1], '\n',
                         'Newline tokenizer returned incorrect value.')
        
    def testSupremeLinks(self):
        content = "<ul class=\"supremelinks\"><li>Link</li></ul>"
        result = self.tokenizer.analyze(content)
        result = result[0] if result else self.fail('Failed to match supreme links.')
        self.assertEqual(result[0], 'SUPREMELINKS',
                         'Supreme links tokenizer returned incorrect token type.')
        self.assertEqual(result[1], '<li>Link</li>',
                         'Supreme links tokenizer returned incorrect value.')


if __name__ == '__main__':
    unittest.main()