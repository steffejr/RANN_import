import subprocess

class dcm2nii(object):

    def __init__(self, path='dcm2nii', args_list=['-a', 'N', '-d', 'N', '-e', 'N', '-g', 'Y', '-i', 'N', '-n', 'Y', '-p', 'N', '-m', 'N', '-r', 'N', '-v', 'Y', '-x', 'N']):
        self.args_list = [path] + args_list

    def recon(self, input_path, output_path, DEBUG=False):
        args_list = self.args_list + ['-o', output_path, input_path]
        #print " ".join(args_list)
        proc = subprocess.Popen(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        output_code = proc.returncode

        #subprocess.check_call(args_list)
        if DEBUG or output_code != 0:
            print "dcm2nii return code {2} for input {0} output {1}".format(input_path, output_path, output_code)
            print 'dcm2nii stdout:\n{}\n\ndcm2nii stderr:\n{}\n\n'.format(stdout, stderr)
