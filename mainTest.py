import cv2 # Import the OpenCV library
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer

from fill_hole_funcs import *
from  cachingJson import cache_handler

start0 = timer() # tick start
update_cache = False

# single file test
myfile = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\test_hole.png'
# define the outputpath
outputPath = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\images\\filledImages'

processed_extension='_filled'
mask_prefix = 'mask_'

# load image & mask image
fh = files_handler(
    filepath=myfile, 
    output_path=outputPath,
    mask_prefix=mask_prefix,
    processed_extension = processed_extension
    )
image, mask = fh.load_image_return_array()

ih = img_holes(img=image)


# get the boudary coordinates using contour detection
b_coords = ih.boundaryDetect8(mask)

# get hole coordinates (x,y)
xy_coords = np.flip(np.column_stack(np.where(mask > 0)), axis=1)

# load the weight configuration data
jsonPath="weight_conf.json"
weight_conf = img_holes().load_weight_conf(jsonPath)

# fill the hole 
start = timer() # tick start
newImage, cache_dict =  ih.fillHole( b_coords = b_coords, xy_coords=xy_coords, weightFunc= ih.defaultWeight_func, **weight_conf)
end = timer() # tick end
print(end - start) # Time in seconds


if update_cache == True:
    # update cache
    ch = cache_handler('defaultWeight_func_cache.json')
    # load original copy of the cache
    org_cache = ch.load_cache()# loading cache from pickle file
    if org_cache != cache_dict:
        ch.store_cache_onDisk(loaded_cache=cache_dict)
        print("cache was updated!")

    end = timer() # tick end
    print(end - start0) # Time in seconds