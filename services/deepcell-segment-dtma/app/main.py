from dataclasses import dataclass
from enum import Enum

from cdb_cellmaps.data import DearrayedTissueMicroArray, DearrayedTissueMicroArrayCellSegmentationMask, MembraneMarkers, NuclearStain, TissueCore, TissueCoreCellSegmentationMask, TissueCoreMembraneSegmentationMask, TissueCoreNucleusSegmentationMask
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, CellSegmentation

import hippo_deepcell #type: ignore

import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

# dearrayed_tissue_micro_array,nuclear_stain,membrane_markers,

@dataclass
class DeepcellDTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            dearrayed_tissue_micro_array_cell_segmentation_masks: bool
        data_flow: DataFlow

    @dataclass
    class Data:
        dearrayed_tissue_micro_array: DearrayedTissueMicroArray

    @dataclass
    class WorkflowParameters:
        nuclear_stain: NuclearStain
        membrane_markers: MembraneMarkers

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class DeepcellDTMAProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        dearrayed_tissue_micro_array_cell_segmentation_masks: DearrayedTissueMicroArrayCellSegmentationMask
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class DeepcellDTMA(CellSegmentation,Automated):
    _ROUTING_KEY = 'DeepcellDTMA'
    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> DeepcellDTMAProcessInput:
        return data_utils.decode_dict(data_class=DeepcellDTMAProcessInput,data=body)

        
    def process(self, prefix, input: DeepcellDTMAProcessInput) -> DeepcellDTMAProcessOutput:
        # helper function
        def merge_membrane_channels(all_channels: TissueCore,markers: MembraneMarkers) -> Image.Image:
            # retrieve all the membrane marker images
            imgs =  [np.array(all_channels[mm].read()) for mm in markers]
            # Some method for merging these images
            img = Image.fromarray(np.mean(np.stack(imgs),axis=0).astype(np.uint8))
            return img

        temp = DearrayedTissueMicroArrayCellSegmentationMask()

        if len(input.workflow_parameters.membrane_markers) > 1:
            for core_name, core in input.data.dearrayed_tissue_micro_array.items():
                # try: 
                # Create Pseudo Membrane Marker
                membrane_stain = merge_membrane_channels(core,input.workflow_parameters.membrane_markers) 
                
                # Deepcell Segment
                nucleus_mask, membrane_mask = hippo_deepcell.segment_core(
                        core[input.workflow_parameters.nuclear_stain].read(),
                        membrane_stain
                    )
                
                
                temp[core_name] = TissueCoreCellSegmentationMask(
                    nucleus_mask=TissueCoreNucleusSegmentationMask.write(
                        data=nucleus_mask,
                        prefix=prefix.add_level(core_name),
                        file_name='nucleus_mask'),
                    membrane_mask=TissueCoreMembraneSegmentationMask.write(
                        data=membrane_mask,
                        prefix=prefix.add_level(core_name),
                        file_name='membrane_mask'),
                        )
                    
                # except Exception as e:
                #     logging.warning(f'{core_name} failed, because of: {e.with_traceback}')

        # Case when you don't have to create a pseudo-membrane-mask
        else:
            for core_name, core in input.data.dearrayed_tissue_micro_array.items():
                # try: 
                # Select First entry from len 1 list
                membrane_marker = input.workflow_parameters.membrane_markers[0]
                
                nucleus_mask, membrane_mask = hippo_deepcell.segment_core(
                        core[input.workflow_parameters.nuclear_stain].read(),
                        core[membrane_marker].read(),
                    )
                
                temp[core_name] = TissueCoreCellSegmentationMask(
                    nucleus_mask=TissueCoreNucleusSegmentationMask.write(
                        data=nucleus_mask,
                        prefix=prefix.add_level(core_name),
                        file_name='nucleus_mask'),
                    membrane_mask=TissueCoreMembraneSegmentationMask.write(
                        data=membrane_mask,
                        prefix=prefix.add_level(core_name),
                        file_name='membrane_mask'),
                        )
                    
                # except Exception as e:
                #     logging.warning(f'{core_name} failed, because of: {e.with_traceback}')
        
        return DeepcellDTMAProcessOutput(
            data=DeepcellDTMAProcessOutput.Data(
                dearrayed_tissue_micro_array_cell_segmentation_masks=temp
            )
        )

if __name__ == "__main__":
    DeepcellDTMA().run()