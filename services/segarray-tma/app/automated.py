"""
The handler function for the Images being passed into the trained segmentation model, generating the bounding boxes and subsquently slicing the images.
There will be two alternative functions - fully automated or automated with validation which will presented the found bounding boxes to the user for verifying they are correct and if not editing them.
"""
from PIL import Image, TiffImagePlugin
import torch
import unet
import cv2 
import numpy as np
from cellmaps_sdk.data import ROIs, PredictedROIs, ROIsPredictionWrapper, ROI

Image.MAX_IMAGE_PIXELS = None

UNET_INPUT_WIDTH = 1024
UNET_INPUT_HEIGHT = 1024
CONFIDENCE_THRESHOLDS = [0.5,0.7,0.9,0.99,0.999,0.9999,0.99999]


def unet_predict_mask(dapi):
    assert type(dapi) == TiffImagePlugin.TiffImageFile or type(dapi) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(dapi)}'
    # return the model (already on the device, GPU or CPU), plus the device
    model, device = unet.get_model()
    transformer = unet.get_transformer(UNET_INPUT_WIDTH,UNET_INPUT_HEIGHT)
    # Apply transformer to dapi Image
    dapi_tensor = transformer(dapi).to(device)
    
    
    with torch.no_grad():
        out = model(dapi_tensor.unsqueeze(0))
    
    mask = torch.sigmoid(out.squeeze()).cpu().numpy()
    
    # This returns a floating point mask / before it's been thresholded
    return mask

def get_gated_mask_by_confidence(mask, confidence_threshold):
    assert mask.dtype == np.float32, 'The mask must be a numpy array of type float32'
    
    gated_mask = (mask > confidence_threshold) * 255
    
    return gated_mask.astype(np.uint8)
    
    

def get_bounding_rects(mask):
    assert mask.dtype == np.uint8, 'The mask must be a numpy arrray of type uint8'
    # Thresholding image and finding external contours only
    ret, threshold = cv2.threshold(mask, 127,255,0)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    rects = []
    scores = []
    for cont in contours:
        x,y,w,h = cv2.boundingRect(cont)
        rects.append([x,y,x+w,y+h])
        scores.append(w*h)
    
    # Applying Non Maxmimum Supression, to eliminate boxes inside boxes
    new_rect_list = cv2.dnn.NMSBoxes(rects,scores,np.mean(scores) + np.std(scores),0.9)
    return [tuple(rects[nr]) for nr in new_rect_list]



def get_rois_unet(img) -> PredictedROIs:
    assert type(img) == TiffImagePlugin.TiffImageFile or type(img) == Image.Image, f'Please use a PIL.TiffImagePlugin.TiffImageFile, not {type(img)}'
    
    # Predict Mask
    mask = unet_predict_mask(img)
    # create semantic wrapper for the rois, conf values
    p_rois = PredictedROIs()

    # Iterate over the confidence thresholds
    for conf in CONFIDENCE_THRESHOLDS:
        # create semantic wrapper for the roi List
        temp_rois = ROIs()
        # Make prediction
        gated_mask = get_gated_mask_by_confidence(mask,conf)

        # Get ROIs for each Core
        for rect in get_bounding_rects(gated_mask):
            temp_rois.append(
                ROI(
                x1=rect[0],
                y1=rect[1],
                x2=rect[2],
                y2=rect[3],
                img_w=UNET_INPUT_WIDTH,
                img_h=UNET_INPUT_HEIGHT
            )
        )

        p_rois.append(ROIsPredictionWrapper(
            confidence_value=conf,
            rois=temp_rois
        ))
        

    return p_rois