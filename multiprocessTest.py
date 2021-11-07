import time
import os
import sys

from timeit import default_timer as timer
import numpy as np
import multiprocessing
import cv2 # Import the OpenCV library

from fill_hole_funcs import files_handler, img_holes
from  cachingPickle import cache_handler

# CPU core count
cpu_count = multiprocessing.cpu_count()

start0 = timer() # tick start

# configuring caching mode:
update_cache = False
cache_mode = False
ch = cache_handler('defaultWeight_func_cache.pickle', cache_mode=cache_mode)


#images_dir = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\images'
#outputPath = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\images\\filledImages'
#mask_prefix = 'mask_'
#jsonPath="weight_conf.json"




def process_image(imgfile, name, weight_conf, outputPath, mask_prefix='mask_', processed_extension='_filled'):
    """
    a function to process a single image / list of images

    Args:
        imgfile - a single file path or a list 
        name - a single file name or a list without extensions of the files
        weight_conf - weight function configuration dictionary
        outputPath - full path to where should processed file be stored
        mask_prefix - prefix for the masked version of the imgfile, used to locate masks
        processed_extension - extensions to the end of the original name (imgfile) after being processed

    Returns:
        path - path to the processed file
        cache_dict - updated caching dictionary (in caching mode only)
    """
    # load image & mask image
    fh = files_handler(
        filepath=imgfile, 
        output_path=outputPath,
        mask_prefix=mask_prefix,
        processed_extension=processed_extension
        )
    image, mask = fh.load_image_return_array()

    # get the boudary coordinates using contour detection
    ih = img_holes(img=image)
    b_coords = ih.boundaryDetect8(mask)

    # get hole coordinates (x,y)
    xy_coords = np.flip(np.column_stack(np.where(mask > 0)), axis=1)

    # fill the hole 
    newImage, cache_dict =  ih.fillHole( b_coords = b_coords, xy_coords=xy_coords, weightFunc= ih.defaultWeight_func, **weight_conf)

    # save the new filled image
    outputFileName = str(name + processed_extension + ".png")
    path = str(outputPath+"\\"+outputFileName)
    cv2.imwrite(path, newImage)
    
    print(f"new processed file was stored into: {path}")
    return(path, cache_dict)




if __name__ == '__main__':

    print('######################################')
    print("Initiating hole filler CLI\n")

    # parse system arguments:
    print(sys.argv)
    try:
        # a list of the arguments provided 
        images_dir = sys.argv[1]  # set the path to the image or images
        mask_prefix = sys.argv[2] # defines the masked files prefix
        outputPath = sys.argv[3] # define the outputpath
        jsonPath = sys.argv[4] # configuration json file for the weight function
        
    except:
        raise Exception(f"Something went wrong! provided arguments: {list(sys.argv)} \n please check your argument!")
        sys.exit(1)

    # instansiate a file handler object
    fh = files_handler(
        filepath=images_dir, 
        output_path=outputPath,
        mask_prefix=mask_prefix)
    # list all the files
    list_files, list_filesName = fh.list_files( path=images_dir, exclude_masks='yes', skipDuplicates=True) 
    if len(list_files)==0:
        print('no files were left to process!')
        sys.exit(0) # exit process without errors
    
    print(f"there are {len(list_files)} files to process...\n")

    # set the number of processes to use 
    avilable_cpu = cpu_count - 2
    files_to_process = len(list_files)
    if files_to_process <= avilable_cpu:
        number_ofProcess = files_to_process
    else:
        number_ofProcess = avilable_cpu

    # set the number of files per chunk 
    n = round(len(list_filesName)/number_ofProcess, 0)

    # load the weight configuration data
    weight_conf = img_holes().load_weight_conf(jsonPath)

    start_multi_time_v1 = time.time()
    print(f"start multi-processing with {number_ofProcess} processes... \n")
    # Start Multi Processing
    pool = multiprocessing.Pool(processes = number_ofProcess)

    # pack all needed arguments
    args2pass = []
    for i in list(zip(list_files, list_filesName)):
        args2pass.append(i + (weight_conf,outputPath))
    
    start = timer() # tick start

    res=[]
    cache_dict={}
    for temp_res, res_cache_dict in  pool.starmap(process_image, args2pass):
        res.append(temp_res)
        cache_dict.update(res_cache_dict)
    

    pool.close()
    pool.join()
    end = timer() # tick end
    print(f"execution time was {end - start} seconds. \n {len(res)} items were processed!") # Time in seconds

    # cache update
    if ((update_cache == True)&(cache_mode==True)):
        print('updating cache, might take a while...\n')
        # update cache
        ch = cache_handler('defaultWeight_func_cache.pickle')
        # load original copy of the cache
        org_cache = ch.load_cache()# loading cache from pickle file
        if org_cache != cache_dict:
            ch.store_cache_onDisk(loaded_cache=cache_dict)
            print("cache was updated!")

    end = timer() # tick end
    print(end - start0) # Time in seconds