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
from bexceptions import EntityError

class Parser(object):
    '''The parser converts the raw case text from lochner to a dictionary object. This is later
    converted to wikitext to be uploaded.'''
    
    def __init__(self, metadict):
        self.logger = logging.getLogger('brandeis')
        self.output = None
        self.metadict = metadict

    def parse(self, tokens, output_file):
        '''Run the parser functions on the file.'''
        if output_file:
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
                except AttributeError as e:
                    self.logger.error("No command for " + command + ". " + repr(e));
                    break;
                except Exception as e:
                    self.logger.error("Exception while parsing: " + repr(e));
                    break;
                else:
                    self.write(self.value)
    
    def write(self, text):
        if type(text) is str:
            if self.output:
                self.output.write(text)
                
            
#===================================================================================================
# PARSING FUNCTIONS
#===================================================================================================
    def ignored_tag_content(self):
        '''Don't want these tags or their content in the output.'''
        self.value = ''
        return self.value
    
    def ignored_tag(self):
        ''''Don't want these tags in the output, but the content is preserved.'''
        self.value = ''
        return self.value
    
    def source(self):
        '''Keep in metadict, remove from output.'''
        self.metadict['source'] = self.value
        self.value = ''
        return self.value
    
    def blockquote(self):
        self.value = "\n:"
        return self.value
    
    def e_blockquote(self):
        self.value = '\n'
        return self.value
    
    def section(self):
        self.value = ''
        return self.value
    
    def b_paragraph(self):
        '''New paragraph within a blockquote; needs its own colon to continue the indentation.'''
        if self.value[0] == '':
            self.value = '\n\n:'
        else:
            self.value = ''
        return self.value
    
    def paragraph(self):
        '''Insert line break if end of paragraph. Ignore otherwise.'''
        #TODO: Handle other formatting
        if self.value[0] == '':
            self.value = '\n\n'
        else:
            self.value = ''
        return self.value
        
    def link(self):
        '''Extract necessary information from the link's HTML to determine if it should be kept'''
        info = self.value[0]
        text = self.value[1]
        m_class = re.search(r'class\="(?P<class>.*?)"', info)
        if m_class:
            link_class = m_class.group('class')
            if link_class == 'page-name':
                self.value = '\nPAGE ' + text + '\n'
                return self.value
            elif link_class == 'page-number':
                num_m = re.search(r'name\="(?P<name>\d+)"', info)
                self.value = '\nPAGE ' + num_m.group('name') + '\n'
                return self.value
            elif link_class == 'pdflink':
                # Hold on to PDF link in case we want it later.
                m_href = re.search(r'href\="(?P<href>.*?)"', info)
                href = m_href.group('href')
                self.metadict['pdf'] = href
        else:
            m_href = re.search(r'''href\=["'](?P<href>.*?)["']''', info)
            if m_href:
                href = m_href.group('href')
                if 'cases/federal/us' in href:
                    self.value = text
                    return self.value
                else:
                    # Footnotes
                    intext = re.match(r'^#F(?P<number>\d+?(\/\d+)?)$', href, re.MULTILINE)
                    if intext:
                        if 'Footnote' in text:
                            self.value = '<ref name="ref{0}"></ref>'.format(intext.group('number'))
                            return self.value
                        else:
                            self.value = text
                            return self.value
                    else:
                        footnote = re.match(r'^#T(?P<number1>\d+?)(?:\/(?P<number2>\d+))?$', href, re.MULTILINE)
                        if footnote:
                            if 'max_footnote' not in self.metadict:
                                self.metadict['max_footnote'] = dict()
                            if footnote.group('number2'):
                                self.metadict['max_footnote'][footnote.group('number1')] = footnote.group('number2')
                                self.value = 'Footnote {}'.format(footnote.group('number1') + '/' + footnote.group('number2'))
                            else:
                                self.metadict['max_footnote']['1'] = int(footnote.group('number1'))
                                self.value = 'Footnote {}'.format(footnote.group('number1'))
                            return self.value
        self.value = ''
        return self.value
        
    def comment(self):
        '''Don't want HTML comments in the output.'''
        self.value = ''
        return self.value
    
    def header(self):
        '''Larger text produced by <h#> tags'''
        level = self.value[0]
        content = self.value[1]
        if level == '6' or level == '5' or level == '4':
            self.value = "'''" + content + "'''"
        elif level == '3':
            self.value = '{{larger|' + content + '}}'
        elif level == '2':
            self.value = '{{x-larger|' + content + '}}'
        elif level == '1':
            self.value = '{{xx-larger|' + content + '}}'
        self.value = self.value + '\n\n'
        return self.value
    
    def html_entity(self):
        if self.value == "quot":
            self.value = '"'
        elif self.value == "sect":
            self.value = '§'
        elif self.value == "amp":
            self.value = '&'
        else:
            raise EntityError('Unknown entity: ' + self.value)
        return self.value
    
    def whitespace(self):
        self.value = ' '
        return self.value
    
    def supremelinks(self):
        '''List of sections. Shouldn't be added to text, not particularly useful to preserve.'''
        self.value = ''
        return self.value
    
    def consecutive(self):
        '''Strips consecutive italics (</i><i>) that occasionally appear'''
        self.value = ''
        return self.value
    
    def italics(self):
        '''Wraps text in double apostrophes.'''
        self.value = "''"
        return self.value
    
    def bold(self):
        '''Wraps text in triple apostrophes.'''
        self.value = "'''"
        return self.value
    
    def ordered(self):
        self.value = "\n\n{{right|''It is so ordered.''}}\n\n"
        return self.value
    
    def smallcaps(self):
        # Avoid making roman numerals into small caps
        roman = {'I', 'V', 'X', 'L', 'C', 'D', 'M', '.'}
        if len(self.value) <= 5:
            if set(self.value) <= roman:
                return self.value
        self.value = "{{sc|" + self.value.title() + "}}"
        return self.value
    
    def word(self):
        return self.value
    
    def b_newline(self):
        '''Newlines within blockquotes need a colon to continue the indentation.'''
        self.value = '\n:'
        return self.value
    
    def newline(self):
        '''Newlines should be preserved. Extraneous ones will be removed in post-processing.'''
        self.value = '\n'
        return self.value
    
    def number(self):
        return self.value
    
    def multi_apostrophes(self):
        '''If multiple apostrophes appear in the text (as they do, occasionally, due to bad OCR), 
        escape them with <nowiki></nowiki> to avoid borking the italics/bold'''
        self.value = "<nowiki>" + self.value + "</nowiki>"
        return self.value
        
    def asterisks(self):
        # For the three-asterisks-in-a-row thing that has no good name
        self.value = '{{***}}'
        return self.value
    
    def punctuation(self):
        if self.value == "'":
            # Replace apostrophes with ¤ for now to reduce conflicts with italics/bold
            self.value = "¤"
        elif self.value == "*":
            # Prevent bullet points
            self.value = "<nowiki>*</nowiki>"
        return self.value
    
def strip_extraneous(content):
    '''Much of the HTML in the page is not useful -- this removes most everything but the case
    itself. Also removes newlines and tab characters.'''
    match = re.search(r'<article\sid\="maincontent">(?P<content>.*?)<\/article>.*?<\/html>(?P<source>.*)',
                      content, flags = re.DOTALL)
    if (match):
        return (match.group('content') + match.group('source')).replace('\n', '').replace('\t', '')
    else:
        return None
    
def get_metadata(metadict, filename):
    '''Pull the title and other information from the file.'''
    with open(filename, 'r', encoding='utf-8') as file:
        while True:
            first_line = file.readline()
            match = re.match(r'^[\n\s\t\r]+$', first_line, re.MULTILINE)
            if not match:
                break
    title = re.match(r'[\s\t]*<h1>(?P<full>(?P<title>(?P<petitioner>.*?)\sv\.\s(?P<respondent>.*?))\s\-\s(?P<number>(?P<volume>\d{1,3})\s(?P<abbr>U.S.)\s(?P<page>\d{1,3}))\s\((?P<date>\d{4})\))</h1>', first_line)
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