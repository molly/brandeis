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

from urllib import error, parse, request
from sys import exit
from exceptions import NoCaseInList, PageNotFound, MultipleCases
import json, re, os

class API(object):
    '''Makes any calls to the Wikisource API to retrieve necessary information.'''    
    
    def __init__(self):
        self.base_URL = 'http://en.wikisource.org/w/api.php?format=json&action='
        self.base_volume = 'United States Reports/Volume ' 
        self.cache = Cache()
        
    def case_exists(self, line):
        '''Use the Wikisource API to parse the case line and determine if the case already exists
        on Wikisource.'''
        
        # Avoid determining if category exists; this will return a false positive.
        title_match = re.search(r'\[{2}(?!:?Category)(?P<link>.*?)\]{2}', line)
        if title_match:
            title = title_match.group("link")
            
        URL = self.base_URL + 'parse&text={0}&prop=links'.format(parse.quote(line))
        response = self.request(URL)
        for link in response["parse"]["links"]:
            if link['*'] == title:
                return "exists" in link
        
    def get_case_line(self, title, vol, page):
        '''Find the case in the appropriate U.S. Reports list. Follows the following logic:
            - If it finds a line matching "[volume] U.S. [page]" in list (e.g. "1 U.S. 100")
                - Return line if only one is found
                - filter_multiple() if multiple matches are found
            - Else search for the a line matching the exact case name in the list
                - Return line if only one is found
                - Raise MultipleCases if multiple matches are found
           If neither of these returns a result, raise NoCaseInList
        '''
        
        # Get the appropriate United States Reports/Volume page
        volume = parse.quote(self.base_volume + vol);
        URL = self.base_URL + 'query&titles={0}&prop=revisions&rvprop=content'.format(volume)
        content = self.cache.get_cached_volume(vol)
        if not content:
            response = self.request(URL)
            rev_id = list(response["query"]["pages"].keys())[0]
            if rev_id == "-1":
                raise PageNotFound("There is no Wikisource page at {}.".format(volume))
            content = response["query"]["pages"][rev_id]["revisions"][0]["*"]
            self.cache.add_to_volume_cache(vol, content)
        
        # Search this page for "[volume] U.S. [page]"
        rstring = "^.*?\D{0}\sU\.S\.\s{1}\D.*?$".format(vol, page)
        regex = re.compile(rstring, re.MULTILINE)
        match = regex.findall(content)
        if match:
            if len(match) == 1:
                return match[0]
            else:
                result = self.filter_multiple(title, match)
                if result:
                    return result
                else:
                    raise MultipleCases("Unable to resolve multiple matches for {0} ({1} U.S."
                                        " {2}) in API query: {3}".format(title, vol, page, URL))
        # Search this page for the exact title (case-insensitive)
        else:
            regex = re.compile(re.escape(title), re.MULTILINE | re.IGNORECASE)
            match = regex.findall(content)
            if match:
                if len(match) == 1:
                    return match[0]
                else:
                    # VERY unlikely to happen, but no harm in adding it
                    raise MultipleCases("Unable to resolve multiple NAME matches for {0} ({1} U.S."
                                            " {2}) in API query: {2}".format(title, vol, page, URL))
            # Neither method worked; time to give up.
            else:
                raise NoCaseInList("Unable to find case {0} ({1} U.S. {2}) in the list of cases"
                                   " retrieved from API query: {3}.".format(title, vol, page, URL))
                
    def filter_multiple(self, title, match_list):
        '''Fuzzy-matches the case name in a list of possible matches. Occasionally the volume page
        will have multiple cases with the same volume and page numbers; this will try to match by
        title. Titles may not be exact, so this requires one word in the petitioner and one in the
        respondent matches. Common words ("the", "et", "al", etc.) will not be matched.
        
        This does NOT correct for spelling mistakes. This does NOT try to differentiate between two
        cases that have matching words in the petitioner and title (for example, it will not return
        a result for "Respublica v. Sweers" when the match list includes "Respublica v. Sweers" and
        "Respublica v. Cornelius Sweers".'''
        try:
            petitioner, respondent = title.split('v.')
            petitioner = set([item.strip().lower() for item in petitioner.split()])
            respondent = set([item.strip().lower() for item in respondent.split()])
            common_words = {"the", "et", "al", "et.", "al.", "of", "a", "for", "and", "inc.", "no.",
                            "&", "co.", "ltd.", "l.l.c."}
            petitioner = list(petitioner.difference(common_words))
            respondent = list(respondent.difference(common_words))
        except:
            return None
        else:
            actual_matches = []
            for item in match_list:
                if any(word in item.lower() for word in petitioner) and any(word in item.lower()
                                                                            for word in respondent):
                    actual_matches.append(item)
            if len(actual_matches) == 1:
                return actual_matches[0]
            else:
                return None
    
    def request(self, url):
        '''Generic API request function. Requires that the response format be JSON.'''
        try:
            response = json.loads(request.urlopen(url).read().decode('utf-8'))
        except error.HTTPError:
            exit("Exited: HTTPError when making API requests.")
        else:
            return response
        
class Cache(object):
    
    def __init__(self):
        try:
            os.mkdir('cache')
        except FileExistsError:
            pass

    def get_cached_volume(self, volume):
        try:
            with open('cache/' + volume, 'r', encoding='utf-8') as cache_file:
                content = cache_file.read()
                return content
        except FileNotFoundError:
            return None            
    
    def add_to_volume_cache(self, volume, content):
        with open('cache/' + volume, 'w', encoding='utf-8') as cache_file:
            cache_file.write(content)
        return True