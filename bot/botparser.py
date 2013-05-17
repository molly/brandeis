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
        self.case_caption = ('{{{{CaseCaption \n| court = United States Supreme Court\n| volume = '
                             '{volume}\n| reporter = U.S.\n| page = {page}\n| party1 = {petitioner}'
                             '\n| party2 = {respondent}\n| lowercourt = \n| argued = {argued} \n| '
                             'decided = {decided}\n| case no = {case_number}\n}}}}')
        self.header = ('{{{{header\n | title = {{{{subst:PAGENAME}}}}\n | author = \n | translator '
                       '= \n | section = {{{{subst:SUBPAGENAME}}}}\n | previous = {previous}\n | next = {next}\n'
                       ' | year = {year}\n | notes = \n | categories = \n| portal = Supreme Court of '
                       'the United States\n}}}}')
        self.months = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        with open(inputfile, 'r', encoding='utf-8') as in_file:
            content = in_file.read()
        with open(self.output, 'w', encoding='utf-8') as outputfile:
            outputfile.write(content)
        
    def add_templates(self):
        '''Add templates to the top of the syllabus page.'''
        with open(self.output, 'r', encoding='utf-8') as input:
            top = input.read(500)
        parameters = ['volume', 'page', 'petitioner', 'respondent', 'argued', 'decided',
                      'case_number']
        case_number = re.search(r'No\.\s(?P<no>\d+\-\d+)', top)
        if case_number:
            self.metadict['case_number'] = case_number.group('no')
        argued = re.search(r'(?:Argued|Submitted)\s(?P<date>' + self.months +
                           r'\s\d{1,2},\s\d{4})', top)
        if argued:
            self.metadict['argued'] = argued.group('date')
        decided = re.search(r'Decided\s(?P<date>' + self.months +
                            r'\s\d{1,2},\s\d{4})', top)
        if decided:
            self.metadict['decided'] = decided.group('date')
        for parameter in parameters:
            if not parameter in self.metadict:
                self.metadict[parameter] = ''
                self.logger.warning('No value for ' + parameter +
                                    ' in dictionary.')
                
        with open(self.output, 'r', encoding='utf-8') as input:
            content = input.read()
        ind = content.find('<div class="indented-page">')
        new = content[:ind+27]
        rest = re.search(r'\n\n([^\n]{70,})', content)
        new += '\n\n' + self.case_caption.format(**self.metadict) + '\n'
        new += content[rest.start():]
        with open(self.output, 'w', encoding='utf-8') as output:
            output.write(new)
        
    def footnotes(self):
        '''Parse out footnotes into <ref></ref> tags. It does what it can, but it's highly
        dependent on the input file. All footnotes should be manually checked.'''
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
                        # Only allow the last footnote to be one line long. This will more likely
                        # than not clip the final footnote, but there's really no way for the
                        # parser to know where the last footnote ends and where the main text
                        # resumes.
                        if foot_no == max_footnote[str(sect)]:
                            foot_text += footnotes[ind]
                            ind += 1
                        else:
                            while ind < len(footnotes) and footnotes[ind] != ('Footnote ' +
                                                                              section +
                                                                              str(foot_no + 1)):
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
                    split.append(text[:x-1])
                    split.append(text[x:x+len(current_footnote)])
                    split.append(text[x+len(current_footnote):])
                    footnote_texts[i-1] = ' ' if footnote_texts[i-1] == '' else footnote_texts[i-1]
                    text = split[0] + split[1] + footnote_texts[i-1] + split[2]
              
                with open(self.output, 'w', encoding='utf-8') as output:
                    output.write(text + trailing)
                    
            with open(self.output, 'a', encoding='utf-8') as output:
                output.write('{{smallrefs}}\n')
                
    def headers(self):
        with open(self.output, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        split = re.split(r"(\{{2}\-start\-\}{2}\n(?:'''.*?'''\n|<div.*?\n))", content)
        sections = []
        new = []
        for i in range(len(split)):
            if i%2 == 1:
                match = re.search(r"'''(.*?)'''", split[i])
                if match:
                    name = match.group(1)
                    if '/' in name:
                        section = '/' + name.split('/')[1]
                        if 'Dissent' in section:
                            section = section + '|Dissent'
                        elif 'Concurrence' in section:
                            section = section + '|Concurrence'
                        else:
                            section = section + '|'
                        sections.append(section)
                    else:
                        sections.append('Syllabus')
        x=0
        for i in range(1, len(split)):
            if i%2 == 0:
                if x == 0:
                    header = self.header.format(section=sections[x], previous='', next='[[' + sections[x+1] + ']]', year=self.metadict['date'])
                elif x == 1:
                    header = self.header.format(section=sections[x], previous='[[/|Syllabus]]', next='[[' + sections[x+1] + ']]', year=self.metadict['date'])
                elif x == len(sections)-1:
                    header = self.header.format(section=sections[x], previous='[[' + sections[x-1] + ']]', next='', year=self.metadict['date'])
                else:
                    header = self.header.format(section=sections[x], previous= '[[' + sections[x-1] + ']]', next='[[' + sections[x+1] + ']]', year=self.metadict['date'])
                new.append(header + '\n')
                new.append(split[i])
                x+=1
            else:
                new.append(split[i])
        with open(self.output, 'w', encoding='utf-8') as output:
            output.write(''.join(new))
            
    def move_pages(self):
        '''Moves page numbers that occur right before a break.'''
        with open(self.output, 'r', encoding="utf-8") as inputfile:
            content = inputfile.read()
        new = re.sub(r"(?P<break>\{{2}page\sbreak\|\d+\|left\}{2}\n)(?P<rest>\{{2}\-stop\-\}{2}\n\{{2}\-start\-\}{2}\n'''(?:.*?)'''\n)", '\g<rest>\g<break>', content)
        with open(self.output, 'w', encoding="utf-8") as output:
            output.write(new)
                  
    def pages(self):
        '''Replace page numbers with {{page break}} template, join any hyphenated words.'''
        with open(self.output, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        split = re.split(r'(\n{2}PAGE\s\d+\n{2})', content)
        for i in range(len(split)):
            if split[i][:6] == '\n\nPAGE':
                number_m = re.match(r'\n{2}PAGE\s(?P<number>\d+)\n{2}', split[i])
                split[i] = ('\n\n{{page break|' + number_m.group('number') + 
                            '|left}}\n\n')
            elif split[i][-1] == '-':
                temp = split[i+2].split(' ', 1)
                split[i] = split[i][:-1] + temp[0]
                split[i+2] = temp[1]        
        content = '<div class="indented-page">\n' + ''.join(split) + '</div>'
        with open(self.output, 'w', encoding='utf-8') as output:
            output.write(content)

    def sectionize(self):
        '''Attempt to parse out any changes in section. Again, this is highly dependent on the input
        file and needs to be double-checked.'''
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
                                output.write('CONCURRENCE' + '-'*80 + justice + '\n\n')
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
                                output.write('DISSENT' + '-'*80 + justice + '\n\n')
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
                
        # Create useful warning messages to help the assistant
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
                
    def split_pages(self):
        '''Split pages for pywikipediabot.'''
        with open (self.output, 'r', encoding='utf-8') as file:
            content = file.read()
        split = re.split(r'((?:\n{0,2})[A-Z ]+[-]{80}(?:[A-Za-z]+)?(?:\n{0,2}))', content)
        for i in range (len(split)):
            divider = re.match(r'\n{0,2}(?P<section>[A-Za-z ]+)[-]{80}(?P<justice>[A-Za-z]+)?\n{0,2}', split[i])
            if divider:
                section_name = divider.group('section')
                if section_name == 'SYLLABUS':
                    split[i] = '\n\n'
                else:
                    if section_name == 'DISSENT' or section_name == 'CONCURRENCE':
                        justice = divider.group('justice')
                        if justice == None:
                            self.logger.warning("Missing justice name for " + section_name + ".")
                            justice = ''
                    else:
                        justice = ''
                    split[i] = ("\n{{-stop-}}\n{{-start-}}\n'''" + self.metadict['title'] + "/" +
                                section_name.title() + " " + justice + "'''\n")
        with open (self.output, 'w', encoding='utf-8') as output:
            output.write("{{-start-}}\n'''" + self.metadict['title'] + "'''\n" + ''.join(split) + "\n{{-stop-}}")