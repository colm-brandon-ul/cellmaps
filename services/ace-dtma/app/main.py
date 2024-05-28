from dataclasses import  dataclass, field
from enum import Enum

from cellmaps_sdk.data import DearrayedTissueMicroArray, TissueCore, TissueCoreProteinChannel
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, TechnicalVarianceCorrection

import ace #type: ignore


@dataclass
class AceDTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            dearrayed_tissue_micro_array: bool
        data_flow: DataFlow
    @dataclass
    class Data:
        dearrayed_tissue_micro_array: DearrayedTissueMicroArray
    system_parameters: SystemParameters
    data: Data


@dataclass
class AceDTMAProcessOutput:
    class Control(str, Enum):
        success = 'success'
    @dataclass
    class Data:
        dearrayed_tissue_micro_array: DearrayedTissueMicroArray
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success
    

# Init Service Prefix / workflow id + service-name
class AceDTMA(TechnicalVarianceCorrection,Automated):
    _ROUTING_KEY = 'AceDTMA'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> AceDTMAProcessInput:
        return data_utils.decode_dict(data_class=AceDTMAProcessInput,data=body)

        
    def process(self, prefix, input: AceDTMAProcessInput) -> AceDTMAProcessOutput:
        
        temp = DearrayedTissueMicroArray()

        for core_name, core in input.data.dearrayed_tissue_micro_array.items():
            temp[core_name] = TissueCore()
            for channel_name, channel in core.items():
                new_im, thresholds = ace.fastACE(channel.read())
                # Need to correct the prefix-writing
                prefix # This is the workflow-id + service-name (& timestamp)
                temp[core_name][channel_name] = TissueCoreProteinChannel.write(
                    img = new_im,
                    prefix=prefix.add_level(core_name),
                    image_name=channel_name)
        
        return AceDTMAProcessOutput(
            data=AceDTMAProcessOutput.Data(
                dearrayed_tissue_micro_array=temp
            )
        )

if __name__ == '__main__':
    AceDTMA().run()