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
    def __init__(self, wikidict):
        self.wikidict = wikidict

    def parse(self, filename):
        '''Run the parser functions on the file.'''
        file = open(filename, 'r', encoding='utf-8')
        self.get_title(file)
        file.close()
        
    def get_title(self, file):
        '''Pull the title from the file.'''
        first_line = file.readline()
        title = re.match(r'\s*=\s(?P<full>(?P<title>.*?)\s\-\s(?P<number>.*?)\s\((?P<date>\d{4})\))\s=\s*', first_line)
        self.wikidict["full_title"] = title.group("full")
        self.wikidict["title"] = title.group("title")
        self.wikidict["number"] = title.group("number")
        self.wikidict["date"] = title.group("date")
