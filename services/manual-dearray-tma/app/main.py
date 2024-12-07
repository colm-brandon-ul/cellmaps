from dataclasses import dataclass
from enum import Enum

from cdb_cellmaps.data import PNG as PNG, NuclearStain, RegionsOfInterest, TissueMicroArray
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import DeArray, Interactive



from PIL import Image
Image.MAX_IMAGE_PIXELS = None


# What comes from the execution environment
@dataclass
class ManualDearrayTMAPrepareTemplateInput:
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
    
    workflow_parameters: WorkflowParameters
    data: Data
    system_parameters: SystemParameters

# The HTML Front end
@dataclass
class ManualDearrayTMAPrepareTemplateOutput:
    html: str

# What the user submits from the Interaction
@dataclass
class ManualDearrayTMAProcessInput:
    @dataclass
    class WorkflowParameters:
        rois: RegionsOfInterest
        
    workflow_parameters: WorkflowParameters

# What is returned to the Execution Environment
@dataclass
class ManualDearrayTMAProcessOutput:
    @dataclass
    class WorkflowParameters:
        rois: RegionsOfInterest

    class Control(str, Enum):
        success = 'success'

    # If there is no decision made in the Control set default to success
    workflow_parameters: WorkflowParameters
    control: Control = Control.success
    


class ManualDearrayTMA(DeArray,Interactive):
    _ROUTING_KEY = 'ManualDearrayTMA'
    def __init__(self) -> None:
        super().__init__()

    def deserialize_prepare_template_input(self, body) -> ManualDearrayTMAPrepareTemplateInput:
        # Can this be abstract away?
        return data_utils.decode_dict(data_class=ManualDearrayTMAPrepareTemplateInput,data=body)


    def prepare_template(self, prefix, submit_url, input: ManualDearrayTMAPrepareTemplateInput) -> ManualDearrayTMAPrepareTemplateOutput:
        template = self.env.get_template("de_array_manual.html")

        # Load Nuclear Stain Image
        nuclear_stain_img = input.data.tissue_micro_array[input.workflow_parameters.nuclear_stain].read()

        
        # Reduce the size of the raw image by 5x so it doesn't blow the browser !
        png = PNG.write(
            nuclear_stain_img.reduce(factor=5),
            prefix=prefix.add_level('browser-images'),
            file_name=input.workflow_parameters.nuclear_stain)
        
        import logging  
        logging.warning(f"PNG: {png.url}")
        
        
        return ManualDearrayTMAPrepareTemplateOutput(
            html=template.render(
                nuclear_stain_static = png.get_external_url(),
                endpoint=submit_url,
            ))
    
    

    def deserialize_process_input(self,body) -> ManualDearrayTMAProcessInput:
        return data_utils.decode_dict(data_class=ManualDearrayTMAProcessInput,data=body)

    def process(self, prefix, input: ManualDearrayTMAProcessInput) -> ManualDearrayTMAProcessOutput:
       
        return ManualDearrayTMAProcessOutput(
            workflow_parameters=ManualDearrayTMAProcessOutput.WorkflowParameters(
                rois=input.workflow_parameters.rois
            )
        )

if __name__ == '__main__':
    ManualDearrayTMA().run()