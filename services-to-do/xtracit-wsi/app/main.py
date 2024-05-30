from dataclasses import dataclass
from enum import Enum
import logging

from cellmaps_sdk.data import  NuclearMarkers, ProteinChannelMarkers, WholeSlideImage, WholeSlideImageCellSegmentationMask, WholeSlideImageMissileFCS
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, FeatureExtraction


import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

import to_tabular_format #type: ignore



# DTMA , CellSegmentationMASKS, Nuclear Markers

@dataclass
class XtracitWSIProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            whole_slide_image_missile_fcs: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class Data:
        whole_slide_image: WholeSlideImage
        whole_slide_image_cell_segmentation_mask: WholeSlideImageCellSegmentationMask
    @dataclass
    class WorkflowParameters:
        nuclear_markers: NuclearMarkers
        protein_channel_markers: ProteinChannelMarkers

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class XtracitWSIProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        whole_slide_image_missile_fcs: WholeSlideImageMissileFCS
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class XtracitWSI(FeatureExtraction,Automated):
    _ROUTING_KEY = 'XtracitWSI'
    _a = 'process'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> XtracitWSIProcessInput:
        return data_utils.decode_dict(data_class=XtracitWSIProcessInput,data=body)

        
    def process(self, prefix, input: XtracitWSIProcessInput) -> XtracitWSIProcessOutput:
        # What do with channel markers?
        membrane_channels = [c for c in input.workflow_parameters.protein_channel_markers if c not in input.workflow_parameters.nuclear_markers]

        try:
            membrane_mask = np.array(input.data.whole_slide_image_cell_segmentation_mask.membrane_mask.read())
            # Creating the membrane channel stack
            all_membrane_protein_channels = []

            for channel in membrane_channels:
                all_membrane_protein_channels.append(np.array(input.data.whole_slide_image[channel].read()))

            membrane_protein_channel_stack = np.stack(all_membrane_protein_channels,axis=2)

            # Fix prefixes
            membrane_df = to_tabular_format.extract_membrane_for_core(membrane_mask,
                                membrane_protein_channel_stack,
                                "A0",
                                membrane_channels)
            # Delete from memory
            del membrane_protein_channel_stack, membrane_mask

            nucleus_mask = np.array(input.data.whole_slide_image_cell_segmentation_mask.nucleus_mask.read())

            # Create nuclear channel stack
            all_nuclear_protein_channels = []
            for channel in input.workflow_parameters.nuclear_markers:
                all_nuclear_protein_channels.append(np.array(input.data.whole_slide_image[channel].read()))

            # W x H x NUMBER_OF_PROTEIN_CHANNELS 
            nuclear_protein_channel_stack = np.stack(all_nuclear_protein_channels,axis=2)

            nuclear_df = to_tabular_format.extract_nucelus_for_core(
                nucleus_mask,
                nuclear_protein_channel_stack,
                "A0",
                input.workflow_parameters.nuclear_markers)
            

            # delete from memory
            del nuclear_protein_channel_stack, nucleus_mask

            final_df = to_tabular_format.get_final_dataframe(membrane_df,nuclear_df)

            # Todo: fix prefix
            temp = WholeSlideImageMissileFCS.write(df = final_df,
                                                   prefix=prefix,
                                                    filename="AO")

        except Exception as e:
            
            logging.warning(f'WSI failed because of: {e.with_traceback}')

        
        return XtracitWSIProcessOutput(
            XtracitWSIProcessOutput.Data(
              whole_slide_image_missile_fcs=temp
            )
          
        )
    

if __name__ == '__main__':
    XtracitWSI().run()