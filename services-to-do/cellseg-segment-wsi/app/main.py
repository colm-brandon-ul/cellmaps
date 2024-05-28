from dataclasses import dataclass
from enum import Enum
import logging

from cellmaps_sdk.data import NuclearStain, WholeSlideImage, WholeSlideImageCellSegmentationMask, WholeSlideImageMembraneSegmentationMask, WholeSlideImageNucleusSegmentationMask
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, CellSegmentation

import hippo_cellseg #type: ignore

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

# dearrayed_tissue_micro_array,nuclear_stain,membrane_markers,

@dataclass
class CellSegWSIProcessInput:
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

    @dataclass
    class ServiceParameters:
        class GrowMethod(str, Enum):
            Sequential = 'Sequential'
        overlap: int = 80
        threshold: int = 20
        increase_factor: int = 1
        grow_mask: bool = True
        grow_pixels: int = 10
        grow_method: GrowMethod = GrowMethod.Sequential
        

    service_parameters: ServiceParameters
    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class CellSegWSIProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        whole_slide_image_cell_segmentation_masks: WholeSlideImageCellSegmentationMask
    # If there is no decision made in the Control set default to success

    data: Data
    control: Control = Control.success


class CellSegWSI(CellSegmentation,Automated):
    _ROUTING_KEY = 'CellSegWSI'
    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> CellSegWSIProcessInput:
        return data_utils.decode_dict(data_class=CellSegWSIProcessInput,data=body)

        
    def process(self, prefix, input: CellSegWSIProcessInput) -> CellSegWSIProcessOutput:
        try:
            nucleus_mask, membrane_mask = hippo_cellseg.segment_core(
                    input.data.whole_slide_image[input.workflow_parameters.nuclear_stain].read(),
                    overlap=input.service_parameters.overlap,
                    threshold=input.service_parameters.threshold, 
                    increase_factor=input.service_parameters.increase_factor, 
                    grow_mask=input.service_parameters.grow_mask,
                    grow_pixels=input.service_parameters.grow_pixels,
                    grow_method=input.service_parameters.grow_method
                    )
            
            wsi = WholeSlideImageCellSegmentationMask(
                nucleus_mask=WholeSlideImageNucleusSegmentationMask.write(
                        img = nucleus_mask,
                        image_name= 'nucleus_mask',
                        prefix=prefix
                    ),
                membrane_mask=WholeSlideImageMembraneSegmentationMask.write(
                        img = membrane_mask,
                        image_name= 'membrane_mask',
                        prefix=prefix
                    ),
            )
        except Exception as e:
            logging.warning(f'WSI failed, because of: {e.with_traceback}')
        
        return CellSegWSIProcessOutput(
            data=CellSegWSIProcessOutput.Data(
                whole_slide_image_cell_segmentation_masks=wsi
            )
        )



if __name__ == '__main__':
    CellSegWSI().run()