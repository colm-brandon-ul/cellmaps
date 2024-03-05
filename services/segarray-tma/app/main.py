from dataclasses import dataclass
from enum import Enum

from cellmaps_sdk.data import NuclearStain, TissueMicroArray, PredictedROIs, TissueMicroArrayProteinChannel
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, DeArray

import automated #type: ignore

@dataclass
class SegArrayTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            predicted_rois: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class WorkflowParameters:
        nuclear_stain: NuclearStain

    @dataclass
    class Data:
        tissue_micro_array: TissueMicroArray

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class SegArrayTMAProcessOutput:

    @dataclass
    class WorkflowParameters:
        predicted_rois: PredictedROIs
    
    class Control(str, Enum):
        success = 'success'
    

    # If there is no decision made in the Control set default to success
    workflow_parameters: WorkflowParameters
    control: Control = Control.success
    


class SegArrayTMA(DeArray,Automated):
    _ROUTING_KEY = 'SegArrayTMA'
    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> SegArrayTMAProcessInput:
        return data_utils.decode_dict(data_class=SegArrayTMAProcessInput,data=body)

        
    def process(self, prefix, input: SegArrayTMAProcessInput) -> SegArrayTMAProcessOutput:

        # PredictedROIs - need to import automated and set it to return a PredictedROIs object
        return SegArrayTMAProcessOutput(
            workflow_parameters=SegArrayTMAProcessOutput.WorkflowParameters(
                predicted_rois=automated.get_rois_unet(TissueMicroArrayProteinChannel.read(
                    input.data.tissue_micro_array[
                        input.workflow_parameters.nuclear_stain]
                    )
                )
            )
        )

if __name__ == '__main__':
    SegArrayTMA().run()