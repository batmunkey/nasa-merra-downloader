#!/usr/bin/python

__version__ ='0.3'
__author__ ='Sam Powell'
__date__ ='2/20/17'
__org__ ='CU Boulder'
__dept__ ='LASP'

import urllib2
import re 
import sys
import os
import time
import logging
import subprocess

try:
    from bs4 import BeautifulSoup
except (IOError, MemoryError, OSError, SyntaxError):
    print "Please install beautiful soup"

from cookielib import CookieJar
from urllib import urlencode

# Build a logger
def instantiateLogger():
    global logger
    logger = logging.getLogger("MERRALogger")
    hdlr = logging.FileHandler('./MERRAFileLogger.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

# Add python system statistics to log file
def pythonSystemStats():
    versionpy = subprocess.check_output("python --version", stderr=subprocess.STDOUT, shell=True)
    whichpy = subprocess.check_output("which python", shell=True)
    osslpy = subprocess.check_output("python -c 'import ssl; print ssl.OPENSSL_VERSION'", shell=True)
    logger.info("Your version of python is " + versionpy.rstrip("\n"))
    logger.info("Here is the path to your python " + whichpy.rstrip("\n"))
    logger.info("This is your pythons openssl version " + osslpy.rstrip("\n"))

# Create a submit request
def getRawHttp():
    global rawHttp
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    string = response.read()
    rawHttp = string
    return rawHttp

# Main system prompt
def prompt():
    global url
    global dir
    instructions = """\n\n                    
                  Welcome to the LASP python file downloader v0.1
                  =====================================================
                    - Currently this supports single and multiple file downloads
                    - Make sure you enter trailing slashes / after your paths 
                    - This is designed to download SINGLE files by URL with any file type
                    - MULTIPLE file download only works on .xml and .nc4 files
                    - run pip install beautifulsoup4 before running to install the html parser\n\n"""
    
    print(instructions)

    while True:
        choice = raw_input("\nDo you want to: A) Download a single file? B) Download a whole directory? [A/B/Q] : ")
        if choice == "A":
            filepath = (raw_input("\nEnter the full https:// path of the FILE you'd like to download: "))
            singleUrl = str(filepath)
            filename = (raw_input("\nEnter the name of the file: "))
            name = str(filename) 
            filedir = (raw_input("\nWhere would you like to save the FILE?: "))
            dir = str(filedir)
            singleGetter(singleUrl, name)
            logger.info('The download for this file was completed ' + filename)
            sys.exit()
        elif choice == "B":
            filepath = (raw_input("\nEnter the full path of the DIRECTORY you'd like to download with a trailing /: "))
            url = str(filepath)
            filedir = (raw_input("\nWhere would you like to save the DIRECTORY?: "))
            dir = str(filedir)
            logger.info('The path requested for download is  ' + url)
            break
        elif choice == "Q":
            sys.exit()

def nasaAuth():
    # The user credentials that will be used to authenticate access to the data
    # Need to find another way to do this, NASA's idea, not mine. Hard coded passwords are bad...
    username = ""
    password = ""
  
    # Create a password manager to deal with the 401 reponse that is returned from
    # Earthdata Login
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)
 
    # Create a cookie jar for storing cookies. This is used to store and return
    # the session cookie given to use by the data server (otherwise it will just
    # keep sending us back to Earthdata Login to authenticate).  Ideally, we
    # should use a file based cookie jar to preserve cookies between runs. This
    # will make it much more efficient.
 
    cookie_jar = CookieJar()
   
    # Install all the handlers.
 
    opener = urllib2.build_opener(
        urllib2.HTTPBasicAuthHandler(password_manager),
        #urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
        #urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
        urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)

def remove_duplicates(in_list):
    out_list = []
    added = set()
    for val in in_list:
        if not val in added:
            out_list.append(val)
            added.add(val)
    return out_list

# This gets the filenames from raw hmtl
def htmlParser(html):
    global cookedSoup
    #halfCookedSoup=[]
    cookedSoup=[]
    soup = BeautifulSoup(html)    
    for link in soup.find_all(href=re.compile(".nc4")): 
       cookedSoup.append(link.get('href'))
    return cookedSoup

def singleGetter(oneUrl, name):
    response = urllib2.urlopen(oneUrl)
    data = response.read()
    filename = dir + name
    file_ = open(filename, 'w')
    file_.write(data)
    file_.close()
    logger.info('The download for this file was completed ' + oneUrl)

def urlDownloader(filelist):
     print("\nWe will now start downloading your folder, you'll be notified at each file completion")
     deduplist = remove_duplicates(filelist)
     for item in deduplist:
         filepath = url + item
         response = urllib2.urlopen(filepath)
         data = response.read()
         filename = dir + item
         file_ = open(filename, 'w')
         file_.write(data)
         file_.close()
         print("\n" + item + "was downloaded, moving on to the next file")
         logger.info('The download for this file was completed ' + item)

# Layout the main logic
def main():
    nasaAuth()
    instantiateLogger()
    pythonSystemStats()
    prompt()
    getRawHttp()
    htmlParser(rawHttp)
    urlDownloader(cookedSoup)

# Run everything
if __name__ == '__main__':
    main()


