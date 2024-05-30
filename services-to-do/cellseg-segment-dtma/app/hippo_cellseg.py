from src.cvsegmenter import CVSegmenter
from src.cvstitch import CVMaskStitcher
from src.cvmask import CVMask
import numpy as np
from PIL import Image,TiffImagePlugin
import os
Image.MAX_IMAGE_PIXELS = None

# Path to the weights file


PATH_TO_WEIGHTS = f"{os.path.dirname(os.path.abspath(__file__))}/src/modelFiles/final_weights.h5"

def segment_core(nucelus_img, overlap=80, threshold=20, increase_factor=1, grow_mask=True, grow_pixels=10, grow_method='Sequential'):
    assert type(nucelus_img) == TiffImagePlugin.TiffImageFile or type(nucelus_img) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(nucelus_img)}'
    # Converting PIL Image to np, and expanding dimensions
    nucleus_array = np.expand_dims(np.array(nucelus_img,dtype=np.uint8),axis=2)
    
    # Initialising Image Sticher and Segmentation Model
    stitcher = CVMaskStitcher(overlap=overlap)
    model = CVSegmenter(
        nucleus_array.shape,
        model_path=PATH_TO_WEIGHTS,
        overlap=overlap,
        increase_factor=increase_factor,
        threshold=threshold
    )
    
    
    rows, cols = None,None
    masks, rows, cols = model.segment_image(nucleus_array)
    intermediate_mask = stitcher.stitch_masks(masks,rows,cols)
    stitched_mask = CVMask(intermediate_mask)
    nucleus_mask = stitched_mask.flatmasks

    # Return the Nucleus and Membrane Masks,
    return Image.fromarray(nucleus_mask.astype(np.uint32)), grow_mask_with_pad(nucelus_mask=nucleus_mask, grow_pixels=grow_pixels, grow_method=grow_method)
    

def grow_mask_with_pad(nucelus_mask,grow_pixels=10, grow_method='Sequential'):
    # assert type(nucelus_img) == TiffImagePlugin.TiffImageFile or type(nucelus_img) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(nucelus_img)}'
    # Convert input to correct type if necceary
    if type(nucelus_mask) == TiffImagePlugin.TiffImageFile or type(nucelus_mask) == Image.Image:
        # If image is format PIL image, convert to np.array and then to CVMask
        nucelus_mask = CVMask(np.array(nucelus_mask,dtype=np.uint32))
    elif type(nucelus_mask) == np.ndarray:
        # If type is np.array, convert to CVMask
        nucelus_mask = CVMask(nucelus_mask)
        
    nucelus_mask.compute_centroids()
    nucelus_mask.compute_boundbox()
    nucelus_mask.grow_masks(growth=grow_pixels, method=grow_method)
    
    membrane_mask = nucelus_mask.flatmasks
    # xPad = nucleus_array.shape[0] - membrane_mask.shape[0]
    # yPad = nucleus_array.shape[1] - membrane_mask.shape[1]
    # membrane_mask = np.pad(membrane_mask, [(0, xPad), (0, yPad)], mode='constant')
    
    return Image.fromarray(membrane_mask.astype(np.uint32))
    