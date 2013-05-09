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
import ply.lex as lex

class Tokenizer(object):
#===================================================================================================
# TOKEN DECLARATIONS
#===================================================================================================
    tokens = (
              'FULL_TITLE',
              'SHORT_TITLE',
              'TERM',
              )
    
    def __init__(self, mdict):
        '''Initiate logging, open a file to store tokens, build the lexer.'''
        self.logger = logging.getLogger('brandeis')
        self.metadict = mdict
        
        # Reusable data
        self.months = r'(?:january|february|march|april|may|june|july|august|september|october|november|december)'
    
        
        # Define any regexes that rely on external data
        self.t_SHORT_TITLE.__func__.__doc__ = ('\n\n' +
                                               re.escape(self.metadict['title']) +
                                               '(?=\n\n)')
        self.t_TERM.__func__.__doc__ = ('\n\n' + self.months + '\sterm,\s(' +
                                        self.metadict['date'] + '|' +
                                        str(int(self.metadict['date'])-1) + '|'
                                        + str(int(self.metadict['date'])+1) +
                                        ')(?=\n\n)')
        
        # Create lexer
        self.lexer = lex.lex(module=self, reflags=re.IGNORECASE)

#===============================================================================
# TOKEN DEFINITIONS
#===============================================================================
    def t_FULL_TITLE(self, token):
        r'\s?=\s?(?P<title>.*?)\s?=\s?(?=\n)'
        token.value = token.lexer.lexmatch.group('title')
        return token
    
    def t_SHORT_TITLE(self, token):
        return token
    
    def t_TERM(self, token):
        return token
    
#===============================================================================
# ERROR HANDLING
#===============================================================================
    def t_ANY_error(self, token):
        token.lexer.skip(1)
#        self.logger.info("Illegal character {} at line {}, position {}."
#                         .format(token.value[0], token.lineno, token.lexpos))
        
    def analyze(self, data):
        '''Read through the text file and tokenize.'''
        self.lexer.input(data)
        self.token_list = list()
        with open('tokenout.txt', 'w+', encoding='utf-8') as tokenfile:
            while True:
                token = self.lexer.token()
                print(token)
                if not token:
                    break # No more input
                l_token = [token.type, token.value]
                self.token_list.append(l_token)
                tokenfile.write(str(token) + '\n')
        return self.token_list