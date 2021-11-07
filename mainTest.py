import cv2 # Import the OpenCV library
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer

from fill_hole_funcs import *

# single file test
myfile = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\test_hole.png'
# define the outputpath
outputPath = 'c:\\gitHub\\Learning_and_Training\\filling_holes_in_images\\images\\filledImages'

def load_weight_conf(jsonPath):
    """
    load the weight configuration file from a JSON file
    input: JSON file full path
    output: dictionary with all configurations
    """
    import json
    f = open(jsonPath)
    weight_conf = json.load(f)

    return(weight_conf)

# load image & mask image
fh = files_handler(
    filepath=myfile, 
    output_path=outputPath
    )

ih = img_holes(img=image)

image, mask = fh.load_image_return_array()

# get the boudary coordinates using contour detection
b_coords = ih.boundaryDetect8(mask)

# get hole coordinates (x,y)
xy_coords = np.flip(np.column_stack(np.where(mask > 0)), axis=1)

# load the weight configuration data
jsonPath="weight_conf.json"
weight_conf = load_weight_conf(jsonPath)

# fill the hole 
start = timer() # tick start
newImage =  ih.fillHole( b_coords = b_coords, xy_coords=xy_coords, weightFunc= ih.defaultWeight_func, **weight_conf)
end = timer() # tick end
print(end - start) # Time in seconds