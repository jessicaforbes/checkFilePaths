import os
import urllib
import datetime
import glob

class PathFinder():
    
    def __init__(self):
        self.inferred_filepath_list = list()
    
    def main(self):
        output_file = self.pullFromXNAT()
        all_images = self.getImageInfo(output_file)
        self.makeInferredFilePathList(all_images)
        self.createImagesNotInFileSystemFile()
        image_file_list = self.findPathsFromFileSystem()
        self.createImagesNotInXnatFile(image_file_list)
    
    def pullFromXNAT(self):
        RESTurl = "https://www.predict-hd.net/xnat/REST/custom/scans?type=(T1|T2|PD|PDT2)-(15|30)&format=csv"
        output_file = "filepaths_tmp.csv"
        urllib.urlretrieve(RESTurl, output_file)
        return output_file
    
    def getImageInfo(self, output_file):
        Handle = open(output_file)
        image_string = Handle.read()
        Handle.close()
        #os.remove(output_file)
        all_images = image_string.strip().replace("\"","").split('\n')
        return all_images[1:] ## header line not needed in the returned list
        
    def makeInferredFilePathList(self, all_images):
        for row in all_images:
            image_info = self.makeImageInfoDict(row)
            self.addImageFileToList(image_info)
        
    def makeImageInfoDict(self, row):
        row = row.strip().split(',')
        image_info = {'project':row[0],
                      'subject':row[2],
                      'session':row[4],
                      'scantype':row[8],
                      'seriesnumber':row[7]
                      }
        return image_info
    
    def addImageFileToList(self, image_info):
        PDT2_scantypes = ['PD-15','T2-15']
        if image_info['scantype'] != 'PDT2-15':
            self.inferFilePath(image_info)
        else:
            ## scan type 'PDT2-15' actually refers to two images: 'PD-15' and'T2-15'
            for scantype in PDT2_scantypes:
                image_info['scantype'] = scantype
                self.inferFilePath(image_info)
            
    def inferFilePath(self, image_info):        
        filepath = "/paulsen/MRx/{0}/{1}/{2}/ANONRAW/{1}_{2}_{3}_{4}.nii.gz".format(
            image_info['project'], image_info['subject'], image_info['session'],
            image_info['scantype'], image_info['seriesnumber'])
        self.inferred_filepath_list.append(filepath)
        
    def createImagesNotInFileSystemFile(self):
        path = "images_not_in_file_system.txt"
        Handle = open(path, 'wb')
        for filepath in self.inferred_filepath_list:
            if os.path.exists(filepath):
                continue
            else:
                Handle.write("{0}\n".format(filepath))
        Handle.close()
    
    def findPathsFromFileSystem(self):
        image_file_pat = '/paulsen/MRx/*/*/*/ANONRAW/*.nii.gz'
        image_file_list = glob.glob(image_file_pat)
        copy_image_file_list = list()
        copy_image_file_list.extend(image_file_list)
        for filepath in image_file_list:
            ## files in FMRI_COMPAT just point to files in fMRI_COMPAT
            if "FMRI_COMPAT" not in filepath:
                pass
            else:
                copy_image_file_list.remove(filepath)
        return copy_image_file_list
    
    def createImagesNotInXnatFile(self, image_file_list):
        path = "images_not_in_XNAT.txt"
        Handle = open(path, 'wb')
        for image in image_file_list:
            if image in self.inferred_filepath_list:
                continue
            else:
                Handle.write("{0}\n".format(image))
        Handle.close()  
    
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    Object = PathFinder()
    Object.main()
    print "-"*50
    print "The program took "
    print datetime.datetime.now() - start_time