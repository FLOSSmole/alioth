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
# python 2AliothTagParser.py <datasource_id> <password>
#
# purpose:
# Gets the tags in each project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def run():
    try:
        cursor.execute(insertQuery,
                       (datasource_id,
                        tag,
                        unixname))
        db.commit()
        print(unixname, " inserted into tags table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()

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

insertQuery = 'INSERT INTO al_projects_tags (datasource_id, \
                                             tag, \
                                             unixname, \
                                             last_updated) \
                VALUES(%s, %s, %s, now())'

try:
    cursor.execute(selectQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        unixname = project[0]
        html = project[1]
        print('\nworking on ', unixname)

        soup = BeautifulSoup(html, 'html.parser')

        p = soup.find_all('p')
        for line in p:
            if 'Tags:' in str(line):
                a = line.find_all('a')
                for section in a:
                    tag = section.contents[0]
                    print('tag: ', tag)
                    run()

except pymysql.Error as err:
    print(err)
