## import required libraries
import re
import time
import urllib2
from urllib2 import URLError, HTTPError
import random

def scrape_speeches(links, logname, folder):
    """
    Get raw html of speeches
    
    Keyword arguments:
    links -- list of urls of speeches
    logname -- string for the name of log file which records errors
    folder -- folder to save html into

    Outputs:
    logfile -- a txt file recording errors and progress
    *.htm -- html file for each url
    """
    logname = logname # log file to record errors
    logfile = open(logname, 'w') # open log file
    errorcount = 0 # initialize error count = 0
    for link in links:
        url = link
        print 'Trying url', url 
        try:
            request = urllib2.Request(url, headers={"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13"})
            response = urllib2.urlopen(request) # try url
        except HTTPError, e:        # if httperror
            print 'Error on request ', url 
            print 'Error code: ', e.code
            error1= 'Error code' +str(e.code)
            errorcount += 1 # add to error count
            logline = ','.join([url,error1])+'\n' # record url and error in log file
            logfile.write(logline) # write to log file
        except URLError, e: # if urlerror
            print 'Failed to reach a server.'
            print 'Reason: ', e.reason
            error2= 'Error code:' +str(e.reason)
            print 'Exiting'
            logline = ','.join([url,error2])+'\n' # record url and error in log file
            logfile.write(logline) # write to log file
            sys.exit() # Something's gone wrong, stop hitting the server
        except socket.error:
            print 'Socket error'
            print 'Exiting'
            error3 = 'Socket error' 
            logline = ','.join([url,error3])+'\n' # record url and error in log file
            logfile.write(logline) # write to log file
            sys.exit() # Something's gone wrong, stop hitting the server
        else:
            html = response.read() # read html
            shortname = re.search('dail\d+', url).group(0)
            filename = 'html/'+folder+'/'+shortname # save page using link name 
            file = open(filename, 'w') # open file
            file.write(html) # write html
            file.close() # close htm file
            success= ','.join([str(url),' written'])+'\n' # save progress to log file
            print 'Wrote ', url
            logfile.write(success) # write to logfile
        if errorcount > 5:
            print 'Have accumulated ', str(errorcount), ' errors. Exiting.'
            sys.exit() 
        time.sleep(random.uniform(6, 10)) ## Don't do anything for 6-10 seconds
    logfile.close()                       

# Open the list of urls
urls = open('data/speechlinks.txt', 'r').read().splitlines()
# Scrape speeches
scrapeSpeeches(urls, 'dailscrapelog.txt', 'dail_html')