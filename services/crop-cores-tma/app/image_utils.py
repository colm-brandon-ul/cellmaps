# For translating region of interest coordinates from UNET Image size, to Browser Image size to full resize image size
def coordinate_translation(src_img_w, des_img_w, src_img_h,des_img_h, x1,y1,x2,y2):
    scale_x, scale_y = des_img_w / src_img_w, des_img_h / src_img_h
    
    return (int(x1*scale_x), int(y1*scale_y), int(x2*scale_x), int(y2*scale_y))