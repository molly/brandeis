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

'''
These are the exceptions used by brandeis:

    ValidatorError
     +-- BadTitle
     +-- GroupedCase
    APIError
     +-- NoCaseInList
     +-- PageNotFound
     +-- MultipleCases
    TokenizerError
     +-- IllegalCharacter
    ParserError
     +-- EntityError
    BotError
     +-- MissingFootnote
'''

class ValidatorError(Exception):
    '''Base exception class for all file validation errors.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class APIError(Exception):
    '''Base exception class for any Wikisource API errors.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class TokenizerError(Exception):
    '''Base exception class for any tokenizer errors.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ParserError(Exception):
    '''Base exception class for any parser errors.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class BotError(Exception):
    '''Base exception class for any bot errors.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BadTitle(ValidatorError):
    '''The file contained an improperly formatted title, or was missing one entirely.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class GroupedCase(ValidatorError):
    '''The file consists of a group of cases.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class NoCaseInList(APIError):
    '''This case was not listed in the U.S. Reports
    (https://en.wikisource.org/wiki/United_States_Reports).'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class PageNotFound(APIError):
    '''The API call did not find an existing page.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class MultipleCases(APIError):
    '''The case was found multiple times in the list.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class IllegalCharacter(TokenizerError):
    '''The tokenizer encountered an illegal character.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class EntityError(ParserError):
    '''The parser encountered an unrecognized HTML entity.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MissingFootnote(BotError):
    '''A footnote is missing.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    