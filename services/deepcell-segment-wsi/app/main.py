from dataclasses import dataclass
from enum import Enum
import logging

from cdb_cellmaps.data import  MembraneMarkers, NuclearStain, WholeSlideImage, WholeSlideImageCellSegmentationMask, WholeSlideImageMembraneSegmentationMask, WholeSlideImageNucleusSegmentationMask
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, CellSegmentation

import hippo_deepcell #type: ignore

import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

@dataclass
class DeepcellWSIProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            whole_slide_image_cell_segmentation_masks: bool
        data_flow: DataFlow

    @dataclass
    class Data:
        whole_slide_image: WholeSlideImage

    @dataclass
    class WorkflowParameters:
        nuclear_stain: NuclearStain
        membrane_markers: MembraneMarkers

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class DeepcellWSIProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        whole_slide_image_cell_segmentation_masks: WholeSlideImageCellSegmentationMask
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success



class DeepcellWSI(CellSegmentation,Automated):
    _ROUTING_KEY = 'DeepcellWSI'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> DeepcellWSIProcessInput:
        return data_utils.decode_dict(data_class=DeepcellWSIProcessInput,data=body)

        
    def process(self, prefix, input: DeepcellWSIProcessInput) -> DeepcellWSIProcessOutput:
        # helper function
        def merge_membrane_channels(all_channels: WholeSlideImage, markers: MembraneMarkers) -> Image.Image:
            
            # retrieve all the membrane marker images
            imgs =  [np.array(all_channels[mm].read()) for mm in markers]
            
            # Some method for merging these images
            img = Image.fromarray(np.mean(np.stack(imgs),axis=0).astype(np.uint8))
            
            return img


        

        if len(input.workflow_parameters.membrane_markers) > 1:
            membrane_stain = merge_membrane_channels(
                input.data.whole_slide_image,
                input.workflow_parameters.membrane_markers) 
                
            # Deepcell Segment
            nucleus_mask, membrane_mask = hippo_deepcell.segment_core(
                    input.data.whole_slide_image[input.workflow_parameters.nuclear_stain].read(),
                    membrane_stain
                )
            
            # Write masks to disk
            temp = WholeSlideImageCellSegmentationMask(
                nucleus_mask= WholeSlideImageNucleusSegmentationMask.write(data=nucleus_mask,
                                                                            prefix=prefix,
                                                                            file_name='nucleus_mask'),

                membrane_mask=WholeSlideImageMembraneSegmentationMask.write(data=membrane_mask,
                                                                            prefix=prefix,
                                                                            file_name='membrane_mask')
            )

            

        # Case when you don't have to create a pseudo-membrane-mask
        else:
            membrane_marker = input.workflow_parameters.membrane_markers[0]

            # Deepcell Segment
            nucleus_mask, membrane_mask = hippo_deepcell.segment_core(
                    input.data.whole_slide_image[input.workflow_parameters.nuclear_stain].read(),
                    input.data.whole_slide_image[membrane_marker].read()
                )

            # Write masks to disk
            temp = WholeSlideImageCellSegmentationMask(
                nucleus_mask= WholeSlideImageNucleusSegmentationMask.write(data=nucleus_mask,
                                                                            prefix=prefix,
                                                                            file_name='nucleus_mask'),

                membrane_mask=WholeSlideImageMembraneSegmentationMask.write(data=membrane_mask,
                                                                            prefix=prefix,
                                                                            file_name='membrane_mask')
            )

            
        
        return DeepcellWSIProcessOutput(
            data=DeepcellWSIProcessOutput.Data(
                whole_slide_image_cell_segmentation_masks=temp
            )
        )
    
if __name__ == '__main__':
    DeepcellWSI().run()