import subprocess
import os

class mri_convert(object):

    def __init__(self, path='mri_convert', args_list=['-it', 'mgz' , '-ot', 'nii' , '-iid', '-1', '0', '0', '-ijd', '0', '0', '-1', '-ikd', '0', '1', '0' , '-r', '1', '-3', '2']):
        self.args_list = args_list
        self.path = path

    def convert(self, input_path, output_path):
        if not os.path.exists(input_path):
            raise Exception('input_path {} does not exist'.format(input_path))
        if os.path.exists(output_path):
            raise Exception('output_path {} does already exists!'.format(output_path))
        args_list = [self.path] + self.args_list + [input_path, output_path]
        #execute script
        print "Executing {}".format(' '.join(args_list))
        p = subprocess.Popen(args_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if stderr != '':
            print "mri_convert Error: {}".format(stderr)
        print stdout
