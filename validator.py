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
    
    def __init__(self):
        pass
    
    def validate(self, filename):
        '''Run various validation functions to try to weed out any improperly-formatted
        files.'''
        if not self.validateTitle(filename):
            raise BadTitle("Bad title in file: " + filename)
    
    def validateTitle(self, filename):
        '''Check a file to make sure it has a properly-formatted title.'''
        with open(filename, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            title = re.match(r'^\s*=\s.*\s=\s*$', first_line, re.MULTILINE)
        if title:
            return True
        else:
            return False
    
    