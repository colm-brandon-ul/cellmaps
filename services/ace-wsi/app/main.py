from dataclasses import dataclass
from enum import Enum

from cdb_cellmaps.data import WholeSlideImage, WholeSlideImageProteinChannel
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, TechnicalVarianceCorrection

import ace #type: ignore


@dataclass
class AceWSIProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            whole_slide_image: bool
        data_flow: DataFlow

    @dataclass
    class Data:
        whole_slide_image: WholeSlideImage

    system_parameters: SystemParameters
    data: Data


@dataclass
class AceWSIProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        whole_slide_image: WholeSlideImage
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success
    


class AceWSI(TechnicalVarianceCorrection,Automated):
    _ROUTING_KEY = 'AceWSI'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> AceWSIProcessInput:
        return data_utils.decode_dict(data_class=AceWSIProcessInput,data=body)

        
    def process(self, prefix, input: AceWSIProcessInput) -> AceWSIProcessOutput:
        
        temp = WholeSlideImage()

        for channel_name, channel in input.data.whole_slide_image.items():

            new_im, thresholds = ace.fastACE(channel.read())
            temp[channel_name] = WholeSlideImageProteinChannel.write(
                    data=new_im,
                    prefix=prefix,
                    file_name=channel_name)
        

        return AceWSIProcessOutput(
            data=AceWSIProcessOutput.Data(
                whole_slide_image=temp
            )
        )
    
if __name__ == '__main__':
    AceWSI().run()