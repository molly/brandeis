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
from exceptions import APIError, NoCaseInList, PageNotFound
import json, re

class API(object):
    '''Makes any calls to the Wikisource API to retrieve necessary information.'''    
    def __init__(self):
        self.base_URL = 'http://en.wikisource.org/w/api.php?format=json&action='
        self.base_volume = 'United States Reports/Volume ' 
        
    def case_exists(self, line):
        title_match = re.search(r'\[{2}(?!:?Category)(?P<link>.*?)\]{2}', line)
        if title_match:
            title = title_match.group("link")
        URL = self.base_URL + 'parse&text={0}&prop=links'.format(parse.quote(line))
        response = self.request(URL)
        for link in response["parse"]["links"]:
            if link['*'] == title:
                return "exists" in link
        
    def get_case_line(self, title, vol, page):
        volume = parse.quote(self.base_volume + vol);
        URL = self.base_URL + 'query&titles={0}&prop=revisions&rvprop=content'.format(volume)
        response = self.request(URL)
        rev_id = list(response["query"]["pages"].keys())[0]
        if rev_id == "-1":
            raise PageNotFound("There is no Wikisource page at {}.".format(volume))
        content = response["query"]["pages"][rev_id]["revisions"][0]["*"]
        regex = re.compile("^\* \[(?:.*?) {0} U\.S\. {1}\] (.*?)$".format(vol, page), re.MULTILINE)
        match = regex.search(content)
        if match:
            return match.group(0)
        else:
            rstring = "^(.*?)" + re.escape(title) + "(.*?)$"
            regex = re.compile(rstring, re.MULTILINE)
            match = regex.search(content)
            if match:
                return match.group(0)
            else:
                raise NoCaseInList("Unable to find case {0} ({1} U.S. {2}) in the list of cases"
                                   " retrieved from API query: {3}.".format(title, vol, page,
                                                                            URL))
    
    def request(self, url):
        try:
            response = json.loads(request.urlopen(url).read().decode('utf-8'))
        except error.HTTPError:
            exit("Exited: HTTPError when making API requests.")
        else:
            return response