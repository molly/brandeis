Brandeis is a Python3 script that converts U.S. Supreme Court cases to wikitext, which can then be uploaded using a [pywikipediabot](http://www.mediawiki.org/wiki/Manual:Pywikipediabot/). It is intended to complement with [lochner](http://gitorious.org/lochner), a scraper that pulls court cases from [Justia](http://supreme.justia.com/). 


# Using brandeis
Before you can use brandeis, you must install lochner and use it to retrieve the case files you want to convert. Brandeis uses lochner's HTML output, *not* the plaintext. Make sure you set the `--format=html` flag when you run lochner. Once you have done this, you can run brandeis on these files.

Run brandeis from its directory using the following syntax:

`python3 brandeis.py (-f FILES | -d DIR)`

###Options
`-h, --help`
Show basic help.

`-f [FILES [FILES ...]], --files [FILES [FILES...]]`
Specify a file or list of files to parse. 

`-d DIR, --dir DIR`
Specify a directory of files to parse.

###Output
Brandeis outputs a number of files. In the "botfiles" directory, you will find one file for each case. This will be a text file formatted for upload by pywikipediabot's [pagefromfile.py](http://www.mediawiki.org/wiki/Manual:Pywikipediabot/pagefromfile.py) script. Brandeis also outputs two log files. The first is named "report", followed by the time the script was run. The contents of this file duplicates the console output — it is a list of warnings for possible problems that should be double-checked before the file is uploaded. The second log file is named "summary", followed by the time of run. This is a summary of the files that will be created on Wikisource when pywikipedia is run.