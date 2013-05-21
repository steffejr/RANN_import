import os
import shutil #for file copying
import string
import warnings
from collections import defaultdict

from ManageStudyErrors import VisitErrors
from Nifti.Image import Image as NIfTIImage
from DICOM.Image import Image as DICOMImage
from Nifti.NiftiTools.path import is_nifti


class Visit(object):

    def __init__(self, subject, visid):
        self.subject = subject
        self.visid = visid
        self.path = os.path.join(self.subject.path, visid)
        if not os.path.exists(self.path):
            os.makedirs(self.path, 0775)
        self.niftilist = []
        self.niftis = defaultdict(dict)
        self.__checkdirs__()
        self.findNIfTIData()
        self.dicomlist = []
        self.dicoms = {}
        self.findDICOMData()


    def __checkdirs__(self):
        self.logdir = os.path.join(self.path, 'logs')
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        Quarantine = os.path.join(self.path, 'Quarantine')
        if not os.path.exists(Quarantine):
            os.makedirs(Quarantine)


    def findNIfTIData(self):
        'Returns a list of visit objects at the subject dir, favors nii.gz over nii files and will delete the nii if both nii and nii.gz present'

        try:
            Files = os.listdir(self.path)
        except:
            warnings.warn("\nCould not list files in: " + self.path)
            return

        Files = [folder for folder in Files if folder not in self.subject.index.config.__ignoredirlist__]
        self.niftilist = []
        self.niftis = defaultdict(dict)

        for folder in Files:
            folderdir = os.path.join(self.path, folder)
            if (not os.path.isdir(folderdir)):
                continue
            try:
                seriesfiles = os.listdir(folderdir)
            except:
                warnings.warn("\nCould not list files in: " + folderdir)
                return

            for seriesfile in seriesfiles:
                fullseriespath = os.path.join(folderdir, seriesfile)
                if (not os.path.isfile(fullseriespath)):
                    continue
                self.check_add_nifti(folder, seriesfile)


    def check_add_nifti(self, folder, filename):
        '''
        Adds Nifti with specified folder and filename if it is not already present. Deletes .nii file if .nii.gz file found
        with same basename
        '''
        if is_nifti(filename):
            newimage = NIfTIImage(self, folder=folder, filename=filename)
            if self.check_image_REC(newimage.basename, folder):
                if (newimage.series not in self.niftis[folder]):
                    self.niftilist.append(newimage)
                    self.niftis[folder][newimage.series] = newimage
                elif newimage.extension == 'nii.gz' : #remove non nii.gz files
                    print "favoring with nii.gz over nii {}".format(self.niftis[folder][newimage.series].path)
                    self.removeNii(self.niftis[folder][newimage.series])
                    self.niftilist.append(newimage)
                    self.niftis[folder][newimage.series] = newimage
                else:
                    print "favoring with nii.gz over nii {}".format(newimage.path)
                    self.unlinknii(newimage.path)
            else:
                fullseriespath = os.path.join(self.path, folder, filename)
                self.subject.index.nonconformingniilist.append(fullseriespath)

    def check_image_REC(self, name, folder=''):
        '''
        checks if folder has subd_visid in it's name.
        '''
        if folder != '':
            folder = os.path.sep + folder
        if name.find(self.subject.subid + '_' + self.visid) == -1:
            print "{0} did not match {1} in {2}".format(name, self.subject.subid + '_' + self.visid, self.path + folder)
            return False
        return True


    def add_nifti_by_full_path(self, path):
        '''
        Runs self.check_add_nifti on nifti pointed to by path if it is in a folder of this visit. Convenience wrapper
        '''
        image_path = os.path.normpath(path)
        (rest, filename) = os.path.split(image_path)
        (rest, folder) = os.path.split(rest)
        if rest == self.path:
            self.check_add_nifti(folder, filename)

    def image_path(self, folder, series, extension=''):
        '''returns full path to image when given folder, series, and extension'''
        return os.path.join(self.path, folder, self.image_basename(series)) + extension

    def image_basename(self, series):
        return "{0}_{1.subject.subid}_{1.visid}".format(series, self)

    def findDICOMData(self):
        'Returns a list of visit objects at the subject dir'

        self.dicomdir = os.path.join(self.path, 'DICOM')
        if not os.path.exists(self.dicomdir):
            os.makedirs(self.dicomdir)

        self.dicomlist = []
        self.dicoms = {}

        dicomdir = os.path.join(self.path, 'DICOM')
        try:
            folders = os.listdir(dicomdir)
        except:
            warnings.warn("\nCould not list files in: " + dicomdir)
            return

        for folder in folders:
            full_path = os.path.join(dicomdir, folder)
            if (not os.path.isdir(full_path)):
                continue
            elif self.check_image_REC(folder):
                newimage = DICOMImage(self, folder='DICOM', filename=folder)
                self.dicomlist.append(newimage)
                self.dicoms[newimage.series] = newimage
            else:
                self.subject.index.nonconformingdicomlist.append(full_path)



    #===========================================================================
    # Utility Methods
    #===========================================================================

    def importNii(self, niftilocation, folder, series, override=False):
        '''Imports *.nii file into current visit's source folder
        folder => T1,T2,PET,CT
        series => V1,V2,PET,CT,Sternberg,etc'''

        #check niftilocation to make sure file is nii
        locationsplit = string.split(os.path.basename(os.path.normpath(niftilocation)), '.')
        if len(locationsplit) < 2:
            raise VisitErrors.UnknownFileException(niftilocation, locationsplit, "niftilocation: nifti filename is too short:: length is %d:: %g Too Short!" % (len(locationsplit)))
        if locationsplit[1].lower() != 'nii':
            raise VisitErrors.ImportNiiError(niftilocation, description="File is not a nii")

        #make destination dir if needed
        destdir = os.path.join(self.path, folder)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        filename = self.image_basename(series) + '.' + '.'.join(locationsplit[1:])
        destfile = os.path.join(destdir, filename)
        print "\nSOURCEFILE::::" + niftilocation
        print "DESTFILE::::" + destfile
        if (override == True) or not os.path.exists(destfile):
            shutil.copyfile(niftilocation, destfile)
            newimage = NIfTIImage(self, folder=folder, filename=filename)
            self.niftilist.append(newimage)
            self.niftis[folder][series] = newimage
            return True
        else:
            raise VisitErrors.ImportNiiError(niftilocation, destfile, "File exists and override False")
            return False

    #TODO RENAME!!! #MAKE OVERRIDE ACTUALLY WORK
    def removeSeries(self, folder, series, override=False):
        '''
        Removes all Nii Files matching folder and series
        for the given visit
        '''
        matchfound = False
        newimagelist = []
        for image in self.niftilist:
            if image.folder == folder and image.series == series:
                matchfound = True
                self.removeNii(image, override)
        if not matchfound:
            raise VisitErrors.DeleteNiiError(niiname=image.path, description="No matching Images found")
        self.niftilist = newimagelist


    def removeNii(self, badnifti, override=False):
        '''
        Removes all nifti file corresponding to nifti object
        '''
        matchfound = False
        newimagelist = []
        for image in self.niftilist:
            if image.path == badnifti.path:
                matchfound = True
                if not image.unlink(override):
                    newimagelist.append(image)
                    self.niftis[image.folder][image.series] = image
            else:
                newimagelist.append(image)
                self.niftis[image.folder][image.series] = image
        if not matchfound:
            badnifti.unlink(override)
            return False
        self.niftilist = newimagelist
        return True

    #now ONLY taking series objects
    def importDICOM(self, dicomlocation, series_info, override=False):
        #make dicom image dir if needed
        dicom_dir = os.path.join(self.path, 'DICOM')
        image_name = self.image_basename(series_info.series)
        dest_image = os.path.join(dicom_dir, image_name)
        if not os.path.exists(dest_image):
            print "Making dir {0!s}".format(dest_image)
            os.makedirs(dest_image)
            newimage = DICOMImage(self, folder='DICOM', filename=image_name)
            self.dicomlist.append(newimage)
            self.dicoms[series_info.series] = newimage

        image = self.dicoms[series_info.series]
        return image.importDICOM(dicomlocation, series_info, override)
        #make series folder, if needed

    def __str__(self):
        outstring = 'visit: {}'.format(self.visid)
        nifti_text = '\n\t'.join([x.__str__().replace('\n', '\n\t') for x in self.niftilist])
        dicom_text = '\n\t'.join([x.__str__().replace('\n', '\n\t') for x in self.dicomlist])
        return outstring + '\n\t' + nifti_text + '\n\t' + dicom_text


    def __str_concise__(self):
        outstring = '#Niftis: {1:04d}\t#Series: {2:04d}\tvisit: {0} '.format(self.visid, len(self.niftilist), len(self.dicomlist))
        return outstring
