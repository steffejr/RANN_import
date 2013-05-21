import nibabel as nib
import numpy as np

def getshape(input):
    ''''''
    II = nib.load(input)
    Data = np.array(II.get_data())
    return Data.shape
