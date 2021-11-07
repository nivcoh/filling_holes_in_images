import time
import os
from timeit import default_timer as timer
import numpy as np
import multiprocessing
from fill_hole_funcs import files_handler, img_holes
import cv2 # Import the OpenCV library

# CPU core count
cpu_count = multiprocessing.cpu_count()

def chunks(l, n):
    """
    creates cunks of list items.
    input: 
    l - list object
    n - number of items per list
    output:
    list of lists, in each list up to n items
    """
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


def process_image(myfile, name, weight_conf, outputPath, processed_extension='_filled'):
    # load image & mask image
    fh = files_handler(
        filepath=myfile, 
        output_path=outputPath,
        processed_extension = processed_extension
        )
    image, mask = fh.load_image_return_array()

    # get the boudary coordinates using contour detection
    ih = img_holes(img=image)
    b_coords = ih.boundaryDetect8(mask)

    # get hole coordinates (x,y)
    xy_coords = np.flip(np.column_stack(np.where(mask > 0)), axis=1)

    # fill the hole 
    newImage =  ih.fillHole( b_coords = b_coords, xy_coords=xy_coords, weightFunc= ih.defaultWeight_func, **weight_conf)

    # save the new filled image
    outputFileName = str(name + processed_extension + ".png")
    path = str(outputPath+"\\"+outputFileName)
    cv2.imwrite(path, newImage)
    print(f"new processed file was stored into: {path}")
    return(path)


if __name__ == '__main__':

    # load files 
    images_dir = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\images'
    # define the outputpath
    outputPath = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\images\\filledImages'

    fh = files_handler(
        filepath=images_dir, 
        output_path=outputPath)
    list_files, list_filesName = fh.list_files( path=images_dir, exclude_masks='yes')

    
    # set the number of files per chunk
    number_ofProcess = cpu_count - 2
    n = round(len(list_filesName)/number_ofProcess, 0)

    # load the weight configuration data
    jsonPath="weight_conf.json"
    weight_conf = img_holes().load_weight_conf(jsonPath)

    start_multi_time_v1 = time.time()
    # Start Multi Processing
    pool = multiprocessing.Pool(processes = cpu_count)

    # pack all needed arguments
    args2pass = []
    for i in list(zip(list_files, list_filesName)):
        args2pass.append(i + (weight_conf,outputPath))
    
    start = timer() # tick start
    res = pool.starmap(process_image, args2pass)

    pool.close()
    pool.join()
    end = timer() # tick end
    print(f"execution time was {end - start} seconds. \n {len(res)} items were processed!") # Time in seconds