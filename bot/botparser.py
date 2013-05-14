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

class BotParser(object):
    
    def __init__(self, inputfile, output, metadict):
        self.inputfile = inputfile
        self.output = output
        self.metadict = metadict
        
    def sectionize(self):
        self.metadict['sections'] = dict()
        self.metadict['sections']['concurrence'] = []
        self.metadict['sections']['dissent'] = []
        with open(self.inputfile, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        paras = content.split('\n\n')
        with open(self.output, 'w', encoding='utf-8') as output:
            for i in range(len(paras)):
                if len(paras[i]) < 400:
                    if 'syllabus' in paras[i].lower():
                        output.write('SYLLABUS' + '-'*80 + '\n')
                        self.metadict['sections']['syllabus'] = i
                    elif ', concurring.' in paras[i].lower():
                        output.write('CONCURRENCE' + '-'*80 + '\n')
                        self.metadict['sections']['concurrence'].append(i)
                    elif ', dissenting.' in paras[i].lower():
                        output.write('DISSENT' + '-'*80 + '\n')
                        self.metadict['sections']['dissent'].append(i)
                    elif 'per curiam' in paras[i].lower():
                        if 'per curiam' not in self.metadict['sections']:
                            output.write('PER CURIAM' + '-'*80 + '\n')
                            self.metadict['sections']['per curiam'] = i
                    output.write(paras[i])
                else:
                    output.write(paras[i])
                output.write("\n\n")
        print(self.metadict['sections'])