from dataclasses import dataclass
from enum import Enum
import json
import logging
import os
from typing import Any, List, Tuple, Optional

from cellmaps_sdk.data import _PNG as PNG, NuclearStain, PredictedROIs, ROIs, TissueMicroArray
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import DeArray, Interactive



from PIL import Image
Image.MAX_IMAGE_PIXELS = None


# What comes from the execution environment
@dataclass
class EditPredictedRoisTMAPrepareTemplateInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            rois: bool
        data_flow: DataFlow
    @dataclass
    class Data:
        tissue_micro_array: TissueMicroArray
    @dataclass
    class WorkflowParameters:
        nuclear_stain: NuclearStain
        predicted_rois: PredictedROIs
    
    workflow_parameters: WorkflowParameters
    data: Data
    system_parameters: SystemParameters

# The HTML Front end
@dataclass
class EditPredictedRoisTMAPrepareTemplateOutput:
    html: str

# What the user submits from the Interaction
@dataclass
class EditPredictedRoisTMAProcessInput:
    @dataclass
    class WorkflowParameters:
        rois: ROIs
        
    workflow_parameters: WorkflowParameters

# What is returned to the Execution Environment
@dataclass
class EditPredictedRoisTMAProcessOutput:
    @dataclass
    class WorkflowParameters:
        rois: ROIs

    class Control(str, Enum):
        success = 'success'

    # If there is no decision made in the Control set default to success
    workflow_parameters: WorkflowParameters
    control: Control = Control.success
    


class EditPredictedRoisTMA(DeArray,Interactive):
    _ROUTING_KEY = 'EditPredictedRoisTMA'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_prepare_template_input(self, body) -> EditPredictedRoisTMAPrepareTemplateInput:
        # Can this be abstract away?
        return data_utils.decode_dict(data_class=EditPredictedRoisTMAPrepareTemplateInput,data=body)


    def prepare_template(self, prefix, submit_url, input: EditPredictedRoisTMAPrepareTemplateInput) -> EditPredictedRoisTMAPrepareTemplateOutput:
        template = self.env.get_template("de_array_edit_predicted_rois.html")

        # Load Nuclear Stain Image
        nuclear_stain_img = input.data.tissue_micro_array[input.workflow_parameters.nuclear_stain].read()

        
        # Reduce the size of the raw image by 5x so it doesn't blow the browser !
        png = PNG.write(
            nuclear_stain_img.reduce(factor=5),
            prefix=prefix.add_level('browser-images'),
            image_name=input.workflow_parameters.nuclear_stain)
        
        
        return EditPredictedRoisTMAPrepareTemplateOutput(
            html=template.render(
                predicted_rois = input.workflow_parameters.predicted_rois.encode(),
                nuclear_stain_static = png.get_external_url(),
                endpoint=submit_url,
            ))
    

    

    def deserialize_process_input(self,body) -> EditPredictedRoisTMAProcessInput:
        return data_utils.decode_dict(data_class=EditPredictedRoisTMAProcessInput,data=body)

    def process(self, prefix, input: EditPredictedRoisTMAProcessInput) -> EditPredictedRoisTMAProcessOutput:


       
        return EditPredictedRoisTMAProcessOutput(
            workflow_parameters=EditPredictedRoisTMAProcessOutput.WorkflowParameters(
                rois=input.workflow_parameters.rois
            )
        )

    
if __name__ == '__main__':
    EditPredictedRoisTMA().run()