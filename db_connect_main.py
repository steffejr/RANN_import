'''
Created on Sep 4, 2012

@author: jason
'''
'''
Created on Aug 31, 2012

@author: jason
'''

import pymysql
import pymysql.cursors
import csv
from collections import defaultdict

class db_connect_main(object):

    def __init__(self, host, port, user, passwd, db):
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()


    def fetch_table_dict_of_study(self, study_name, ):
        print study_name
        print self.conn.db
        table = self.fetch_table_dict(study_name)
        return table[study_name]
    
    
    def fetch_table_dict(self, table_name):
        
        table_dict = defaultdict(lambda: defaultdict(dict))
        sqlcommand = 'SELECT * FROM {}'.format(table_name)
        print sqlcommand
        self.cur.execute(sqlcommand)
        for row_dict in self.cur.fetchall():
            study_name = row_dict['StudyName']
            subid = row_dict['subid']
            visid = row_dict['visitid']
            table_dict[study_name][subid][visid] = row_dict
        return table_dict
    
    def fetch_table_dict_of_study_mriQC(self, study_name, SeriesName):
        print study_name
        print self.conn.db #name of the database
        table = self.fetch_table_dict_mriQC(study_name,SeriesName)
        return table[study_name]
    
    def fetch_table_dict_mriQC(self, study_name, SeriesName):
        
        table_dict = defaultdict(lambda: defaultdict(dict))
        sqlcommand = "SELECT subid,visitid,StudyName,qc_mri_"+SeriesName+" FROM "+self.conn.db+".AllData where StudyName='"+study_name+"';" 
        print sqlcommand
        self.cur.execute(sqlcommand)
        for row_dict in self.cur.fetchall():
            study_name = row_dict['StudyName']
            subid = row_dict['subid']
            visid = row_dict['visitid']
            
            table_dict[study_name][subid][visid] = row_dict
        return table_dict
    
    