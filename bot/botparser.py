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

class BotParser(object):
    
    def __init__(self, inputfile, output, metadict):
        self.inputfile = inputfile
        self.output = output
        self.metadict = metadict
        
    def sectionize(self):
        self.metadict['sections'] = dict()
        self.metadict['sections']['concurrence_justices'] = []
        self.metadict['sections']['dissent_justices'] = []
        self.metadict['sections']['concurrence'] = []
        self.metadict['sections']['dissent'] = []
        with open(self.inputfile, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        paras = content.split('\n\n')
        with open(self.output, 'w', encoding='utf-8') as output:
            for i in range(len(paras)):
                if len(paras[i]) < 400:
                    if 'syllabus' in paras[i].lower():
                        if 'syllabus' not in self.metadict['sections']:
                            output.write('SYLLABUS' + '-'*80 + '\n')
                            self.metadict['sections']['syllabus'] = i
                    elif re.search(r',\sconcurring(\.|\Z)', paras[i], re.IGNORECASE):
                        sentence_m = re.search(r'(\.|\A)(?P<justices>.*?),\sconcurring(\.|\Z)',
                                               paras[i], re.IGNORECASE)
                        if sentence_m:
                            sentence = sentence_m.group('justices')
                            justices = re.search(r'\{{2}sc\|(?:(?:Chief\s)?Justice\s)?(?P<justice>.*?)\}{2}', sentence)
                            justice = justices.group('justice')
                            if not justice in self.metadict['sections']['concurrence_justices']:
                                output.write('CONCURRENCE' + '-'*80 + '\n')
                                self.metadict['sections']['concurrence_justices'].append(justice)
                                self.metadict['sections']['concurrence'].append(i)
                    elif re.search(r',\sdissenting(\.|\Z)', paras[i], re.IGNORECASE):
                        sentence_m = re.search(r'(\.|\A)(?P<justices>.*?),\sdissenting(\.|\Z)',
                                               paras[i], re.IGNORECASE)
                        if sentence_m:
                            sentence = sentence_m.group('justices')
                            justices = re.search(r'\{{2}sc\|(?:(?:Chief\s)?Justice\s)?(?P<justice>.*?)\}{2}', sentence)
                            justice = justices.group('justice')
                            if not justice in self.metadict['sections']['dissent_justices']:
                                output.write('DISSENT' + '-'*80 + '\n')
                                self.metadict['sections']['dissent_justices'].append(justice)
                                self.metadict['sections']['dissent'].append(i)
                    elif 'per curiam' in paras[i].lower():
                        if 'per curiam' not in self.metadict['sections']:
                            output.write('PER CURIAM' + '-'*80 + '\n')
                            self.metadict['sections']['per curiam'] = i
                    elif 'delivered the opinion' in paras[i].lower():
                        if 'opinion' not in self.metadict['sections']:
                            output.write('OPINION' + '-'*80 + '\n')
                            self.metadict['sections']['opinion'] = i
                    output.write(paras[i])
                else:
                    output.write(paras[i])
                output.write("\n\n")
        print(self.metadict['sections'])