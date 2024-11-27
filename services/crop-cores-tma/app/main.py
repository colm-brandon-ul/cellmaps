from dataclasses import dataclass
from enum import Enum

from cdb_cellmaps.data import DearrayedTissueMicroArray, RegionsOfInterest, TissueCore, TissueCoreProteinChannel, TissueMicroArray
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, DeArray

from image_utils import coordinate_translation #type: ignore


@dataclass
class CropCoresTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            dearrayed_tissue_micro_array: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class WorkflowParameters:
        rois: RegionsOfInterest

    @dataclass
    class Data:
        tissue_micro_array: TissueMicroArray

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class CropCoresTMAProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        dearrayed_tissue_micro_array: DearrayedTissueMicroArray
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success
    


class CropCoresTMA(DeArray,Automated):
    _ROUTING_KEY = 'CropCoresTMA'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> CropCoresTMAProcessInput:
        return data_utils.decode_dict(data_class=CropCoresTMAProcessInput,data=body)

        
    def process(self, prefix, input: CropCoresTMAProcessInput) -> CropCoresTMAProcessOutput:
        
        temp = DearrayedTissueMicroArray()
        
        
        for channel_name,channel in input.data.tissue_micro_array.items():
            # Load in full channel
            tiff = channel.read()

            # This will iterate correctly, but need to figure out how to retain type annotations for objects
            # being iterated over
            for i,roi in enumerate(input.workflow_parameters.rois):
                
                # Translate to coordinates from the image they were predicted/draw on to the full size image
                bounds = coordinate_translation(roi.img_w, 
                                             tiff.width, 
                                             roi.img_h, 
                                             tiff.height, 
                                             roi.x1,
                                             roi.y1,
                                             roi.x2,
                                             roi.y2)
                
                core_name = f'A{i}'
                if core_name not in temp.keys():
                    temp[core_name] = TissueCore()

                # Change Prefix
                temp[core_name][channel_name] = TissueCoreProteinChannel.write(
                    data=tiff.crop(bounds), 
                    prefix=prefix.add_level(
                        level=core_name),
                        file_name=channel_name
                        )

        return CropCoresTMAProcessOutput(
            data=CropCoresTMAProcessOutput.Data(
                dearrayed_tissue_micro_array=temp
            )
        )

if __name__ == "__main__":
    CropCoresTMA().run()