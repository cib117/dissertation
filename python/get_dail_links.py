# import required libraries
from bs4 import BeautifulSoup
import re
import random
import time
import urllib2
from urllib2 import URLError, HTTPError

def removeDups(seq, idfun=None): 
   """
   Function to remove duplicates from list
   
   Keyword arguments:
   seq -- list of strings, some of which may be duplicates
   
   Returns:
   result -- list of strings, with no duplicates
   """
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def get_month_urls(year):
    """Get the month index urls from the Dail website for a given year.

    Keyword arguments:
    year -- The year for which you want to get the links.
    """
    url = 'http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=dail&year='+str(year) # open the year index page
    print 'trying: '+str(url)
    try:
        response = urllib2.urlopen(url)
    except HTTPError, e:        # if httperror
        print 'Error on request ', url # page causing error
        print 'Error code: ', e.code # print error code
        print 'Taking a break'
        time.sleep(random.uniform(60,120))
    except URLError, e: # if urlerror
        print 'Failed to reach a server.', url # page causing error
        print 'Reason: ', e.reason # print reason for error
        print 'Exiting'
        sys.exit() # stop
    else:
        html = response.read() # read html
        soup = BeautifulSoup(html) # soup this html
        atags = soup.findAll('a') # get a tags
        # only extract urls containing month (and add start of url)
        links = ['http://oireachtasdebates.oireachtas.ie'+str(i.get('href')) for i in atags if re.search('month', str(i.get('href')))]
        print 'Successfully extracted links from '+str(url)
        time.sleep(random.uniform(3,6)) # sleep to give website a break
    return links
    
def get_speech_urls(month):
    """Get the urls of speeches/questions from the Dail website for a given year.

    Keyword arguments:
    month -- The month for which you want to get the links.
    """
    url = month # open the month index page identified by getMonthUrls
    print 'trying: '+str(url)
    try:
        response = urllib2.urlopen(url)
    except HTTPError, e:        # if httperror
        print 'Error on request ', url # page causing error
        print 'Error code: ', e.code # print error code
        print 'Taking a break'
        time.sleep(random.uniform(60,120))
    except URLError, e: # if urlerror
        print 'Failed to reach a server.', url # page causing error
        print 'Reason: ', e.reason # print reason for error
        print 'Exiting'
        sys.exit() # stop
    else:
        html = response.read() # read html
        soup = BeautifulSoup(html) # soup this html
        atags = soup.findAll('a') # get a tags
        # only extract urls containing opendocument (and add start of url)
        speechlinks = ['http://oireachtasdebates.oireachtas.ie'+str(i.get('href')) for i in atags if re.search('opendocument', str(i.get('href')))]
        print 'Successfully extracted links from '+str(url)
        time.sleep(random.uniform(3,6)) # sleep to give website a break
    return speechlinks

# get month links
monthlinks = []
for yr in xrange(2007, 2016+1):
    monthlinks.extend(getMonthUrls(yr))

# get links to individual speech/question pages
urllinks = []
for link in monthlinks:
    urllinks.extend(getSpeechUrls(link))

# Remove the fragment identifier to prevent scraping pages multiple times. The last link in the broken, so drop it.    
urllinks = [re.sub(r'[#][A-Z0-9]+', '', link) for link in urllinks[:-1]]

# Remove duplicates
urllinks = removeDups(urllinks)
    
# save the speech/question links to a text file
out = open('data/speechlinks.txt', 'w')
for item in urllinks:
  out.write("%s\n" % item)