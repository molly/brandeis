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

import logging, re, sys
import ply.lex as lex
from bexceptions import IllegalCharacter

class Tokenizer(object):
#===================================================================================================
# TOKEN DECLARATIONS
#===================================================================================================
    tokens = (
              'IGNORED_TAG_CONTENT',# For tags where we want to ignore the tags AND the content
              'IGNORED_TAG',        # Various tags we don't need to keep (content is preserved)
              'SOURCE',             # Source link and text added by lochner
              'BLOCKQUOTE',         # <blockquote>
              'E_BLOCKQUOTE',       # </blockquote>
              'SECTION',            # Repeated section name
              'B_PARAGRAPH',        # <p> in blockquote state
              'PARAGRAPH',          # <p>, </p>
              'LINK',               # <a> tags
              'COMMENT',            # <!-- comment -->
              'HEADER',             # <h1>, <h2>, etc.
              'HTML_ENTITY',        # &thing;
              'WHITESPACE',         # Tabs, spaces
              'SUPREMELINKS',       # <ul class="supremelinks">
              'CONSECUTIVE',        # <i></i>
              'ITALICS',            # <i>
              'BOLD',               # <b>
              'B_NEWLINE',          # Newline in blockquote state
              'NEWLINE',            # Newline
              'SMALLCAPS',          # ALL CAPS WORDS
              'ORDERED',            # "It is so ordered."
              'WORD',
              'NUMBER',
              'MULTI_APOSTROPHES',  # For '', ''' in the text
              'ASTERISKS',          # ***
              'PUNCTUATION',
              )

#===================================================================================================
# STATES
#===================================================================================================
    states = (
              ('blockquote', 'inclusive'),
             )
    
    def __init__(self, mdict):
        '''Initiate logging, open a file to store tokens, build the lexer.'''
        self.logger = logging.getLogger('brandeis')
        self.metadict = mdict
        self.lexer = lex.lex(module=self)
        
#===============================================================================
# TOKEN DEFINITIONS
#===============================================================================
    def t_IGNORED_TAG_CONTENT(self, token):
        r'<(script|SCRIPT|div\sclass\="disclaimer")(.*?)>.*?<\/(div|script|SCRIPT)>'
        return token
        
    def t_IGNORED_TAG(self, token):
        r'<\/?(?P<tag>div|DIV|span|SPAN|hr|HR)(.*?)>'
        token.value = token.lexer.lexmatch.group('tag')
        return token
    
    def t_CONSECUTIVE(self, token):
        r'<\/i><i>'
        return token
    
    def t_SOURCE(self, token):
        r'Source\:\s(?P<source>http.*?\.html).*'
        token.value = token.lexer.lexmatch.group('source')
        return token
    
    def t_BLOCKQUOTE(self, token):
        r'<blockquote>'
        token.lexer.begin('blockquote') # Begin blockquote state
        return token
    
    def t_blockquote_E_BLOCKQUOTE(self, token):
        r'<\/blockquote>'
        token.lexer.begin('INITIAL') # End blockquote state
        return token
    
    def t_SECTION(self, token):
        r'(?<=<\/A><\/p><p>)(?P<name>Per\sCuriam)(?=<\/p>)'
        token.value = token.lexer.lexmatch.group('name')
        return token
    
    def t_ORDERED(self, token):
        r'<p>It\sis\sso\sordered\.<\/p>'
        return token
    
    def t_blockquote_B_PARAGRAPH(self, token):
        r'<(?P<end>\/?)[Pp](?P<info>.*?)>'
        token.value = token.lexer.lexmatch.group('end', 'info')
        return token
    
    def t_PARAGRAPH(self, token):
        r'<(?P<end>\/?)[Pp](?P<info>.*?)>'
        token.value = token.lexer.lexmatch.group('end', 'info')
        return token        
    
    def t_LINK(self, token):
        r'\[?<[aA]\s(?P<info>.*?)>(?P<text>.*?)<\/[aA]>\]?'
        token.value = token.lexer.lexmatch.group('info', 'text')
        return token
        
    def t_COMMENT(self, token):
        r'<!--(.*?)-->'
        return token
    
    def t_HEADER(self, token):
        r'<[Hh](?P<level>[1-6])>(?P<content>.*?)<\/[Hh][1-6]>'
        token.value = token.lexer.lexmatch.group('level', 'content')
        return token
    
    def t_HTML_ENTITY(self, token):
        r'&(?P<entity>[#a-z0-9]{6});'
        token.value = token.lexer.lexmatch.group('entity')
        return token
    
    def t_SUPREMELINKS(self, token):
        r'<(ul|UL)\s(class|CLASS)\="supremelinks">(?P<content>.*?)<\/(ul|UL)>'
        token.value = token.lexer.lexmatch.group('content')
        return token
    
    def t_ITALICS(self, token):
        r'(<\/?([Ii]|em|EM)>)+'
        return token
    
    def t_BOLD(self, token):
        r'<\/?(B|b|strong|STRONG)>'
        return token
    
    def t_blockquote_B_NEWLINE(self, token):
        r'(<[Bb][Rr]\s?\/?>)'
        return token
    
    def t_NEWLINE(self, token):
        r'(<[Bb][Rr]\s?\/?>)'
        return token
    
    def t_SMALLCAPS(self, token):
        r'((?:[A-Z]{2,}\.?\s?)+|[A-Z]+,\s[A-Z]\.)+(?=[\W])'
        return token
    
    def t_WHITESPACE(self, token):
        r'\s'
        return token
    
    def t_WORD(self, token):
        r'[a-zA-z]+'
        return token
    
    def t_NUMBER(self, token):
        r'[0-9]+'
        return token
    
    def t_MULTI_APOSTROPHES(self, token):
        r"'{2,3}"
        return token
    
    def t_ASTERISKS(self, token):
        r'\*{3}'
        return token
    
    def t_PUNCTUATION(self, token):
        r"""[!@\#\$\%\^&\*\(\)\-;\+=\[\]\{\}\\\|\:;"',\.\?~°–—/]"""
        return token
    
#===============================================================================
# ERROR HANDLING
#===============================================================================
    def t_ANY_error(self, token):
        token.lexer.skip(1)
        raise IllegalCharacter(token.lexpos)
        
    def analyze(self, data):
        '''Read through the text file and tokenize.'''
        self.lexer.input(data)
        self.token_list = list()
        with open('tokenout.txt', 'w+', encoding='utf-8') as tokenfile:
            while True:
                token = self.lexer.token()
                #print(token)
                if not token:
                    break # No more input
                l_token = [token.type, token.value]
                self.token_list.append(l_token)
                tokenfile.write(str(token) + '\n')
        return self.token_list