# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# License: GPLv3
# 
# Contribution from:
# Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for free and open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to:
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# International Journal of Information Technology and Web Engineering, 1(3),
# 17–26.
#
# and
#
# FLOSSmole: a project to provide research access to
# data and analyses of open source projects.
# Available at http://flossmole.org
#
################################################################
# usage:
# python 1AliothWebScraper.py <datasource_id> <password>
#
# purpose:
# Gets the  project name, url, real url, unixname, group id, short desc
# and date registered for each Alioth project
# Gets the index html and member html of each project
################################################################

import re
import time
import sys
import pymysql
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = '122'  # sys.argv[1]


def regexMaker(regex):
    line = re.findall(regex, str(section))
    if line:
        word = line[0]
        return word    


def runProjects():
    try:
        cursor.execute(insertProjectsQuery,
                       (datasource_id,
                        display_name,
                        url,
                        real_url,
                        unixname,
                        group_id,
                        short_desc,
                        registered))
        db.commit()
        print(display_name, " inserted into projects table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()

def runIndex():
    try:
        cursor.execute(insertIndexQuery,
                       (datasource_id,
                        unixname,
                        indexhtml,
                        memberhtml))
        db.commit()
        print(display_name, " inserted into indexes table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# establish database connection: SYR
try:
    db = pymysql.connect(host='flossdata.syr.edu',
                     user='cfrankel',
                     passwd='Marco1997',
                     db='test',
                     use_unicode=True,
                     charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

insertProjectsQuery = 'INSERT INTO al_projects (datasource_id, \
                                                display_name, \
                                                url, \
                                                real_url, \
                                                unixname, \
                                                group_id, \
                                                short_desc, \
                                                registered, \
                                                last_updated) \
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, now())'

insertIndexQuery = 'INSERT INTO al_project_indexes (datasource_id, \
                                                    unixname, \
                                                    indexhtml, \
                                                    memberhtml, \
                                                    last_updated) \
                    VALUES(%s, %s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

try:
    num = 1
    numProjectsRegex = 'text-align:center;font-size:smaller\"><strong>(.*?)</strong>'
    numProjects = re.findall(numProjectsRegex, str(div))[0]

    while num < int(numProjects):
        pageurl = 'https://alioth.debian.org/softwaremap/full_list.php?page=' + str(num)
        req = urllib2.Request(pageurl, headers=hdr)
        pagehtml = urllib2.urlopen(req).read()

        soup = BeautifulSoup(pagehtml, 'html.parser')
        div = soup.find('div', id='maindiv')

        table = div.find_all('table', border='0')
        for t in table:
            for line in t:
                for l in line:
                    for section in l:
                        regexUnixname = '<a href=\"https://alioth\.debian\.org/projects/(.*?)/\"><'
                        unixnameFinder = re.findall(regexUnixname, str(section))
                        if unixnameFinder:
                            unixname = unixnameFinder[0]
                            print('unixname: ', unixname)
                            
                            url = 'https://alioth.debian.org/projects/' + str(unixname) + '/'
                            print('url: ', url)

                            # gets the html of each projecct page
                            req2 = urllib2.Request(url, headers=hdr)
                            indexhtml = urllib2.urlopen(req2).read()
                            soup2 = BeautifulSoup(indexhtml, 'html.parser')

                            regexGroupId = 'group_id=(.*?)\"'
                            group_id = re.findall(regexGroupId, str(soup2))[0]
                            print('group id: ', group_id)
                            
                            try:
                                regexRealUrl = '\"doap:homepage\"><a href=\"(.*?)\">'
                                real_url = re.findall(regexRealUrl, str(soup2))[0]
                                print('real url: ', real_url)
                            except:
                                real_url = None
                                print('real url: ', real_url)

                            # gets the html of each projecct member page
                            memberurl = 'https://alioth.debian.org/project/memberlist.php?group_id=' + str(group_id)
                            req3 = urllib2.Request(memberurl, headers=hdr)
                            memberhtml = urllib2.urlopen(req3).read()

                            display_name = regexMaker('property=\"doap:name\">(.*?)</span></strong></a>')
                            if display_name:
                                print('display name: ', display_name)

                            if 'short_desc' in str(section):
                                short_desc = section.contents[0]
                                print('short desc: ', short_desc)

                            if 'doap:name' not in str(section):
                                registeredLine = regexMaker('<strong>(.*?)</strong>')
                                registered = registeredLine.split(' ')[0]
                                print('registered: ', registered)
            runIndex()
            runProjects()
            time.sleep(.5)  # So you are not locked out of the website like I was
        num = num + 1

except pymysql.Error as err:
    print(err)

except urllib2.HTTPError as herror:
    print(herror)
