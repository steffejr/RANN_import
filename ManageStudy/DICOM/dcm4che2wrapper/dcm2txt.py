import subprocess
import re


class dcm2txt(object):

    def __init__(self, path='dcm2txt', option_args_list=['-w', '500', '-l', '500']):
        self.path = path
        self.option_args_list = option_args_list


    def make_dict(self, input_path):
        args_list = [self.path] + self.option_args_list + [input_path]
        series_dict = {}
        dcm2txt_process = subprocess.Popen(args_list, stdout=subprocess.PIPE)
        line = dcm2txt_process.stdout.readline()
        for line in dcm2txt_process.stdout:
            newfield = dcm2txt.parse_line(line)
            if newfield != None:
                series_dict[newfield[0]] = newfield[1]
        return series_dict



    @staticmethod
    def parse_line(line, REC=re.compile('^[0-9]+:(\([0-9A-Z]{4},[0-9A-Z]{4}\))\s+[A-Z]{2}\s+\#[0-9]+\s+\[(.*)\](.*)$')):
        result = re.match(REC, line.rstrip())
        if result == None:
            return None
        results = result.groups()
        return [x.strip() for x in results] # strip away extra whitespace

