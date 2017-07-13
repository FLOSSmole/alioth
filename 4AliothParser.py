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
# python 4AliothParser.py <datasource_id> <password>
#
# purpose:
# Gets informatin on the audience, language, status, environment, 
# license, operating system, and topic of each project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def runQuery(word, query):
    def run1():
        try:
            cursor.execute(query,
                           (datasource_id,
                            desc,
                            cat,
                            unixname))
            db.commit()
            print(unixname, " inserted into ", word, "table!\n")
        except pymysql.Error as err:
            print(err)
            db.rollback()

    def run2():
        try:
            cursor.execute(query,
                           (datasource_id,
                            desc,
                            cat,
                            subdesc,
                            subcat,
                            unixname))
            db.commit()
            print(unixname, " inserted into ", word, "table!\n")
        except pymysql.Error as err:
            print(err)
            db.rollback()

    def run3():
        try:
            cursor.execute(query,
                           (datasource_id,
                            desc,
                            cat,
                            subdesc,
                            subcat,
                            subdesc2,
                            subcat2,
                            unixname))
            db.commit()
            print(unixname, " inserted into ", word, "table!\n")
        except pymysql.Error as err:
            print(err)
            db.rollback()

    if word in str(l.contents[0]):
        i = 1
        for section in l.contents[1:]:
            if i == 2:
                match = re.findall(regex, str(section))
                if match:
                    cat = match[0][0]
                    print('cat: ', cat)

                    desc = match[0][1]
                    print(word, ': ', desc)

            if i == 4:
                match = re.findall(regex, str(section))
                if match:
                    subcat = match[0][0]
                    print('subcat: ', subcat)

                    subdesc = match[0][1]
                    print('sub', word, ': ', subdesc)

            if i == 6:
                match = re.findall(regex, str(section))
                if match:
                    subcat2 = match[0][0]
                    print('subcat2: ', subcat2)

                    subdesc2 = match[0][1]
                    print('sub', word, '2: ', subdesc2)

            i = i + 1

        if i == 3:
            if word is 'Environment' or word is 'License':
                subdesc = None
                subcat = None
                run2()

            if word is 'Operating System' or word is 'Topic':
                subdesc = None
                subcat = None
                subdesc2 = None
                subcat2 = None
                run3()

            if word is 'Audience' or word is 'Language' or word is 'Status':
                run1()

        if i == 5:
            if word is 'Environment' or word is 'License':
                run2()
            else:
                subdesc2 = None
                subcat2 = None
                run3()

        if i == 7:
            run3()

# establish database connection: SYR
try:
    db = pymysql.connect(host='flossdata.syr.edu',
                         user='',
                         passwd='',
                         db='',
                         use_unicode=True,
                         charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

selectQuery = 'SELECT unixname, indexhtml FROM al_project_indexes WHERE datasource_id = %s'

insertAudienceQuery = 'INSERT INTO al_projects_audience (datasource_id, \
                                                         audience, \
                                                         cat, \
                                                         unixname, \
                                                         last_updated) \
                        VALUES(%s, %s, %s, %s, now())'

insertEnvironmentQuery = 'INSERT INTO al_projects_environment (datasource_id, \
                                                               environment, \
                                                               cat, \
                                                               subenvironment, \
                                                               subcat, \
                                                               unixname, \
                                                               last_updated) \
                        VALUES(%s, %s, %s, %s, %s, %s, now())'

insertLanguageQuery = 'INSERT INTO al_projects_language (datasource_id, \
                                                         language, \
                                                         cat, \
                                                         unixname, \
                                                         last_updated) \
                        VALUES(%s, %s, %s, %s, now())'

insertLicenseQuery = 'INSERT INTO al_projects_license (datasource_id, \
                                                       license, \
                                                       cat, \
                                                       sublicense, \
                                                       subcat, \
                                                       unixname, \
                                                       last_updated) \
                    VALUES(%s, %s, %s, %s, %s, %s, now())'

insertOSQuery = 'INSERT INTO al_projects_os (datasource_id, \
                                             os, \
                                             cat, \
                                             subos, \
                                             subcat, \
                                             subos2, \
                                             subcat2, \
                                             unixname, \
                                             last_updated) \
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, now())'

insertStatusQuery = 'INSERT INTO al_projects_status (datasource_id, \
                                                     status, \
                                                     cat, \
                                                     unixname, \
                                                     last_updated) \
                        VALUES(%s, %s, %s, %s, now())'

insertTopicQuery = 'INSERT INTO al_projects_topic (datasource_id, \
                                                   topic, \
                                                   cat, \
                                                   subtopic, \
                                                   subcat, \
                                                   subtopic2, \
                                                   subcat2, \
                                                   unixname, \
                                                   last_updated) \
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, now())'

try:
    cursor.execute(selectQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        unixname = project[0]
        html = project[1]
        print('\nworking on ', unixname)

        soup = BeautifulSoup(html, 'html.parser')
        divMain = soup.find('div', id='maindiv')
        li = divMain.find_all('li')
        for l in li:
            regex = 'form_cat=(.*?)\">(.*?)</a>'

            runQuery('Audience', insertAudienceQuery)
            runQuery('Language', insertLanguageQuery)
            runQuery('Status', insertStatusQuery)
            runQuery('Environment', insertEnvironmentQuery)
            runQuery('License', insertLicenseQuery)
            runQuery('Operating System', insertOSQuery)
            runQuery('Topic', insertTopicQuery)

except pymysql.Error as err:
    print(err)
