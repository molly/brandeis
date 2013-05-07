# -*- coding: utf-8  -*-
# Brandeis - A tool to convert plaintext court cases (from the lochner
# tool: http://gitorious.org/lochner/) to wikidict.
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

import re

__all__ = ['Parser']

class Parser(object):
    '''The parser converts the raw case text from lochner to a dictionary object. This is later
    converted to wikitext to be uploaded.'''
    def __init__(self, wikidict, filename):
        self.filename = filename
        self.wikidict = wikidict
        self.file = open(filename, 'r', encoding='utf-8')

    def parse(self, filename):
        '''Run the parser functions on the file.'''
        pass
        
    def get_title(self):
        '''Pull the title from the file.'''
        first_line = self.file.readline()
        title = re.match(r'\s*=\s(?P<full>(?P<title>(?P<petitioner>.*?)\sv\.\s(?P<respondent>.*?))\s\-\s(?P<number>(?P<volume>\d{1,3})\s(?P<abbr>U.S.)\s(?P<page>\d{1,3}))\s\((?P<date>\d{4})\))\s=\s*', first_line)
        self.wikidict["full_title"] = title.group("full")
        self.wikidict["title"] = title.group("title")
        self.wikidict["petitioner"] = title.group("petitioner")
        self.wikidict["respondent"] = title.group("respondent")
        self.wikidict["number"] = title.group("number")
        self.wikidict["volume"] = title.group("volume")
        self.wikidict["title"] = title.group("title")
        self.wikidict["abbr"] = title.group("abbr")
        self.wikidict["page"] = title.group("page")
        self.wikidict["date"] = title.group("date")