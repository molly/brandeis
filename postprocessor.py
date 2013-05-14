# -*- coding: utf-8  -*-
#! python3
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

class Postprocessor(object):
    def __init__(self, file):
        self.filename = file
        
    def process(self):
        self.clean_spaces()
        self.multiline_bold()
        self.multiline_italic()
        self.fix_apostrophes()
        self.clean_spaces() #Once more for good measure.
    
    def clean_spaces(self):
        '''Make sure any line break consists of two spaces, avoid lines with just spaces on them.'''
        with open(self.filename, 'r', encoding='utf-8') as output:
            content = output.read()
        content = content.strip(' \t\n\r\f\v')
        content = content.replace('\n|\n', '')
        content = re.sub('\n(\s)*\n', '\n\n', content)
        content = content.replace('\n ', '\n')
        content = re.sub('(?<!\n)\n(?!\n)', '\n\n', content)
        with open(self.filename, 'w', encoding='utf-8') as output:
            output.write(content)
            
    def fix_apostrophes(self):
        with open(self.filename, 'r', encoding='utf-8') as output:
            content = output.read()
        content = content.replace('¤', "'")
        with open(self.filename, 'w', encoding='utf-8') as output:
            output.write(content)
            
    def multiline_bold(self):
        '''Deal with line breaks within bold text.'''
        with open(self.filename, 'r', encoding='utf-8') as output:
            content = output.read()
        content = re.split(r"'''((?:.|\n)*?)'''", content)
        new = ''
        for i in range(len(content)):
            if ( i%2 ):
                if '\n' in content[i]:
                    lines = content[i].split('\n')
                    print(lines)
                    for line in lines:
                        if line == '' or line == ' ':
                            new += '\n'
                        else:
                            new += "'''" + line + "'''"
                else:
                    new += content[i]
            else:
                new += content[i]
        with open(self.filename, 'w', encoding='utf-8') as output:
            output.write(new)
            
    def multiline_italic(self):
        '''Deal with line breaks within bold text.'''
        with open(self.filename, 'r', encoding='utf-8') as output:
            content = output.read()
        content = re.split(r"((?<!')''[^'](?:.|\n)*?[^']''(?!'))", content)
        new = ''
        for i in range(len(content)):
            if ( i%2 ):
                if '\n' in content[i]:
                    lines = content[i].split('\n')
                    print(lines)
                    for line in lines:
                        if line == '' or line == ' ':
                            new += '\n'
                        else:
                            new += "''" + line + "''"
                else:
                    new += content[i]
            else:
                new += content[i]
        with open(self.filename, 'w', encoding='utf-8') as output:
            output.write(new)