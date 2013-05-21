import pymysql
import pymysql.cursors
import csv
from collections import defaultdict

class db_connect(object):

    def __init__(self, host, port, user, passwd, db):
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()


    def enter_index_visits(self, study_name, index):
        visits_dict = self.fetch_table_dict_of_study_visits(study_name)
        study_dict = self.fetch_table_dict_of_study(study_name)
        for subject in index.subjectlist:
            for visit in subject.visitlist:
                if visit.visid not in visits_dict[subject.subid]:
                    visits_row_dict = self.create_row_dict(visit)
                    self.insert_row_dict_into_table('Visits', visits_row_dict)
                if visit.visid not in study_dict[subject.subid]:
                    study_row_dict = self.create_row_dict(visit)
                    self.insert_row_dict_into_table(study_name, study_row_dict)
        self.cur.execute('commit')

    def update_db_from_csvref(self, study_name, csv_ref):
        study_dict = self.fetch_table_dict_of_study(study_name)
        for subject in csv_ref.ref_dict.iterkeys():
            for visit in csv_ref.ref_dict[subject].iterkeys():
                if visit not in study_dict[subject]:
                    continue
                if csv_ref.ref_dict[subject][visit].exclude:
                    ref_entry = '0'
                else:
                    ref_entry = '1'
                if (study_dict[subject][visit]['IncludeSubjectRef'] != ref_entry):
                    study_dict[subject][visit]['IncludeSubjectRef'] = ref_entry
                    print "Updated IncludeSubjectRef for {0} {1} to {2}".format(subject, visit, ref_entry)
                    self.update_row_dict_in_table(study_name, study_dict[subject][visit])
		else:
		    print "subject already entered"
        self.cur.execute('commit')

    def fetch_table_dict_of_study_visits(self, study_name):
        table = self.fetch_table_dict('Visits')
        return table[study_name]

    def fetch_table_dict_of_study(self, study_name):
        table = self.fetch_table_dict(study_name)
        return table[study_name]

    def fetch_table_dict(self, table_name):
        table_dict = defaultdict(lambda: defaultdict(dict))
        self.cur.execute('SELECT * FROM {}'.format(table_name))
        for row_dict in self.cur.fetchall():
            study_name = row_dict['StudyName']
            subid = row_dict['subid']
            visid = row_dict['visitid']
	    #print visitdate
            # JASON CHANGE
            # Strip off the beginning of the visid from the SQL table
            visid = visid[-5:]
            # END JASON
            table_dict[study_name][subid][visid] = row_dict
        return table_dict

    def create_row_dict(self, scan):
        mydict = {}
        mydict['subid'] = scan.subject.subid
        # Jason added this
        visid = scan.subject.index.project.name+"_"+scan.subject.subid+"_"+scan.visid
        mydict['visitid'] = visid
#        mydict['visitid'] = scan.visid
        mydict['StudyName'] = scan.subject.index.project.name
        return mydict

    def table_2_csv(self, study_name, table_name, path):
        csv_dict = self.fetch_table_dict(table_name)
        csv_dict = csv_dict[study_name]
        with open(path, 'wb') as csv_file:
            series_info_writer = csv.writer(csv_file, delimiter=r',', quotechar=r'"', quoting=csv.QUOTE_MINIMAL)
            column_keys = csv_dict[csv_dict.keys()[0]].keys()
            series_info_writer.writerow(column_keys)
            for subid in csv_dict.iterkeys():
                for visitid in csv_dict[subid].iterkeys():
                    row = []
                    for column in column_keys:
                        row.append(csv_dict[subid][visitid][column])
                    series_info_writer.writerow(row)

    def insert_row_dict_into_table(self, table_name, row_dict, DEBUG=False):
        keys = row_dict.keys()
        values = row_dict.values()
        query = 'insert into {0} ({1}) values ({2});'.format(table_name, ','.join(keys), ','.join(['%s'] * len(keys)))
        # JASON
        query = query+" on duplicate key update "
        for i in range(0,len(keys)):
            query = query+keys[i]+"='"+values[i]+"',"
	   # query = query+keys[-1]+"='"+values[-1]+"'"
	query=query[0:-1]
        # END JASON    
        #if DEBUG:
        print "query:: " + query
        print "values: " + 'insert into {0} ({1}) values ({2});'.format(table_name, ','.join(keys), ','.join(values))
#	self.cur.execute(query)        
	self.cur.execute(query, values)

    def update_row_dict_in_table(self, table_name, row_dict, DEBUG=False):
        keys = row_dict.keys()
        values = row_dict.values()
        where_clause = ' WHERE (subid="{0}" AND visitid="{1}" AND StudyName="{2}");'.format(row_dict['subid'], row_dict['visitid'], row_dict['StudyName'])
        query = "update " + table_name + " set " + ",".join([key + "=%s" for key in keys]) + where_clause
        if DEBUG:
            print "query:: " + query
        self.cur.execute(query, values)


