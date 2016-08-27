# -*- coding: utf-8 -*-
import urllib2
try: import simplejson as json
except ImportError: import json
import os
import sys

# load URL
try:
    loadConfig = open('url.json', 'r')
    configURL = json.load(loadConfig)
    loadConfig.close()
    url = configURL['url']
    name = configURL['name']
    version = configURL['version']
except:
    print 'ERR: Invalid url.json'
    sys.exit(1)

print '-------- DOWNLOADER --------'
print '- Fetch URL: ' + url + ' -'
print '- Fetch NAME: ' + name + ' -'
print '- Fetch VERSION: ' + ('latest' if version is None else version) + ' -'
print '----------------------------'