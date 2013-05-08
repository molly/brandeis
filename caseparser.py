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

import logging, re

class Parser(object):
    '''The parser converts the raw case text from lochner to a dictionary object. This is later
    converted to wikitext to be uploaded.'''
    
    def __init__(self):
        self.logger = logging.getLogger('brandeis')
        self.output = None

    def parse(self, tokens, output_file):
        '''Run the parser functions on the file.'''
        self.output = output_file
        self.tokens = tokens
        self.dispatch()
        
    def dispatch(self):
        for token in self.tokens:
            self.value = token[1]
            if self.value:
                command = 'self.{0}()'.format(token[0].lower())
                try:
                    exec(command)
                except:
                    self.logger.error("Unable to run command " + command);
                    break;
                else:
                    self.write(self.value)
    
    def write(self, text):
        if type(text) is str:
            self.output.write(text)
        
def get_metadata(metadict, filename):
    '''Pull the title from the file.'''
    with open(filename, 'r', encoding='utf-8') as file:
        first_line = file.readline()
    title = re.match(r'\s*=\s(?P<full>(?P<title>(?P<petitioner>.*?)\sv\.\s(?P<respondent>.*?))\s\-\s(?P<number>(?P<volume>\d{1,3})\s(?P<abbr>U.S.)\s(?P<page>\d{1,3}))\s\((?P<date>\d{4})\))\s=\s*', first_line)
    metadict["full_title"] = title.group("full")
    metadict["title"] = title.group("title")
    metadict["petitioner"] = title.group("petitioner")
    metadict["respondent"] = title.group("respondent")
    metadict["number"] = title.group("number")
    metadict["volume"] = title.group("volume")
    metadict["title"] = title.group("title")
    metadict["abbr"] = title.group("abbr")
    metadict["page"] = title.group("page")
    metadict["date"] = title.group("date")