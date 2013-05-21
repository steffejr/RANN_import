import os
import gzip
import subprocess

def ungzipall(index):
    if (raw_input("Are you sure?: ") == 'YES'):
        for subject in index.subjectlist:
            for scan in subject.scanlist:
                for nifti in scan.niftilist:
                    if nifti.extension == 'nii.gz':
                        print "uncompressing %s" % nifti.path
                        f_in = gzip.open(nifti.path, 'rb');
                        f_out = open(os.path.join(scan.path, nifti.folder, nifti.basename + '.nii'), 'wb')
                        f_out.writelines(f_in)
                        f_out.close()
                        f_in.close()
                        if os.path.exists(os.path.join(scan.path, nifti.folder, nifti.basename + '.nii')):
                            os.unlink(nifti.path)


def set_permissions(path, DEBUG=False):
    "Sets 775 permissions and studydata group on directory"
    if not os.path.isdir(path):
        print "set_permissions was given an invalid path:{}\n".format(path)
        return
    if DEBUG:
        print "setting study permissions to 775 on {}....".format(path)
    subprocess.call("chmod -Rf 775 {}".format(path), shell=True)
    if DEBUG:
        print "setting study group to studydata on {}....".format(path)
    subprocess.call("chgrp -Rf studydata {}".format(path), shell=True)
