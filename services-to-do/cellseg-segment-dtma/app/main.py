from dataclasses import dataclass
from enum import Enum
import logging

from cellmaps_sdk.data import DearrayedTissueMicroArray, DearrayedTissueMicroArrayCellSegmentationMask, NuclearStain, TissueCoreCellSegmentationMask, TissueCoreMembraneSegmentationMask, TissueCoreNucleusSegmentationMask
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, CellSegmentation

import hippo_cellseg #

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

@dataclass
class CellSegDTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            dearrayed_tissue_micro_array_cell_segmentation_masks: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class Data:
        dearrayed_tissue_micro_array: DearrayedTissueMicroArray

    @dataclass
    class WorkflowParameters:
        nuclear_stain: NuclearStain

    @dataclass
    class ServiceParameters:
        # class GrowMethod(str, Enum):
        #     Sequential = 'Sequential'
        overlap: int = 80
        threshold: int = 20
        increase_factor: int = 1
        grow_mask: bool = True
        grow_pixels: int = 10
        # grow_method: GrowMethod = GrowMethod.Sequential
        

    service_parameters: ServiceParameters
    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class CellSegDTMAProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        dearrayed_tissue_micro_array_cell_segmentation_masks: DearrayedTissueMicroArrayCellSegmentationMask
    # If there is no decision made in the Control set default to success

    data: Data
    control: Control = Control.success


class CellSegDTMA(CellSegmentation,Automated):
    _ROUTING_KEY = 'CellSegDTMA'
    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> CellSegDTMAProcessInput:
        return data_utils.decode_dict(data_class=CellSegDTMAProcessInput,data=body)

        
    def process(self, prefix, input: CellSegDTMAProcessInput) -> CellSegDTMAProcessOutput:
        temp = DearrayedTissueMicroArrayCellSegmentationMask()
        for core_name, core in input.data.dearrayed_tissue_micro_array.items():
            # try:
            nucleus_mask, membrane_mask = hippo_cellseg.segment_core(
                core[input.workflow_parameters.nuclear_stain].read(),
                overlap=input.service_parameters.overlap,
                threshold=input.service_parameters.threshold, 
                increase_factor=input.service_parameters.increase_factor, 
                grow_mask=input.service_parameters.grow_mask,
                grow_pixels=input.service_parameters.grow_pixels,
                grow_method='Sequential'
                )
                
            
            temp[core_name] = TissueCoreCellSegmentationMask(
                nucleus_mask=TissueCoreNucleusSegmentationMask.write(
                    img = nucleus_mask,
                    image_name= 'nucleus_mask',
                    prefix=prefix.add_level(core_name) 
                ),
                membrane_mask=TissueCoreMembraneSegmentationMask.write(
                    img = membrane_mask,
                    image_name= 'membrane_mask',
                    prefix=prefix.add_level(core_name) 
                )
            )
            # except Exception as e:
            #     logging.warning(f'{core_name} failed, because of: {e.with_traceback}')
        
        return CellSegDTMAProcessOutput(
            data=CellSegDTMAProcessOutput.Data(
                dearrayed_tissue_micro_array_cell_segmentation_masks=temp
            )
        )


if __name__ == "__main__":
    CellSegDTMA().run()