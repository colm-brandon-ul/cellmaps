from dataclasses import dataclass
from enum import Enum
import logging

from cdb_cellmaps.data import DearrayedTissueMicroArray, DearrayedTissueMicroArrayCellSegmentationMask, DearrayedTissueMicroArrayMissileFCS, NuclearMarkers, ProteinChannelMarkers, TissueCoreMissileFCS
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, FeatureExtraction


import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

from to_tabular_format import * #type: ignore



# DTMA , CellSegmentationMASKS, Nuclear Markers

@dataclass
class XtracitDTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            dearrayed_tissue_micro_array_missile_fcs: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class Data:
        dearrayed_tissue_micro_array: DearrayedTissueMicroArray
        dearrayed_tissue_micro_array_cell_segmentation_masks: DearrayedTissueMicroArrayCellSegmentationMask

    @dataclass
    class WorkflowParameters:
        nuclear_markers: NuclearMarkers
        protein_channel_markers: ProteinChannelMarkers

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class XtracitDTMAProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        dearrayed_tissue_micro_array_missile_fcs: DearrayedTissueMicroArrayMissileFCS
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success
    


class XtracitDTMA(FeatureExtraction,Automated):
    _ROUTING_KEY = 'XtracitDTMA'
    _a = 'process'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> XtracitDTMAProcessInput:
        return data_utils.decode_dict(data_class=XtracitDTMAProcessInput,data=body)

        
    def process(self, prefix, input: XtracitDTMAProcessInput) -> XtracitDTMAProcessOutput:
        # What do with channel markers?
        # Typing of this is wrong -> Need to fix it
        membrane_channels = [c for c in input.workflow_parameters.protein_channel_markers if c not in input.workflow_parameters.nuclear_markers]
        temp = DearrayedTissueMicroArrayMissileFCS()

        for core_name, core in input.data.dearrayed_tissue_micro_array.items():
            
               
            # Creating the membrane channel stack
            all_membrane_protein_channels = []

            for channel in membrane_channels:
                all_membrane_protein_channels.append(np.array(core[channel].read()))

            membrane_protein_channel_stack = np.stack(all_membrane_protein_channels,axis=2)
            membrane_mask = np.array(input.data.dearrayed_tissue_micro_array_cell_segmentation_masks[core_name].membrane_mask.read())

            membrane_df = extract_membrane_for_core(membrane_mask,
                                membrane_protein_channel_stack,
                                core_name,
                                membrane_channels)
            # Delete from memory
            del membrane_protein_channel_stack, membrane_mask

            nucleus_mask = np.array(input.data.dearrayed_tissue_micro_array_cell_segmentation_masks[core_name].nucleus_mask.read())

            # Create nuclear channel stack
            all_nuclear_protein_channels = []
            for channel in input.workflow_parameters.nuclear_markers:
                all_nuclear_protein_channels.append(np.array(core[channel].read()))
            
            # W x H x NUMBER_OF_PROTEIN_CHANNELS 
            nuclear_protein_channel_stack = np.stack(all_nuclear_protein_channels,axis=2)
            nuclear_df = extract_nucelus_for_core(
                nucleus_mask,
                nuclear_protein_channel_stack,
                core_name,
                input.workflow_parameters.nuclear_markers)
            

            # delete from memory
            del nuclear_protein_channel_stack, nucleus_mask

            final_df = get_final_dataframe(membrane_df,nuclear_df)

            # Todo: Correct Prefix
            temp[core_name] = TissueCoreMissileFCS.write(
                final_df,
                prefix=prefix,
                file_name=core_name,
            )

            

        
        return XtracitDTMAProcessOutput(
            XtracitDTMAProcessOutput.Data(
                dearrayed_tissue_micro_array_missile_fcs= temp
            )
          
        )
    
if __name__ == '__main__':
    XtracitDTMA().run()