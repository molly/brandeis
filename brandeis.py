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

import argparse, logging, os, re, sys
from time import strftime, gmtime
from bexceptions import *
from validator import Validator
from caseparser import Parser, get_metadata, strip_extraneous
from api import API
from tokenizer import Tokenizer
from postprocessor import Postprocessor
from bot.core import Bot

# Set up logging
try:
    os.mkdir('logs')
except OSError:
    pass
logger = logging.getLogger('brandeis')
summary_logger = logging.getLogger('summary')
logger.setLevel(logging.DEBUG)
summary_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
console = logging.StreamHandler()
report = logging.FileHandler("logs/report" + strftime("%H%M%S_%d%m%Y", gmtime()), encoding='utf-8')
summary = logging.FileHandler("logs/summary" + strftime("%H%M%S_%d%m%Y", gmtime()), encoding='utf-8')
console.setFormatter(formatter)
report.setFormatter(formatter)
summary.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(report)
summary_logger.addHandler(summary)
summary_logger.info('==Bot run: ' + strftime("%d-%m-%Y, %H:%M:%S (UTC)", gmtime()) + '==')

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
    api = API()
    
    # Remove extra HTML
    with open(file, 'r', encoding='utf-8') as html:
        raw = html.read()
        content = strip_extraneous(raw)
        
    if content:
         with open(file, 'w', encoding='utf-8') as html:
             html.write(content)
    
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
        choice = input(e.value + ' Continue? (y/n)')
        if choice == 'n' or choice == "N":
            logger.info(e.value + " Skipping.")
            continue
        else:
            logger.info(e.value + " Continuing.")
    except MultipleCases as e:
        choice = input(e.value + ' Continue? (y/n)')
        if choice == 'n' or choice == "N":
            logger.info(e.value + " Skipping.")
            continue
        else:
            logger.info(e.value + " Continuing.")
    else:
        if api.case_exists(line):
            choice = input('This file exists on Wikisource. Continue? (y/n)')
            if choice == 'n' or choice == "N":
                logger.info(metadict['title'] + " exists on Wikisource. Skipping.")
                continue
            else:
                logger.info(metadict['title'] + " exists on Wikisource. Continuing.")
    
    # At this point, we have a valid text file for a case that does not exist on Wikisource
    logger.info("Parsing {0}.".format(metadict['title']))
    tokenizer = Tokenizer(metadict)
    parser = Parser(metadict)
    try:
        os.mkdir('wikitext')
    except OSError:
        pass
    out_filename = 'wikitext/' + re.sub(r'[^a-zA-Z0-9_]', '', metadict['title'])
    postprocessor = Postprocessor(out_filename)
    
    with open(file, 'r', encoding='utf-8') as input_file:
        raw_text = input_file.read()
        try:
            token_stream = tokenizer.analyze(raw_text)
        except IllegalCharacter as e:
            logger.error("Illegal character encountered: \"{0}\" at {1}. More: {2}"
                              .format(raw_text[e.value], e.value,
                                     (raw_text[e.value:e.value+20] + "...").replace('\n', '\\n')))
            sys.exit()
    with open(out_filename, 'w', encoding='utf-8') as output_file:
        parser.parse(token_stream, output_file)
    postprocessor.process()
     
    # Begin the bot parsing
    try:
        os.mkdir('botfiles')
    except OSError:
        pass
    try:
        os.mkdir('botfiles/pdfs')
    except OSError:
        pass
    bot_filename = out_filename.replace('wikitext', 'botfiles')
    bot = Bot(out_filename, bot_filename, metadict)
    bot.prepare()
    logger.info('-----')
    summary_logger.info('\n\n')
         