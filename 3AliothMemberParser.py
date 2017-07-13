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
# python 3AliothMemberParser.py <datasource_id> <password>
#
# purpose:
# Gets the members in each project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def runMembers():
    try:
        cursor.execute(insertMembersQuery,
                       (datasource_id,
                        username,
                        userid,
                        fullname,
                        unixname))
        db.commit()
        print(unixname, " inserted into project members table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()


def runRoles():
    try:
        cursor.execute(insertRolesQuery,
                       (datasource_id,
                        username,
                        unixname,
                        role))
        db.commit()
        print(unixname, " inserted into project member roles table!\n")
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

selectQuery = 'SELECT unixname, memberhtml FROM al_project_indexes WHERE datasource_id = %s'

insertMembersQuery = 'INSERT INTO al_project_members (datasource_id, \
                                                      username, \
                                                      userid, \
                                                      fullname, \
                                                      unixname, \
                                                      last_updated) \
                VALUES(%s, %s, %s, %s, %s, now())'

insertRolesQuery = 'INSERT INTO al_project_members_roles (datasource_id, \
                                                          username, \
                                                          unixname, \
                                                          role, \
                                                          last_updated) \
                VALUES(%s, %s, %s, %s, now())'

try:
    cursor.execute(selectQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        unixname = project[0]
        html = project[1]
        print('\nworking on ', unixname)

        soup = BeautifulSoup(html, 'html.parser')
        tbody = soup.find('tbody')

        tr = tbody.find_all('tr')
        for t in tr:
            #print(t, '\n')
            td = t.find_all('td')
            for section in td:
                if 'sioc:name' in str(section):
                    if '<strong>' in str(section):
                        regexFullname = '\"sioc:name\"></span><strong>(.*?)</strong></div>'
                        nameFinder = re.findall(regexFullname, str(section))
                        if nameFinder:
                            fullname = nameFinder[0]
                            print('*full name: ', fullname)
                    else:
                        regexFullname = '\"sioc:name\"></span>(.*?)</div>'
                        nameFinder = re.findall(regexFullname, str(section))
                        if nameFinder:
                            fullname = nameFinder[0]
                            print('full name: ', fullname)
                
                if '<td><a href="https://alioth.debian.org/users' in str(section):
                    username = section.contents[0].contents[0]
                    print('username: ', username)
                
                if 'href=' not in str(section):
                    if 'div about=' not in str(section):
                        role = section.contents[0]
                        print('role: ', role)
                
                regexId = 'user_id=(.*?)"'
                idFinder = re.findall(regexId, str(section))
                if idFinder:
                    userid = idFinder[0]
                    print('user id: ', userid)
 
            runMembers()
            runRoles()

except pymysql.Error as err:
    print(err)
