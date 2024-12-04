from deepcell_toolbox.utils import tile_image     
from deepcell_toolbox.utils import untile_image, erode_edges
from deepcell.applications import Mesmer
from skimage.measure import label, regionprops, regionprops_table
from scipy.ndimage import distance_transform_edt
from skimage.segmentation import expand_labels
import tensorflow as tf
import os


import pandas as pd
import numpy as np
# import sys

from PIL import Image,TiffImagePlugin
Image.MAX_IMAGE_PIXELS = None

MODEL_PATH = f'{os.path.dirname(os.path.abspath(__file__))}/MultiplexSegmentation'

def segment_core(nucelus_img, membrane_img):
    assert type(nucelus_img) == TiffImagePlugin.TiffImageFile or type(nucelus_img) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(nucelus_img)}'
    assert type(membrane_img) == TiffImagePlugin.TiffImageFile or type(membrane_img) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(membrane_img)}'
    # Loading the deepcell model
    app = Mesmer(tf.keras.models.load_model(MODEL_PATH))
    # Potentially make these as input variables
    TILE_SIZE = 256
    MICRONS_PER_PIX = 0.5
    ERODE_WIDTH = 1
    BATCH_SIZE = 4
    # Create array structure for segmentation model [1, ncol, nrow, nchannels]
    deepcell_input = np.expand_dims(np.stack([np.array(nucelus_img),np.array(membrane_img)],axis=2),axis=0)
    tiles,tile_info = tile_image(deepcell_input, model_input_shape=(TILE_SIZE,TILE_SIZE)) # is this the main issue for RAM? Make sure the image is uint8 so dtype within np.zeros is uint8
    segmentation_predictions = app.predict(tiles, image_mpp = MICRONS_PER_PIX, compartment = 'both', batch_size = BATCH_SIZE)
    #segmentation_eroded = segmentation_predictions # is this the best way to do this memory wise?
    for i in range(0,segmentation_predictions.shape[0]):
        segmentation_predictions[i,...,0] = erode_edges(segmentation_predictions[i,...,0], ERODE_WIDTH)
        segmentation_predictions[i,...,1] = erode_edges(segmentation_predictions[i,...,1], ERODE_WIDTH)
    segmentation_eroded_whole = untile_image(segmentation_predictions, tile_info)
    
    del segmentation_predictions, tile_info
    
    segmentation_eroded_whole[0,...,0][segmentation_eroded_whole[0,...,0] > 0] = 1
    segmentation_eroded_whole[0,...,1][segmentation_eroded_whole[0,...,1] > 0] = 1
    labeled_eroded = segmentation_eroded_whole
    #labeled_eroded[0,...,0] = label(segmentation_eroded_whole[0,...,0]) # membrane
    #labeled_eroded[0,...,1] = label(segmentation_eroded_whole[0,...,1]) # nucleus
    # This could simply be replaced by skimage.segmentation expand_labels
    labeled_eroded[0,...,0] = expandLabelsHIPPo(label(segmentation_eroded_whole[0,...,0]), distance = ERODE_WIDTH) # membrane
    labeled_eroded[0,...,1] = expandLabelsHIPPo(label(segmentation_eroded_whole[0,...,1]), distance = ERODE_WIDTH) # nucleus
    
    nucleus_mask, membrane_mask_precorrection = Image.fromarray(labeled_eroded[0,...,1].astype(np.uint32)), Image.fromarray(labeled_eroded[0,...,0].astype(np.uint32))
        
    # Return the Nucleus and the Corrected membrane mask
    return nucleus_mask, match_labels_and_correct(nucleus_mask,membrane_mask_precorrection)

        
def expandLabelsHIPPo(label_image, distance=1):
    # from scipy.ndimage import distance_transform_edt
    '''
    Parameters
    ----------
    label_image : TYPE
        DESCRIPTION.
    distance : TYPE, optional
        DESCRIPTION. The default is 1.
    Returns
    -------
    labels_out : TYPE
        DESCRIPTION.
    '''
    distances, nearest_label_coords = distance_transform_edt(
        label_image == 0, return_indices=True
    )
    labels_out = np.zeros_like(label_image)
    dilate_mask = distances <= distance
    # build the coordinates to find nearest label
    # in contrast to [1] this implementation supports label arrays
    # of any dimension
    masked_nearest_label_coords = [
        dimension_indices[dilate_mask]
        for dimension_indices in nearest_label_coords
    ]
    nearest_labels = label_image[tuple(masked_nearest_label_coords)]
    labels_out[dilate_mask] = nearest_labels
    return labels_out



def match_labels_and_correct(nucleus_mask, membrane_mask):
    assert type(nucleus_mask) == TiffImagePlugin.TiffImageFile or type(nucleus_mask) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(nucleus_mask)}'
    assert type(membrane_mask) == TiffImagePlugin.TiffImageFile or type(membrane_mask) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(membrane_mask)}'
    # Convert PIL image to np array
    nucleus_array = np.array(nucleus_mask,dtype=np.uint32)
    membrane_array = np.array(membrane_mask,dtype=np.uint32)
    # Get all the mask regions for both nucleus and membrane mask
    nuc_regions = regionprops(nucleus_array); nuc_region_dict = {nr.label: nr for nr in nuc_regions}
    mem_regions = regionprops(membrane_array); mem_regions_dict = {mr.label: mr for mr in mem_regions}
    
    # Creating blank arrays to copy membrane masks that are correct and incorrect into, Incorrect is defined as 1 membrane has > 1 nucleus who's maximum overlap is what that membrane
    blank_membrane = np.zeros(membrane_array.shape,np.uint32)
    blank_membrane_for_growth = np.zeros(membrane_array.shape,np.uint32)

    """
    How it works
    For a given Nucleus:
        Find the membrane it overlaps with the most
        For that membrane, find the nuclei it overlaps with
        For each of those nuclei - check if the membrane that it overlaps with most is the membrane
    """
    
    # Phase 1, find the nuceli / membrane mask mismatches
    
    for nuc_region in nuc_regions:
        try:
            # Get bounding box for the nucleus
            col1, row1, col2, row2 = nuc_region.bbox
            # Crop the section nucleus bounding box for both the nucleus and the membrane
            nuc_subsection_nuc = nucleus_array[col1:col2,row1:row2]
            mem_subsection_nuc = membrane_array[col1:col2,row1:row2]
            # Using the nucleus label as a gate, find the maximum membrane overlap and remove background counts
            mem_labels, mem_counts = np.unique(mem_subsection_nuc * (nuc_subsection_nuc == nuc_region.label),return_counts=True)
            zeros = np.where(mem_labels==0)[0]
            mem_labels, mem_counts = np.delete(mem_labels,zeros), np.delete(mem_counts, zeros)
            # The maximum overlap is the one with the highest count
            cm_id = mem_labels[np.argmax(mem_counts)]
            # Get the maximum overlap membrane bounding box and crop both the nucleus and the membrane
            cm = mem_regions_dict[cm_id]
            mcol1,mrow1,mcol2,mrow2 = cm.bbox
            nuc_subsection_mem = nucleus_array[mcol1:mcol2,mrow1:mrow2]
            mem_subsection_mem = membrane_array[mcol1:mcol2,mrow1:mrow2]
            # Get the set of nucleus labels
            nuc_labels,nuc_counts = np.unique(nuc_subsection_mem * (mem_subsection_mem == cm_id),return_counts=True)
            # Iterate over every nucleus label and find if the given membrane_id is the maximum overlap for it
            zeros = np.where(nuc_labels==0)[0]
            nuc_labels, nuc_counts = np.delete(nuc_labels, zeros), np.delete(nuc_counts, zeros)
            nuclei_matches = []
            for nuc in nuc_labels:
                if nuc != nuc_region.label:
                    cn = nuc_region_dict[nuc]
                    # Get nucleus region and crop
                    cncol1,cnrow1,cncol2,cnrow2 = cn.bbox
                    nuc_subsection_cn = nucleus_array[cncol1:cncol2,cnrow1:cnrow2]
                    mem_subsection_cn = membrane_array[cncol1:cncol2,cnrow1:cnrow2] 
                    
                    cn_labels, cn_counts = np.unique(mem_subsection_cn * (nuc_subsection_cn == nuc),return_counts=True)
                    zeros = np.where(cn_labels==0)[0]
                    cn_labels, cn_counts = np.delete(cn_labels,zeros), np.delete(cn_counts, zeros)
                    
                    cn_id = cn_labels[np.argmax(cn_counts)]
                    
                    nuclei_matches.append(cm_id == cn_id)
            
            # print(np.sum(nuclei_matches) > 0)
            
            cn_id = nuc_labels[np.argmax(nuc_counts)]
            
            # There is more than 1 nucleus, whos maximum overlap is with this membrane 
            if np.sum(nuclei_matches) > 0:
                # If the membrane doesn't have a clear nucleas counterpart, copy nucleus into mebrane mask for growth 
                # Gate the nucleus region so that it doesn't copy in irrelevant nuclei
                # += so that overlapping nucleus regions don't overwrite eachother
                blank_membrane_for_growth[col1:col2,row1:row2] += (nuc_subsection_nuc * (nuc_subsection_nuc == nuc_region.label)).astype(np.uint32)
            # Mask is valid
            else:
                blank_membrane[mcol1:mcol2,mrow1:mrow2] += (nuc_region.label * (mem_subsection_mem == cm_id)).astype(np.uint32)

        except Exception:
            # Where no mebrane mask is found - copy nucleus directly in to membrane mask for growth
            # print(e.with_traceback())
            col1, row1, col2, row2 = nuc_region.bbox
            nuc_subsection_nuc = nucleus_array[col1:col2,row1:row2]
            blank_membrane_for_growth[col1:col2,row1:row2] += (nuc_subsection_nuc * (nuc_subsection_nuc == nuc_region.label)).astype(np.uint32)
    
    # Taking the nuclei that have been correctly matches, find the mean growth between the nucleus and the membrane along the major and minor axis
    nucleus_with_membrane_df = pd.DataFrame(regionprops_table(nucleus_array * (blank_membrane_for_growth ==0),properties=['label','axis_major_length','axis_minor_length']))
    membrane_with_nucleus_df = pd.DataFrame(regionprops_table(blank_membrane,properties=['label','axis_major_length','axis_minor_length']))
    merged = nucleus_with_membrane_df.merge(membrane_with_nucleus_df,on='label')
    
    merged['expanded_minor'] = merged.axis_minor_length_y - merged.axis_minor_length_x
    merged['expanded_major'] = merged.axis_major_length_y - merged.axis_major_length_x
    merged['average_expanded'] = (merged.expanded_major+merged.expanded_minor) / 2
    
    # Get the mean distance, this will be the parameter for the mask dilation
    # If this return a NaN then simply set distance to zero
    try:
        distance = int(merged.average_expanded.mean())
    except:
        distance = 0
    
    expanded_mask = expand_labels(blank_membrane_for_growth, distance=distance)
    corrected_expanded = expanded_mask * (blank_membrane == 0)
    
    final_membrane_mask = blank_membrane + corrected_expanded
    
    
    return Image.fromarray(final_membrane_mask)
    


