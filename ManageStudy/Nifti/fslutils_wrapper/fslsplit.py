import subprocess

class fslsplit(object):

    def __init__(self, path='fslsplit', args_list=['-t']):
        self.args_list = args_list
        self.path = path

    def split(self, input_path, output_basename):
        args_list = [self.path, input_path, output_basename] + self.args_list
        output_code = subprocess.check_call(args_list, stdout=subprocess.PIPE)
        print "fslsplit return code {2} for input {0} output {1}".format(input_path, output_basename, output_code)
