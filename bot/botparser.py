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
        self.inputfile = inputfile
        self.metadict = metadict
        self.logger = logging.getLogger('brandeis')
        self.summary_logger = logging.getLogger('summary')
        self.case_caption = ('{{{{CaseCaption \n| court = United States Supreme Court\n| volume = '
                             '{volume}\n| reporter = U.S.\n| page = {page}\n| party1 = {petitioner}'
                             '\n| party2 = {respondent}\n| lowercourt = \n| argued = {argued} \n| '
                             'decided = {decided}\n| case no = {case_number}\n}}}}')
        self.header = ('{{{{header\n | title = {{{{subst:PAGENAME}}}}\n | author = \n | translator '
                       '= \n | section = {{{{subst:SUBPAGENAME}}}}\n | previous = {previous}\n | next = {next}\n'
                       ' | year = {year}\n | notes = \n | categories = \n | portal = Supreme Court of '
                       'the United States\n}}}}\n')
        self.months = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        self.pagelist = ['']
        
    def prepare(self):
        '''Perform the parsing functions. Note the order of some of these functions is important.'''
        self.sectionize()
        self.footnotes()
        self.pages()
        self.move_pages()
        self.add_case_caption()
        try:
            self.headers()
        except IndexError:
            self.logger.warning("Unable to add any headers.")
        self.ussc_case()
        self.clean_spaces()
        self.talk_pages()
        self.redirect()
        with open(self.output, 'w', encoding="utf-8") as output:
            output.write('\n'.join(self.pagelist))
        
    def add_case_caption(self):
        '''Add {{CaseCaption}} to the syllabus page.'''
        top = self.pagelist[0][:500] if len(self.pagelist[0]) >= 500 else self.pagelist[0]
        parameters = ['volume', 'page', 'petitioner', 'respondent', 'argued', 'decided',
                      'case_number']
        case_number = re.search(r'No\.\s?(?P<no>\d+\-\d+)', top)
        if case_number:
            self.metadict['case_number'] = case_number.group('no')
        argued = re.search(r'(?:Argued|Submitted)\s(?P<date>' + self.months +
                           r'\s\d{1,2}(?:-\d{1,2})?,\s\d{4})', top)
        if argued:
            self.metadict['argued'] = argued.group('date')
        decided = re.search(r'Decided\s(?P<date>' + self.months +
                            r'\s\d{1,2}(?:-\d{1,2})?,\s\d{4})', top)
        if decided:
            self.metadict['decided'] = decided.group('date')
        for parameter in parameters:
            if not parameter in self.metadict:
                self.metadict[parameter] = ''
                self.logger.warning('No value for ' + parameter +
                                    ' in dictionary.')
                
        ind = self.pagelist[0].find('{{-start-}}')
        new = self.pagelist[0][:ind+11] + "\n'''" + self.metadict['title'] + "'''\n"
        rest = re.search(r'\n\n([^\n]{100,})', self.pagelist[0])
        new += '\n' + self.case_caption.format(**self.metadict)
        new += self.pagelist[0][rest.start():]
        self.pagelist[0] = new
        
    def clean_spaces(self):
        '''Clean any excessive newlines or spaces that may have been introduced. Groups of newlines
        with more than two in a row are replaced by two newlines. Groups of two or more spaces are
        replaced with one.'''
        for i in range(len(self.pagelist)):
            self.pagelist[i] = re.sub(r'[ ]{2,}', ' ', self.pagelist[i])
            self.pagelist[i] = re.sub(r'\n{3,}', '\n\n', self.pagelist[i])
        
    def footnotes(self):
        '''Parse out footnotes into <ref></ref> tags. It does what it can, but it's highly
        dependent on the input file. All footnotes should be manually checked.'''
        if 'max_footnote' in self.metadict:
            max_footnote = self.metadict['max_footnote']
            self.logger.warning("Added footnotes to the text. ({0} sections: {1})."
                                .format(len(max_footnote), str(max_footnote)))
            sect = 1
            for sect in range(1,len(max_footnote)+1):
                for i in range(len(self.pagelist)):
                    section = '' if sect == 1 else str(sect) + '/'
                    footnote_start = self.pagelist[i].find('Footnote ' + section + '1')
                    if footnote_start != -1:
                        content = [self.pagelist[i][:footnote_start], self.pagelist[i][footnote_start:]]
                        self.pagelist[i] = content[0]
                        end_ind = content[1].find('{{smallrefs}}')
                        if end_ind != -1:
                            footnotes = content[1][:end_ind]
                            self.pagelist[i] += content[1][end_ind:]
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
                          
                        end_footnote = '</ref>'
                        for j in range(1,int(max_footnote[str(sect)])+1):
                            split = []
                            current_footnote = '<ref name="ref{}">'.format(section + str(j))
                            x = -1
                            page_num = 0
                            while x == -1 and page_num < len(self.pagelist):
                                x = self.pagelist[page_num].find(current_footnote)
                                if x != -1:
                                    break
                                page_num += 1
                            if x == -1:
                                self.logger.warning("Unable to find an in-text tag for footnote #" +
                                                    section + str(j) + ". It has been omitted.")
                                continue
                            else:
                                split.append(self.pagelist[page_num][:x-1])
                                split.append(self.pagelist[page_num][x:x+len(current_footnote)])
                                split.append(self.pagelist[page_num][x+len(current_footnote):])
                                footnote_texts[j-1] = ' ' if footnote_texts[j-1] == '' else footnote_texts[j-1]
                                self.pagelist[page_num] = split[0] + split[1] + footnote_texts[j-1] + split[2]
                
    def headers(self):
        '''Add the {{header}} template to the beginning of each page.'''
        content = ''.join(self.pagelist)
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
        for page_num in range(len(self.pagelist)):
            if page_num == 0:
                header = self.header.format(section=sections[page_num], previous='', next='[[' +
                                            sections[page_num+1] + ']]', year=self.metadict['date'])
            elif page_num == 1:
                header = self.header.format(section=sections[page_num], previous='[[{{subst:BASEPAGENAME}}|Syllabus]]',
                                            next='[[' + sections[page_num+1] + ']]',
                                            year=self.metadict['date'])
            elif page_num == len(sections)-1:
                header = self.header.format(section=sections[page_num], previous='[[' +
                                            sections[page_num-1] + ']]', next='',
                                            year=self.metadict['date'])
            else:
                header = self.header.format(section=sections[page_num], previous= '[[' +
                                            sections[page_num-1] + ']]', next='[[' +
                                            sections[page_num+1] + ']]', year=self.metadict['date'])
            page_split = re.split(r"(\{{2}-start-\}{2}\n*(?:'''.*?''')?\n?)",
                                  self.pagelist[page_num], re.DOTALL)
            try:
                ind = page_split[2].find('\n{{-stop-}}')
                page_split[2] = page_split[2][:ind] + '\n</div>\n{{PD-USGov}}' + page_split[2][ind:]
                self.pagelist[page_num] = page_split[0] + page_split[1] + '<div class="indented-page">\n' + header + page_split[2]
            except IndexError:
                self.logger.warning("Unable to add a header for page " + str(page_num) + ".")
            
            
    def move_pages(self):
        '''Moves page numbers that occur right before a break.'''
        for i in range(len(self.pagelist)):
            match = re.search(r'(?P<page>\{{2}page\sbreak\|\d+\|left\}{2})(\s|\n)*\{{2}smallrefs',
                              self.pagelist[i])
            if match:
                self.pagelist[i] = self.pagelist[i].replace(match.group('page'), '')
                split = re.split(r"(\{{2}\-start\-\}{2}\n+'{3}.*?'{3}\n)",self.pagelist[i+1])
                self.pagelist[i+1] = (split[0] + split[1] + '\n' + match.group('page') + '\n' +
                                      split[2])
                  
    def pages(self):
        '''Replace page numbers with {{page break}} template, join any hyphenated words.'''
        for page_num in range(len(self.pagelist)):
            split = re.split(r'(\n{2}PAGE\s\d+\n{2})', self.pagelist[page_num])
            for i in range(len(split)):
                if split[i][:6] == '\n\nPAGE':
                    number_m = re.match(r'\n{2}PAGE\s(?P<number>\d+)\n{2}', split[i])
                    split[i] = ('\n\n{{page break|' + number_m.group('number') + 
                                '|left}}\n\n')
                elif split[i][-1] == '-':
                    temp = split[i+2].split(' ', 1)
                    split[i] = split[i][:-1] + temp[0]
                    split[i+2] = temp[1]
            content = ''.join(split)
            self.pagelist[page_num] = content
            
    def redirect(self):
        '''Create redirect page for the case number'''
        page = "{{-start-}}\n'''" + self.metadict['number'] + "'''\n#REDIRECT [[" + self.metadict['title'] + "]]\n{{-stop-}}"
        self.pagelist.append(page)
        self.summary_logger.info("Creating redirect from [[" + self.metadict['number'] + "]] to [[" + self.metadict['title'] + "]].")
        
    def sectionize(self):
        '''Attempt to parse out any changes in section. Again, this is highly dependent on the input
        file and needs to be double-checked.'''
        self.metadict['sections'] = dict()
        self.metadict['sections']['concurrence_justices'] = []
        self.metadict['sections']['dissent_justices'] = []
        self.metadict['sections']['concurrence'] = []
        self.metadict['sections']['dissent'] = []
        with open(self.inputfile, 'r', encoding='utf-8') as inputfile:
            content = inputfile.read()
        paras = content.split('\n\n')
        for i in range(len(paras)):
            ind = 0 if len(self.pagelist) == 1 and self.pagelist[0] == '' else -1
            if len(paras[i]) < 400:
                if 'syllabus' in paras[i].lower():
                    if 'syllabus' not in self.metadict['sections']:
                        self.metadict['sections']['syllabus'] = i
                elif re.search(r',\sconcurring(\.|\Z)', paras[i], re.IGNORECASE):
                    sentence_m = re.search(r'(\.|\A)(?P<justices>.*?),\sconcurring(\.|\Z)',
                                           paras[i], re.IGNORECASE)
                    if sentence_m:
                        sentence = sentence_m.group('justices')
                        justices = re.search(r'\{{2}sc\|(?:(?:Mr\.\s)?(?:Chief\s)?Justice\s)?(?P<justice>.*?)\}{2}', sentence)
                        justice = justices.group('justice')
                        if not justice in self.metadict['sections']['concurrence_justices']:
                            self.pagelist[ind] += "\n{{smallrefs}}\n{{-stop-}}"
                            self.pagelist.append("\n{{-start-}}\n'''" + self.metadict['title'] +
                                                 "/Concurrence " + justice + "'''\n")
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
                            self.pagelist[ind] += "\n{{smallrefs}}\n{{-stop-}}"
                            self.pagelist.append("{{-start-}}\n'''" + self.metadict['title'] +
                                                 "/Dissent " + justice + "'''\n")
                            self.metadict['sections']['dissent_justices'].append(justice)
                            self.metadict['sections']['dissent'].append(i)
                elif 'per curiam' in paras[i].lower():
                    if 'per curiam' not in self.metadict['sections']:
                        self.pagelist[ind] += "\n{{smallrefs}}\n{{-stop-}}"
                        self.pagelist.append("{{-start-}}\n'''" + self.metadict['title'] +
                                             "/Opinion of the Court'''\n")
                        self.metadict['sections']['per curiam'] = i
                elif 'delivered the opinion' in paras[i].lower():
                    if 'opinion' not in self.metadict['sections']:
                        self.pagelist[ind] += "\n{{smallrefs}}\n{{-stop-}}"
                        self.pagelist.append("{{-start-}}\n'''" + self.metadict['title'] +
                                             "/Opinion of the Court'''\n")
                        self.metadict['sections']['opinion'] = i
                self.pagelist[ind] += (paras[i] + '\n\n')
            else:
                self.pagelist[ind] += (paras[i] + '\n\n')
        self.pagelist[0] = '{{-start-}}\n'+ self.pagelist[0]
        self.pagelist[-1] += '\n{{smallrefs}}\n{{-stop-}}'
        
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
                
    def talk_pages(self):
        temp = self.pagelist
        self.pagelist = []
        for i in range(len(temp)):
            self.pagelist.append(temp[i])
            title_match = re.search(r"\{{2}-start-\}{2}\n+'''(?P<title>.*?)'''", temp[i])
            if not title_match:
                self.logger.warning('Unable to add a talk page.')
                continue
            self.summary_logger.info("Adding page [[" + title_match.group('title') + "]]")
            self.summary_logger.info("Adding page [[Talk:" + title_match.group('title') + "]]")
            talkpage = "{{-start-}}\n'''Talk:" + title_match.group('title') + "'''\n{{textinfo\n"
            talkpage += "|edition = " + self.metadict['full_title'] + '\n'
            talkpage += ("|source = " + self.metadict['title'] + ' from [' + self.metadict['source']
                         + ' Justia]\n')
            talkpage += "|contributors = [[User:BrandeisBot]]\n"
            talkpage += "|progress = Text being edited [[Image:25%.png]]\n"
            talkpage += ("|notes = Text gathered and wikified using the an automated tool. See " +
                         "[[User:BrandeisBot/Documentation]] for more information.\n")
            talkpage += "|proofreaders = \n}}\n{{-stop-}}"
            self.pagelist.append(talkpage)
                
    def ussc_case(self):
        for page in range(len(self.pagelist)-4):
            if page == 0:
                template = '\n{{USSCcase\n|percuriam = '
            else:
                template = '\n{{USSCcase2\n|percuriam = '
            if 'per curiam' in self.metadict['sections']:
                template += 'yes\n'
            else:
                template += 'no\n'
            try:
                for i in range(len(self.metadict['sections']['concurrence_justices'])):
                    template += ('|concurrence_author' + str(i+1) + ' = ' + 
                                 self.metadict['sections']['concurrence_justices'][i]) + '\n'
                if i > 8:
                    self.logger.warning("Too many concurrence authors in {{USSCcase}}.")
            except KeyError:
                pass
            try:
                for i in range(len(self.metadict['sections']['dissent_justices'])):
                    template += ('|dissent_author' + str(i+1) + ' = ' + 
                                 self.metadict['sections']['dissent_justices'][i]) + '\n'
                if i > 4:
                    self.logger.warning("Too many dissent authors in {{USSCcase}}.")
            except KeyError:
                pass
            template += "|linked_cases =\n|wikipedia = no\n}}\n"
            if page == 0:
                s = re.split(r'(\{{2}CaseCaption(?:.|\n)*?\}{2})', self.pagelist[page])
            else:
                s = re.split(r'(\{{2}header(?:.|\n)*?[^A-Z]\}{2})', self.pagelist[page])
            self.pagelist[page] = s[0] + s[1] + template + s[2]