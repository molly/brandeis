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

import argparse, logging, os, sys
from exceptions import *
from validator import Validator
from caseparser import Parser, get_metadata
from api import API

# Set up logging
logger = logging.getLogger('brandeis')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# Command line parser
parser = argparse.ArgumentParser(description='Convert the text file of a supreme court case '
                                 'to wikitext.')
input_files = parser.add_mutually_exclusive_group(required=True)
input_files.add_argument('-f', '--files', nargs='*', help='List of files to be parsed.')
input_files.add_argument('-d', '--dir', nargs=1, help='Directory of files to be parsed.')
args = vars(parser.parse_args())

# Get list of files
if args["dir"]:
    # Directory name was supplied
    if os.path.isdir(args["dir"][0]):
        files = os.listdir(args["dir"][0])
        for i in range(len(files)):
            files[i] = args["dir"][0] + "/" + files[i]
    else:
        logger.error('There is no directory at {0}\{1}. Please check the path and retry.'
                     .format(os.path.dirname(os.path.abspath(__file__)), args["dir"][0]))
        sys.exit(0)
else:
    # List of files was supplied
    files = args["files"]
    for file in files:
        if not os.path.isfile(file):
            logger.error('There is no file named {0}\{1}. Please check the path and retry.'
                         .format(os.path.dirname(os.path.abspath(__file__)), file))
            sys.exit(0)

# Validate and parse each file
for file in files:
    metadict = dict()
    validator = Validator(file)
    parser = Parser()
    api = API()
    
    # Validate the file. Files that do not pass validation are skipped without interrupting the rest
    # of the process.
    try:
        validator.validate()
    except GroupedCase as e:
        logger.info(e.value + " File will be skipped.")
        continue
    except ValidatorError as e:
        logger.error(e.value + " File will be skipped.")
        continue
    
    # Get the title and other metadata
    get_metadata(metadict, file)
    
    # Skip if the file exists on Wikisource already
    try:
        line = api.get_case_line(metadict['title'], metadict['volume'], metadict['page'])
    except NoCaseInList as e:
        logger.info(e.value + " File will be skipped.")
        continue
    except MultipleCases as e:
        logger.error(e.value + " File will be skipped.")
        continue
    else:
        if api.case_exists(line):
            logger.info(metadict['title'] + " exists on Wikisource. File will be skipped.")
            continue
    
    # At this point, we have a valid text file for a case that does not exist on Wikisource
    print(metadict['title'])
    try:
        parser.parse()
    except Exception as e:
        logger.error(e.value)