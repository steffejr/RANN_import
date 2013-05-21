from Visit_Ref import Visit_Ref
from collections import defaultdict
from datetime import datetime
from ManageStudy.ManageStudyErrors.RefErrors import Bad_Column_Entry_Exception
import csv


class CSV_Ref(object):

    def __init__(self, csvfile_path):
        '''ref_dict['subid']['scanid']'''
        self.ref_dict = self.ref_dict_from_csv(csvfile_path)

    @staticmethod
    def isDateFormat(input_string):
        try:
            datetime.strptime(input_string, '%m/%d/%Y')
            return True
        except ValueError:
            try:
                datetime.strptime(input_string, '%m/%d/%y')
                return True
            except ValueError:
                return False
    @staticmethod
    def isTimeFormat(input_string):
        try:
            datetime.strptime(input_string, '%H:%M:%S')
            return True
        except ValueError:
            return False
    @staticmethod
    def isFloatTimeFormat(input_string):
        try:
            datetime.strptime(input_string, '%H:%M:%S.%f')
            return True
        except ValueError:
            return False

    @staticmethod
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def gender_format(gender):
        gender_l = gender.strip().lower()
        if gender_l == '':
            return None
        if gender_l in ['m', 'male', 'man']:
            return 'M'
        elif gender_l in ['f', 'female', 'woman']:
            return 'F'
        else:
            return gender


    @staticmethod
    def ref_dict_from_csv(csvfile_path, DEBUG=False):
        '''csv format: subid,visid,date,time,exclude, has header row
        'Subid', 'Visid', 'BirthYear','Gender', 'VisitDate', 'VisitTime', 'Excluded','Performance'
        '''
        ref_dict = defaultdict(dict)
        with open(csvfile_path, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect=dialect)
            headers = reader.next()
            if DEBUG:
                print "Headers:\n" + '\t'.join(headers)
            for row in reader:
                if len(row) < 8:
                    row.extend([''] * (8 - len(row)))
                #print '\t'.join(row)
                VisitDateTime = CSV_Ref.datetime_from_date_and_time(date=row[4], time=row[5])
                BirthDate = CSV_Ref.datetime_from_date_and_time(date=row[2])
                Gender = CSV_Ref.gender_format(gender=row[3])
                if (row[6].lower() == 'y' or row[5].lower() == 'true'):
                    exclude = True
                elif (row[6].lower() == 'n' or row[5].lower() == 'false'):
                    exclude = False
                elif row[6].lower() == '?' or row[5].lower() == '':
                    exclude = None
                else:
                    raise Bad_Column_Entry_Exception(entry=row[6], column=7, why='Row Entry must be Y/N True/False ? for column 6: Excluded')
                try:
                    Performance = None if row[7] == '' else int(row[7])
                except ValueError:
                    raise Bad_Column_Entry_Exception(entry=row[7], column=8, why='Row Entry must be 0,1,2 (0: no scans, 1: partial, 2: complete) for column 8: Performance')
                new_visit_ref = Visit_Ref(subid=row[0], visid=row[1], BirthDate=BirthDate, Gender=Gender, VisitDateTime=VisitDateTime, exclude=exclude, Performance=Performance)
                if new_visit_ref.subid in ref_dict:
                    for key in ref_dict[new_visit_ref.subid].iterkeys():
                        existing_sub = ref_dict[new_visit_ref.subid][key]
                        existing_sub.merge_both(new_visit_ref)
                ref_dict[new_visit_ref.subid][new_visit_ref.visid] = new_visit_ref
        return ref_dict


    @staticmethod
    def datetime_from_date_and_time(date, time=None):
        if date == 'XXXX-XX-XX':
            return datetime.min
        if not CSV_Ref.isDateFormat(date):
            return None
        try:
            date_obj = datetime.strptime(date, '%m/%d/%Y')
        except ValueError:
            date_obj = datetime.strptime(date, '%m/%d/%y')

        if time == '' or time == None or time == 'XX:XX:XX':
            return date_obj
        elif CSV_Ref.isTimeFormat(time) or CSV_Ref.isFloatTimeFormat(time):
            time_split = time.split(":")
            formatted_date_time = "{1}:{2}:{3:.6f}".format(time_split[0], time_split[1], float(time_split[2]))
            time_obj = datetime.strptime(formatted_date_time, '%H:%M:%S.%f')
            date_obj.hour = time_obj.hour
            date_obj.minute = time_obj.minute
            date_obj.second = time_obj.second
            date_obj.microsecond = time_obj.microsecond
            return date_obj

#    def csv_from_ref_dict(self, csvfile_path):
#        with open(csvfile_path, 'wb') as csvfile:
#            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#            writer.writerow(['Subid', 'Visid', 'BirthYear', 'Gender', 'VisitDate', 'VisitTime', 'Excluded', 'Performance'])
#            for subid in self.ref_dict.iterkeys():
#                for visid in self.ref_dict[subid].iterkeys():
#                    visit_ref = self.ref_dict[subid][visid]
#                    visdate=
#                    vistime=
#                    exclude = 'Y' if visit_ref.exclude else 'N'
#                    writer.writerow([visit_ref.subid,
#                                     visit_ref.visid,
#                                     visit_ref.BirthDate.strftime('%Y'),
#                                     visit_ref.Gender,
#                                     visit_ref.VisitDateTime.strftime('%m/%d/%Y'),
#                                     visit_ref.VisitDateTime.strftime('%H:%M:%S.%f'),
#                                     visit_ref.exclude,
#                                     visit_ref.Performance])


    def dicom_series_info_gender_checks_against_ref(self, dicom_series_info):
        if dicom_series_info.subid not in self.ref_dict:
            return False
        elif dicom_series_info.visid not in self.ref_dict[dicom_series_info.subid]:
            return False
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].Gender == None:
            return False
        ref_gender = self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].Gender
        if ref_gender == dicom_series_info.PatientsSex:
            return True
        else:
            return False

    def dicom_series_info_date_checks_against_ref(self, dicom_series_info):
        '''Returns True if the dicom_series_info.VisitDateTime.date() matches the ref VisitDateTime,
        or if the ref VisitDateTime is set to datetime.min, indicating that a special XXXX-XX-XX parameter was
        passed for the subject in the input csv (info does not exist -> omit)'''
        if dicom_series_info.subid not in self.ref_dict:
            return False
        elif dicom_series_info.visid not in self.ref_dict[dicom_series_info.subid]:
            return False
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].VisitDateTime == None:
            return False
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].VisitDateTime == datetime.min:
            return True
        ref_date = self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].VisitDateTime
        
#        print "{}\t{}\t{}\t{}".format("Debug",dicom_series_info.subid,dicom_series_info.visid,dicom_series_info.SeriesNumber)
        
 #       if dicom_series_info.subid=="P00004614" and dicom_series_info.visid=="S0001" and dicom_series_info.SeriesNumber==401:
  #              print "This is where it breaks..."
        
                
        if ref_date.date() == dicom_series_info.VisitDateTime.date():
            return True
        else:
            return False

    def dicom_series_info_birth_year_checks_against_ref(self, dicom_series_info):
        '''Returns True if the dicom_series_info.BirthDate.year matches the ref VisitDateTime,
        or if the ref VisitDateTime is set to datetime.min, indicating that a special XXXX-XX-XX parameter was
        passed for the subject in the input csv (info does not exist -> omit)'''
        if dicom_series_info.subid not in self.ref_dict:
            return False
        elif dicom_series_info.visid not in self.ref_dict[dicom_series_info.subid]:
            return False
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].BirthDate == None:
            return False
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].BirthDate == datetime.min:
            return True
        birth_date = self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].BirthDate
        if birth_date.year == dicom_series_info.BirthDate.year:
            return True
        else:
            return False

    def dicom_series_info_ref_date(self, dicom_series_info):
        if dicom_series_info.subid not in self.ref_dict:
            return "Subid {} not in Ref CSV".format(dicom_series_info.subid)
        elif dicom_series_info.visid not in self.ref_dict[dicom_series_info.subid]:
            return "Visid not in Ref CSV"
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].VisitDateTime == None:
            return "VisitDate not in Ref CSV"
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].VisitDateTime == datetime.min:
            return "XXXX-XX-XX"
        ref_time = self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].VisitDateTime
        return ref_time.strftime('%m/%d/%Y')

    def dicom_series_info_birth_year(self, dicom_series_info):
        if dicom_series_info.subid not in self.ref_dict:
            return "Subid {} not in Ref CSV".format(dicom_series_info.subid)
        elif dicom_series_info.visid not in self.ref_dict[dicom_series_info.subid]:
            return "Visid not in Ref CSV"
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].BirthDate == None:
            return "BirthDate not in Ref CSV"
        elif self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].BirthDate == datetime.min:
            return "XXXX"
        birth_date = self.ref_dict[dicom_series_info.subid][dicom_series_info.visid].BirthDate
        return birth_date.year


