
import os
import functools
from glob import glob

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2 # Import the OpenCV library
#from memoization import cached

import os
import pickle

def cached(cachefile):
    """
    A function that creates a decorator which will use "cachefile" for caching the results of the decorated function "fn".
    """
    def decorator(fn):  # define a decorator for a function "fn"
        def wrapped(*args, **kwargs):   # define a wrapper that will finally call "fn" with all arguments   
            target_key = kwargs
            target_key = frozenset(target_key.items())
            print(target_key)   
            # if cache exists -> load it and return its content
            if os.path.exists(cachefile):
                    with open(cachefile, 'rb') as cachehandle:
                        print("using cached result from '%s'" % cachefile)
                        cache = pickle.load(cachehandle)
                        if target_key in cache:
                            return(cache[target_key])
            else:
                cache={}

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)
            cache[target_key] = res
            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                print("saving result to cache '%s'" % cachefile)
                pickle.dump(cache, cachehandle)

            return res

        return wrapped

    return decorator   # return this "customized" decorator that uses "cachefile"

class img_holes(object): 

    # instanciate object
    def __init__(self, img=None):
        self.img = img  

    # 4 - connected
    def boundaryDetect4(self, img_mask):
        """
        get a single chanel binary mask image and return the boundary pixels coordinates using 4 conected pixels strategy
        input: 
        img_mask - the mask of an image
        output:
        list of coordinates arrays ordered as [x,y]
        """
        b_list=[]
        cols, rows = img_mask.shape
        for y in range(cols-1):
            for x in range(rows-1):
                if img_mask[y,x]==0:
                    if img_mask[y,x+1]>0:
                        b_list.append([x,y])
                    elif img_mask[y,x-1]>0:
                        b_list.append([x,y])
                    elif img_mask[y+1,x]>0:
                        b_list.append([x,y])
                    elif img_mask[y-1,x]>0:
                        b_list.append([x,y])
        return(b_list)


    # 8 - connected
    def boundaryDetect8(self, img_mask):
        """
        get a single chanel binary mask image and return the boundary pixels coordinates using 8 conected pixels strategy
        input: 
        img_mask - the mask of an image
        output:
        list of coordinates arrays ordered as [x,y]
        """
        b_list=[]
        cols, rows = img_mask.shape
        for y in range(cols-1):
            for x in range(rows-1):
                if img_mask[y,x]==0:
                    if img_mask[y,x+1]>0:
                        b_list.append([x,y])
                    elif img_mask[y,x-1]>0:
                        b_list.append([x,y])
                    elif img_mask[y+1,x]>0:
                        b_list.append([x,y])
                    elif img_mask[y-1,x]>0:
                        b_list.append([x,y])
                    elif img_mask[y-1,x-1]>0:
                        b_list.append([x,y])
                    elif img_mask[y+1,x-1]>0:
                        b_list.append([x,y])
                    elif img_mask[y-1,x+1]>0:
                        b_list.append([x,y])
                    elif img_mask[y+1,x+1]>0:
                        b_list.append([x,y])
        return(b_list)
    
    def load_weight_conf(self, jsonPath):
        """
        load the weight configuration file from a JSON file
        input: JSON file full path
        output: dictionary with all configurations
        """
        import json

        f = open(jsonPath)
        weight_conf = json.load(f)
        return(weight_conf)

    @cached('defaultWeight_func_cache.pickle')
    def defaultWeight_func(self, v, u, **kwargs):
        """
        input:
        u - coordinate in hole
        v - coordinate in boundary
        z - integer factor 
        epsilon - small float value used to avoid division by 0
        output:
        wz - non-negative float weight
        """

        dist = np.linalg.norm(u-v)
        wz = 1.0/((dist**kwargs['z'])+kwargs['epsilon'])
        return(wz)


    def fillHole(self, b_coords, xy_coords, weightFunc, **kwargs):
        """
        inputs:
        xy_coords - the hole xy coordinates array
        b_coords  - the boundary xy coordinates array
        weightFunc - weight function to calculate the fill value
        **kwargs - weight configuration data for the weight function
        """
        for u in xy_coords:
            wz_iv_list = []
            wz_list = []
            for v in b_coords :
                vx=v[0]
                vy=v[1]
                iv = self.img[vy,vx]
                wz = weightFunc(v, u, **kwargs)
                wz_iv_list.append(wz*iv)
                wz_list.append(wz)
            
            iu = sum(wz_iv_list)/sum(wz_list)
            self.img[u[1],u[0]] = iu

        return(self.img)


class files_handler(object):
    # instanciate object
    def __init__(self, filepath, output_path, processed_extension='_filled'):
        self.filepath = filepath  
        self.output_path = output_path
        self.processed_extension = processed_extension

    """
    input:  
    - filepath - 
    - processed_extension - the expected extnsion for the processed files
    """

    def list_files(self, path=os.getcwd(), exclude_masks='no', mask_prefix='mask_', skipDuplicates=True):
        """
        get a path and list all the git/png/jpg files
        input: 
        path - full path to directory (default is current directory)
        exclude_masks - when 'yes' will not return any files which their prefix starts with the mask_prefix parameter. by default it is 'no' state
        mask_prefix - the prefix to filter mask files according to. by default it is 'mask'
        skipDuplicates - by default True, will skip processing files which already been processed and appears in the output directoy

        output:
        files_list - list of all the relevant files with their full paths
        fileNames_list - list of all the file names without extensions
        """

        # test if the path input is a file or directory
        if os.path.isdir(path) == True:
            files_list = glob(path +'/*.gif')
            files_list.extend(glob(path +'/*.png'))
            files_list.extend(glob(path +'/*.jpg'))
            
            # if skip duplicates is True
            if skipDuplicates == True:
                files_list = self.skipDuplicates(olist=files_list)

            fileNames_list=[os.path.basename(x).split('.')[0] for x in files_list]
            if exclude_masks == 'yes':
                files_list = list(filter(lambda x: not os.path.basename(x).startswith(mask_prefix), files_list))
                fileNames_list = list(filter(lambda x: not x.startswith(mask_prefix), fileNames_list))

            return(files_list, fileNames_list)

        elif os.path.isfile(path) == True:
            filename = os.path.basename(path)
            return(path, filename)

        else:
            raise Exception("File or path were not provided corectly!")

    def skipDuplicates(self, olist):
        """
        test if a file was processed already and exclude it from a list
        input:
        - olist - source images list with their full path
        output:
        - res_files_list - filtered list without the files which already been processed
        """
        # create list of named file
        processedFNames=[os.path.basename(x).split('.')[0] + self.processed_extension for x in olist]

        # list files names in the output path
        files_paths, namesList = self.list_files(path=self.output_path, skipDuplicates=False)
        diff_indices = [i for i, item in enumerate(processedFNames) if item not in set(namesList)]

        # slice original list by the new index
        res_files_list = [olist[i] for i in diff_indices] 

        removedItemscount = len(olist) - len(res_files_list)
        if removedItemscount > 0 :
            print(f"{removedItemscount} duplicated items were removed! \n")
        else:
            print("no duplicated items were found!\n")
        return(res_files_list)


    def getMaskFile(self, org_filepath, maskPath=None):
        """
        load the mask image under the assumption the name of the mask image is the same with additional prefix of "mask_imgName"
        input:
        - maskPath - (optional) - unique path to mask file directory
        output:
        - mask image as openCV object
        """

        org_path, org_fileName = self.list_files(path=org_filepath) # get the original image file name 
        mask_fileName = 'mask_'+ org_fileName.split('.')[0] # remove extension from file name and modify for mask version
        
        # when maskPath provided:
        if maskPath != None: 
            if os.path.isdir(maskPath) == True:
                files_paths, namesList = self.list_files(path=maskPath) # list files on the mask path 
                x = namesList.index(mask_fileName)
                maskFile = files_paths[x]
                mask = cv2.imread(maskFile, 0) # loading as grayscale image
                print("the file {0} was loaded".format(maskFile))
                return(mask)
            elif os.path.isfile(maskPath) == True:
                mask = cv2.imread(maskPath, 0) # direct loading as grayscale image
                return(mask)
            else:
                raise Exception("Maskpath parameters was not defined corectly")

        # when all masks files are stored together with original images     
        else: 
            files_paths, namesList = self.list_files(os.path.dirname(org_filepath))
            x = namesList.index(mask_fileName)
            maskFile = files_paths[x]
            mask = cv2.imread(maskFile, 0) # loading as grayscale image
            print("the file {0} was loaded".format(maskFile))
            return(mask)


    def load_image_return_array(self, maskPath=None):
        """
        Methods gets a path to a PNG or JPG image file 
        and returns an openCV image object
        input:
        - filepath - original image file path
        - maskPath - (optional) - unique path to mask file directory 
        output:
        - openCV original image object
        - openCV mask image object
        """

        # load the original image 
        img = cv2.imread(self.filepath)

        # load the mask image
        img_mask = self.getMaskFile(self.filepath, maskPath=maskPath)
        return(img, img_mask)