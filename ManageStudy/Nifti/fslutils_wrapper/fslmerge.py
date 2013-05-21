import subprocess

class fslmerge(object):

    def __init__(self, path='fslmerge', args_list=['-t']):
        self.args_list = [path] + args_list

    def merge(self, output_path, input_list):
        args_list = self.args_list + [output_path] + input_list
        output_code = subprocess.check_call(args_list, stdout=subprocess.PIPE)
        print "merge return code {2} for output {0} inputs:\n {1}".format(output_path, '\n'.join(input_list), output_code)
