import subprocess

class fslview(object):

    def __init__(self, path='fslview', args_list=[]):
        self.args_list = [path] + args_list

    def view(self, input_images=[]):
        args_list = self.args_list + input_images
        output_code = subprocess.check_call(args_list, stdout=subprocess.PIPE)
        print "fslview return code {1} for inputs {0}".format('\n'.join(input_images), output_code)
