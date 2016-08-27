# -*- coding: utf-8 -*-
import urllib
import urllib2
try: import simplejson as json
except ImportError: import json
import os
import sys
from distutils.version import LooseVersion

# format json
def format(typejson):
    return json.dumps(typejson, indent=4, separators=(',', ': '));

# load URL
try:
    loadConfig = open('url.json', 'r')
    configURL = json.load(loadConfig)
    loadConfig.close()
    url = configURL['url']
    id = configURL['id']
    version = configURL['version']
except IOError, e:
    print e
    sys.exit(1)
except ValueError, e:
    print e
    sys.exit(1)

print '-------- DOWNLOADER --------'
print '- Fetch URL: ' + url + ' -'
print '- Fetch ID: ' + id + ' -'
print '- Fetch VERSION: ' + ('latest' if version is None else version) + ' -'
print '----------------------------'

try:
    indexResponse = urllib2.urlopen(url + 'index.json')
    indexJson = json.loads(indexResponse.read())
except urllib2.URLError, e:
    print e
    sys.exit(1)
except ValueError, e:
    print e
    sys.exit(1)
if version is None:
    versions = sorted(indexJson[id], key=LooseVersion, reverse=True)
    version = versions[0]
    print '- Determined latest version: ' + version + ' -'

