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
from validator import Validator

# Set up logging
logger = logging.getLogger('brandeis')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
validator = Validator()
for file in files:
    validator.validate(file)
    

    