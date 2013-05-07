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

import re
from exceptions import BadTitle

__all__ = ['Validator']

class Validator(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'r', encoding='utf-8')
        
    def __del__(self):
        self.file.close()
    
    def validate(self):
        '''Run various validation functions to try to weed out any improperly-formatted
        files.'''
        if not self.validateTitle():
            raise BadTitle("Bad title in file: " + self.filename)
        if not self.validateTitleParts():
            raise BadTitle("Bad title parts in file: " + self.filename)
    
    def validateTitle(self):
        '''Check a file to make sure it has a properly-formatted title. The title should be the
        first line of the text file, and of the format:
         = Title = 
        There should a leading and trailing space.'''
        first_line = self.file.readline()
        title = re.match(r'^\s*=\s.*\s=\s*$', first_line, re.MULTILINE)
        if title:
            return True
        else:
            return False
        
    def validateTitleParts(self):
        '''Check that the title can be broken into valid parts. Each title has the short title, 
        case number, and date. The title can be of any format. The case number is of the format:
        ### U.S. ###
        with 1-3 digits in each number. The date is of the format:
        (####)
        The full format of the title is:
         = Title - Number Date = 
        '''
        first_line = self.file.readline()
        title = re.match(r'^\s*=\s.*\s=\s*$', first_line, re.MULTILINE)
        if not title:
            return False
        parts = re.match(r'\s*=\s(?P<full>(?P<title>.*?)\s\-\s(?P<number>.*?)\s\((?P<date>\d{4})\))\s=\s*',
                         title.group())
        if not parts:
            return False
        number = re.match(r'\d{1,3}\sU.S.\s\d{1,3}', parts.group('number'))
        date = re.match(r'\d{4}', parts.group('date'))
        if not parts.group('title') or not number or not date:
            return False
        else:
            return True