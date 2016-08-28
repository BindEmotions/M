# -*- coding: utf-8 -*-
import urllib
import urllib2
try: import simplejson as json
except ImportError: import json
import os
import sys
import cgi
import urlparse
import zipfile
import multiprocessing
from more_itertools import chunked
from distutils.version import LooseVersion

# rendering json
def renderingJson(typejson):
    return json.dumps(typejson, indent=4, separators=(',', ': '));

# get localdir path
path = os.path.dirname(os.path.abspath(__file__))

# load URL
try:
    loadConfig = open(path + os.sep + 'url.json', 'r')
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

# show informations
print '-------- DOWNLOADER --------'
print '- Fetch URL: ' + url
print '- Fetch ID: ' + id
print '- Fetch VERSION: ' + ('latest' if version is None else version)
print '----------------------------'

# get index.json
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

# get id/version.json
try:
    idResponse = urllib2.urlopen(url + id + '/' + version + '.json')
    idJson = json.loads(idResponse.read())
except urllib2.URLError, e:
    print e
    sys.exit(1)
except ValueError, e:
    print e
    sys.exit(1)

# download
def showProgress(bytesSoFar, totalBytes):
    progressLine = '- %s/%s (%0.2f%%) ...\r' % (bytesSoFar, totalBytes, float(bytesSoFar) / totalBytes * 100)
    sys.stdout.write(progressLine)
    sys.stdout.flush()

def download(content):
    try:
        contentTo = str(content['to'])
    except:
        contentTo = None
    try:
        contentUnzip = content['unzip']
    except:
        contentUnzip = False
    try:
        contentReferer = content['referer']
    except:
        contentReferer = None
    contentName = str(content['name'])
    contentUrl = str(content['from'])
    # download
    print '- Downloading ' + contentName + ' ...'

    contentRequest = urllib2.Request(contentUrl)
    # set User-Agent (Win Chrome)
    contentRequest.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36')
    # set Referer
    if contentReferer is not None:
        contentRequest.add_header('Referer', contentReferer)

    if contentTo is None:
        contentPath = path 
    else:
        contentPath = path + os.sep + contentTo
        if not os.path.exists(contentPath):
            try:
                os.makedirs(contentPath)
            except:
                print "処理被りモタク"

    try:
        contentResult = urllib2.urlopen(contentRequest)
        totalBytes = int(contentResult.info().getheader('Content-Length'))
        if contentResult.info().getheader('Content-Disposition') is not None:
            contentFilename = urllib.unquote(cgi.parse_header(contentResult.headers.getheader('Content-Disposition'))[1]['filename'])
        else:
            contentFilename = urllib.unquote(urlparse.urlparse(contentUrl).path.rsplit('/', 1)[1])
        print '- Saving ' + contentPath + os.sep + contentFilename + ' ...'
        bytesSoFar = 0

        showProgress(bytesSoFar, totalBytes)

        with open(contentPath + os.sep + contentFilename, 'wb') as contentFile:
            while True:
                readBytes = contentResult.read(1024 * 100)
                bytesSoFar += len(readBytes)

                if not readBytes:
                    contentResult.close()
                    sys.stdout.write('\n')
                    break

                contentFile.write(readBytes)
                showProgress(bytesSoFar, totalBytes)

    except urllib2.HTTPError, e:
        print e

    if contentUnzip:
        print '- Unpacking to ' + contentPath + ' ...'
        try:
            with zipfile.ZipFile(contentPath + os.sep + contentFilename, 'r') as zip_file:
                zip_file.extractall(contentPath)
            os.remove(contentPath + os.sep + contentFilename)
        except zipfile.BadZipfile, e:
            print e

contents = idJson['files']

contentsLen = len(contents)
for content in list(chunked(contents, 3)):
    pool = multiprocessing.Pool(processes=3)
    pool.map(download, content)