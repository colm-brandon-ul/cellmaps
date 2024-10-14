from typing import Union
from PIL import Image, TiffImagePlugin
Image.MAX_IMAGE_PIXELS = None
# from sklearn.multioutput import MultiOutputRegressor
# from sklearn.ensemble import RandomForestRegressor
import pickle
import numpy as np
from pathlib import Path
import os
this_dir, this_filename = os.path.split(__file__) 

# perhaps replace this with something such as skops to be more secure! \
    # https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
f = open(Path(this_dir)/ 'models' /'ace_clf.pkl','rb')
clf = pickle.load(f)


def fastACE(img: Union[Image.Image,TiffImagePlugin.TiffImageFile]):
    assert type(img) == TiffImagePlugin.TiffImageFile or type(img) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(img)}'
    # Get the histogram for the image
    im_hist = np.array(img.histogram())
    # Now normalize this histogram so it's agmnostic of the Image size
    im_hist = im_hist / im_hist.sum()
    # pass the normalized histogram through the classifer, reshaping as there's only 1 sample being passed in
    tmin, tmax = clf.predict(im_hist.reshape(1,-1))[0]
    # Using the predicted thresholds, apply the contrast function and return the adjusted Image 
    return contrast_function_8bit(img,int(tmin),int(tmax)), (int(tmin), int(tmax))


def contrast_function_8bit(img, min,max):
    assert type(img) == Image.Image or type(img) == TiffImagePlugin.TiffImageFile, f'Type {type(img)}, is not a valid input. Please convert image to a PIL.Image and retry'
    assert type(min) == int, 'min must be of type int'
    assert type(max) == int, 'max must be of type float'
    
    output_min, output_max = 0,255
    
    def rescale_pixel(px):
        if px <= min:
            return output_min
        elif px > max:
            return output_max
        else:
            return np.uint8((((px - min) / max) * output_max))
    
    vect_func = np.vectorize(rescale_pixel)
    
    return Image.fromarray(np.uint8(vect_func(np.array(img))))
         
