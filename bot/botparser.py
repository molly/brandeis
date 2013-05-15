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

from bexceptions import MissingFootnote
import logging, re

class BotParser(object):
    
    def __init__(self, inputfile, output, metadict):
        self.output = output
        self.metadict = metadict
        self.logger = logging.getLogger('brandeis')
        with open(inputfile, 'r', encoding='utf-8') as in_file:
            content = in_file.read()
        with open(self.output, 'w', encoding='utf-8') as outputfile:
            outputfile.write(content)
        
    def footnotes(self):
        if 'max_footnote' in self.metadict:
            max_footnote = self.metadict['max_footnote']
            self.logger.warning("Added footnotes to the text. ({0} sections: {1})."
                                .format(len(max_footnote), str(max_footnote)))
            for sect in range(1, len(max_footnote)+1):
                with open(self.output, 'r', encoding='utf-8') as inputfile:
                    content = inputfile.read()
                section = '' if sect == 1 else str(sect) + '/'
                footnote_start = content.find('Footnote ' + section + '1')
                content = [content[:footnote_start], content[footnote_start:]]
                text = content[0]
                footnotes = content[1]
                footnotes = footnotes.split('\n\n')
                foot_no = 1
                ind = 0
                foot_text = ''
                footnote_texts = []
                while ind < len(footnotes) and foot_no <= int(max_footnote[str(sect)]):
                    if footnotes[ind] == 'Footnote ' + section + str(foot_no):
                        ind += 1
                        if foot_no == max_footnote[str(sect)]:
                            foot_text += footnotes[ind]
                            ind += 1
                        else:
                            while ind < len(footnotes) and footnotes[ind] != 'Footnote ' + section + str(foot_no + 1):
                                if foot_text != '':
                                    foot_text += '\n\n'
                                foot_text += footnotes[ind]
                                ind += 1
                        footnote_texts.append(foot_text)
                        foot_text = ''
                        foot_no += 1
                    else:
                        raise MissingFootnote( foot_no )
                trailing = '\n\n'.join(footnotes[ind:])
                  
                end_footnote = '</ref>'
                for i in range(1,int(max_footnote[str(sect)])+1):
                    split = []
                    current_footnote = '<ref name="ref{}">'.format(section + str(i))
                    x = text.find(current_footnote)
                    if x == -1:
                        self.logger.warning("Unable to find an in-text tag for footnote #" +
                                            section + str(i) + ". It has been omitted.")
                        continue
                    split.append(text[:x+len(current_footnote)])
                    split.append(text[x+len(current_footnote):])
                    footnote_texts[i-1] = ' ' if footnote_texts[i-1] == '' else footnote_texts[i-1]
                    text = split[0] + footnote_texts[i-1] + split[1]
              
                with open(self.output, 'w', encoding='utf-8') as output:
                    output.write(text + trailing)
                    
            with open(self.output, 'a', encoding='utf-8') as output:
                output.write('{{smallrefs}}\n')
                    
    def pages(self):
        '''Replace page numbers with {{page break}} template, join any hyphenated words.'''
        with open(self.output, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        split = re.split(r'(\n{2}PAGE\s\d+\n{2})', content)
        for i in range(len(split)):
            if split[i][:6] == '\n\nPAGE':
                number_m = re.match(r'\n{2}PAGE\s(?P<number>\d+)\n{2}', split[i])
                split[i] = (' \n{{page break|' + number_m.group('number') + 
                            '|left}}\n')
            elif split[i][-1] == '-':
                temp = split[i+2].split(' ', 1)
                split[i] = split[i][:-1] + temp[0]
                split[i+2] = temp[1]        
        content = '<div class="indented-page">' + ''.join(split) + '</div>'
        with open(self.output, 'w', encoding='utf-8') as output:
            output.write(content)

    def sectionize(self):
        self.metadict['sections'] = dict()
        self.metadict['sections']['concurrence_justices'] = []
        self.metadict['sections']['dissent_justices'] = []
        self.metadict['sections']['concurrence'] = []
        self.metadict['sections']['dissent'] = []
        with open(self.output, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        paras = content.split('\n\n')
        with open(self.output, 'w', encoding='utf-8') as output:
            for i in range(len(paras)):
                if len(paras[i]) < 400:
                    if 'syllabus' in paras[i].lower():
                        if 'syllabus' not in self.metadict['sections']:
                            output.write('SYLLABUS' + '-'*80 + '\n\n')
                            self.metadict['sections']['syllabus'] = i
                    elif re.search(r',\sconcurring(\.|\Z)', paras[i], re.IGNORECASE):
                        sentence_m = re.search(r'(\.|\A)(?P<justices>.*?),\sconcurring(\.|\Z)',
                                               paras[i], re.IGNORECASE)
                        if sentence_m:
                            sentence = sentence_m.group('justices')
                            justices = re.search(r'\{{2}sc\|(?:(?:Mr\.\s)?(?:Chief\s)?Justice\s)?(?P<justice>.*?)\}{2}', sentence)
                            justice = justices.group('justice')
                            if not justice in self.metadict['sections']['concurrence_justices']:
                                output.write('CONCURRENCE' + '-'*80 + '\n\n')
                                self.metadict['sections']['concurrence_justices'].append(justice)
                                self.metadict['sections']['concurrence'].append(i)
                    elif re.search(r',\sdissenting(\.|\Z)', paras[i], re.IGNORECASE):
                        sentence_m = re.search(r'(\.|\A)(?P<justices>.*?),\sdissenting(\.|\Z)',
                                               paras[i], re.IGNORECASE)
                        if sentence_m:
                            sentence = sentence_m.group('justices')
                            justices = re.search(r'\{{2}sc\|(?:(?:Mr\.\s)?(?:Chief\s)?Justice\s)?(?P<justice>.*?)\}{2}', sentence)
                            justice = justices.group('justice')
                            if not justice in self.metadict['sections']['dissent_justices']:
                                output.write('DISSENT' + '-'*80 + '\n\n')
                                self.metadict['sections']['dissent_justices'].append(justice)
                                self.metadict['sections']['dissent'].append(i)
                    elif 'per curiam' in paras[i].lower():
                        if 'per curiam' not in self.metadict['sections']:
                            output.write('PER CURIAM' + '-'*80 + '\n\n')
                            self.metadict['sections']['per curiam'] = i
                    elif 'delivered the opinion' in paras[i].lower():
                        if 'opinion' not in self.metadict['sections']:
                            output.write('OPINION' + '-'*80 + '\n\n')
                            self.metadict['sections']['opinion'] = i
                    output.write(paras[i])
                else:
                    output.write(paras[i])
                output.write("\n\n")
        self.logger.warning("Sections: ")
        for key in self.metadict['sections']:
            value = self.metadict['sections'][key]
            if 'justices' in key and len(value) is not 0:
                self.logger.warning("\t" + key + ": " + ', '.join(value))
            elif type(value) is int:
                self.logger.warning("\t" + key + ": 1")
            elif type(value) is list and len(value) is not 0:
                self.logger.warning("\t" + key + ": " + str(len(value)))
            else:
                self.logger.warning("\tNo " + key + ".")