#!/usr/bin/env python
# encoding: utf-8
"""
region_extractor.py
This scripts extracts any anatomical region from the labeled image

Created by Ray Razlighi on 2010-09-08.
Expanded by Aleksey Orekhov on 7/24/2012
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import nibabel as nb
import numpy as np
from path import is_nifti

def main(Input_FileName,Output_FileName,Label_Intensities=[]):
	
	
	# load the files
	Input_FileHandle = nb.load(InputFileName)
	Nifti_Affine = Input_FileHandle.get_affine()	
	Nifti_Shape = np.array(Input_FileHandle.get_shape(), int)
	Data = np.array(Input_FileHandle.get_data(), np.int32)
	Data = Data.flatten()
	
	for i in xrange(np.size(Data)):
		
		if Data[i] in Label:
			Data[i] = 1
		else:
			Data[i] = 0
			
	print('Writing the output file in' + Output_FileName)
	Data = Data.reshape(Nifti_Shape)
	Output_Nifti_FileHandle = nb.Nifti1Image(Data, Nifti_Affine)
	Output_Nifti_FileHandle.to_filename(Output_FileName)

	


if __name__ == '__main__':
	Usage='Usage: region_extractor.py <labeled_image> <-p prefix> [Labels of Region]\nEx:\n region_extractor.py -p frontal_lobe test.nii.gz 3 4 7\n\nWill extract regions with values 3 4 7 from test.nii.gz and output them into frontal_lobe_test.nii.gz with values of 1 (zero elsewhere)'

	if len(sys.argv) <= 4 or not is_nifti(Input_FileName):
		print Usage
	   	sys.exit(1)

	if sys.argv[2] != '-p' and sys.argv[2] != '-prefix':
		print Usage
	   	sys.exit(1)
	else:
		prefix=sys.argv[3]

	try:
		Label_Intensities = [int(x) for x in sys.argv[4:]]
	except:
		print Usage
	   	sys.exit(1)

	if not 	is_nifti(Input_FileName):
		print "Input File must by .nii or .nii.gz"
		print Usage
		sys.exit(1)

	OutputFileName = prefix+'_'+InputFileName
	get_nifti_basename(Input_FileName)
	main(Input_FileName,Output_FileName,Label_Intensities)





