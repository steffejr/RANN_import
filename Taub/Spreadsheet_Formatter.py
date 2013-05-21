import csv
import re

class row_info(object):
    def __init__(self):
        self.subid = None
        self.visid = None
        self.dob = None
        self.gender = None
        self.visdate = None
        self.vistime = None
        self.perf = None
        self.DQ_list = []


    def parserow(self, in_row):
        out_row = 8 * ['']

        if self.subid != None and in_row[self.subid] != '':
            try:
                out_row[0] = "P{0:08d}".format(int(in_row[self.subid]))
            except ValueError:
                out_row[0] = in_row[self.subid]
        else:
            return None
        if self.visid != None and in_row[self.visid] != '':
            out_row[1] = in_row[self.visid]
        else:
            return None
        if self.dob != None:
            out_row[2] = in_row[self.dob]
        if self.gender != None:
            out_row[3] = in_row[self.gender]
        if self.visdate != None:
            out_row[4] = in_row[self.visdate]
        if self.vistime != None:
            out_row[5] = in_row[self.vistime]
        row_dq_list = [in_row[i] != '' for i in self.DQ_list]
        if any(row_dq_list):
            out_row[6] = 'Y'
        else:
            out_row[6] = 'N'
        if self.perf != None:
            out_row[7] = in_row[self.perf]
        return out_row

    def __repr__(self):
        return 'subid:{0.subid} visid:{0.visid} dob:{0.dob} gender:{0.gender} visdate:{0.visdate} vistime:{0.vistime} perf:{0.perf} DQ:{0.DQ_list}'.format(self)

    @staticmethod
    def removeNonAscii(s):
        return "".join(i for i in s if ord(i) < 128)

#    def DQ(self):
#        if any(self)

def extract_headernames(headers, accepted_headings):
    row_templates = {}
    for heading in accepted_headings:
        new_row = row_info()
        visid_REC = re.compile(heading + ' id', re.IGNORECASE)
        visdate_REC = re.compile(heading + ' date', re.IGNORECASE)
        perf_REC = re.compile(heading + ' perf', re.IGNORECASE)
        for i in range(0, len(headers)):
            if headers[i].lower() == 'dob':
                new_row.dob = i
            if headers[i].lower() == 'gender':
                new_row.gender = i
            if headers[i].lower() == 'subid':
                new_row.subid = i
            if headers[i].upper().endswith('DQ'):
                new_row.DQ_list.append(i)
            if visid_REC.match(headers[i]):
                new_row.visid = i
            if visdate_REC.match(headers[i]):
                new_row.visdate = i
            if perf_REC.match(headers[i]):
                new_row.perf = i
        row_templates[heading] = new_row
    return row_templates


def format_CSV(csv_path_in, csv_writer, accepted_headings=[], check_perf=True, check_dob=True, override=True, DEBUG=False):
    with open(csv_path_in, 'rb') as csv_file_in:
        dialect = csv.Sniffer().sniff(csv_file_in.read(1024))
        csv_file_in.seek(0)
        reader = csv.reader(csv_file_in, dialect=dialect)
        headers = reader.next()
        row_templates = extract_headernames(headers, accepted_headings)
        if DEBUG:
            print row_templates
            print "Headers:\n" + '\t'.join(headers)

        for row in reader:
            if not any(row):
                continue
            row = [row_info.removeNonAscii(x) for x in row]
            for template in row_templates.itervalues():
                out_row = template.parserow(row)
                if out_row != None:
                    csv_writer.writerow(out_row)

def format_CSVs(csv_paths_in, csv_path_out, accepted_headings=[], check_perf=True, check_dob=True, override=True, DEBUG=False):
    with open(csv_path_out, 'wb') as csv_path_out:
        csv_writer = csv.writer(csv_path_out)
        csv_writer.writerow(['Subid', 'Visid', 'DOB', 'Gender', 'VisDate', 'VisTime', 'DQ', 'Performance'])
        for csv_path_in in csv_paths_in:
            format_CSV(csv_path_in, csv_writer, accepted_headings=accepted_headings, check_perf=check_perf, check_dob=check_dob, override=override, DEBUG=DEBUG)

