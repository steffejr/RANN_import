import os


def is_nifti(filename):
    'takes a filename and checks if it is a nifti'
    extension = get_nifti_extension(filename)
    if extension == '.nii' or extension == '.nii.gz':
        return True
    return False

def get_nifti_extension(filename):
    filename_split = filename.split('.')
    if filename_split[-1].lower() == 'nii':
        return '.nii'
    elif len(filename_split) > 2 and filename_split[-2].lower() == 'nii' and filename_split[-1].lower() == 'gz':
        return '.nii.gz'
    return None

def get_nifti_basename(filename):
    filename_split = filename.split('.')
    if filename_split[-1].lower() == 'nii':
        return ".".join(filename_split[0:-1])
    elif len(filename_split) > 2 and filename_split[-2].lower() == 'nii' and filename_split[-1].lower() == 'gz':
        return ".".join(filename_split[0:-2])
    return None

def nifti_exists(basename):
    if os.path.exists(basename + ".nii") or os.path.exists(basename + ".nii.gz"):
        return True
    return False

def delete_nifti_by_basename(basename):
    if os.path.exists(basename + ".nii"):
        os.unlink(basename + ".nii")
    if os.path.exists(basename + ".nii.gz"):
        os.unlink(basename + ".nii.gz")

