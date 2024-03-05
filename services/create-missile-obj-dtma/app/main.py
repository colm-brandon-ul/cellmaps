# DearrayedTissueMicroArrayMissileFCS -> MissileExpressions, MissileMetaData
from dataclasses import dataclass
from enum import Enum
from typing import Any

from cellmaps_sdk.data import (DearrayedTissueMicroArrayMissileFCS, 
                  MissileExpressionCounts, MissileMetadata, 
                   MissileExpressionSpatialData, ProteinChannelMarkers)
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, DataTransformation
import os

# Libraries for interfacing between python and R environment

# Data Models


# https://rpy2.github.io/doc/v2.9.x/html/introduction.html

@dataclass
class CreateMissileObjectDTMAProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            missile_metadata: bool
            missile_counts: bool
            missile_spatial_data: bool

        data_flow: DataFlow

    @dataclass
    class Data:
        dearrayed_tissue_micro_array_missile_fcs: DearrayedTissueMicroArrayMissileFCS
    
    @dataclass
    class WorkflowParameters:
        protein_channel_markers: ProteinChannelMarkers

    system_parameters: SystemParameters
    workflow_parameters: WorkflowParameters
    data: Data


@dataclass
class CreateMissileObjectDTMAProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        missile_metadata: MissileMetadata
        missile_counts: MissileExpressionCounts
        missile_spatial_data: MissileExpressionSpatialData
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class CreateMissileObjectDTMA(DataTransformation,Automated):
    _ROUTING_KEY = "CreateMissileObjectDTMA"

    def process(self, prefix, input: CreateMissileObjectDTMAProcessInput) -> CreateMissileObjectDTMAProcessOutput:
        # Implement R method using rpy2

        # Load R Functions in Python
        from rpy2.robjects.packages import STAP # type: ignore
        import rpy2.robjects as ro # type: ignore
        from rpy2.robjects import pandas2ri # type: ignore
        from rpy2.robjects.conversion import localconverter # type: ignore

        # get current directory file path (so rfunc can be loaded when cwd is not app)
        import os
        from pathlib import Path
        current_file_path = os.path.abspath(__file__)
        current_directory = Path(os.path.dirname(current_file_path))

        with open(current_directory /'rfunc.r', 'r') as f:
            r_script = f.read()
        
        rfuncs = STAP(r_script, 'rfunc')
        
        # Read in MISSILE FCS list and conver to R DF
        with localconverter(ro.default_converter + pandas2ri.converter):
            rdfs_list = [ro.conversion.py2rpy(core.read()) for core in input.data.dearrayed_tissue_micro_array_missile_fcs.values()]

        marker_vector = ro.StrVector(input.workflow_parameters.protein_channel_markers.encode())
        

        mobj = rfuncs.createMISSILeTMA(
            rdfs_list,
            marker_vector
        )
        

        # raise Exception(mobj.do_slot('metadata'))


        with localconverter(ro.default_converter + pandas2ri.converter):
            a = ro.conversion.rpy2py(mobj.do_slot('counts'))
            b = ro.conversion.rpy2py(mobj.do_slot('spatialdata'))
            c = ro.conversion.rpy2py(mobj.do_slot('metadata'))

        return CreateMissileObjectDTMAProcessOutput(
            data=CreateMissileObjectDTMAProcessOutput.Data(
                missile_counts= MissileExpressionCounts.write(
                            df=a, # gets rdf and coverts to pandas
                            prefix=prefix,
                            filename='counts'
                        ),
                missile_spatial_data=MissileExpressionSpatialData.write(
                            df=b, # gets rdf and coverts to pandas
                            prefix=prefix,
                            filename='spatial_data'
                        ),
                missile_metadata= MissileMetadata.write(
                        df=c, # gets rdf and coverts to pandas
                        prefix=prefix,
                        filename='metadata' 
                    )
                )
            )
              
            
    
    def deserialize_process_input(self, body) -> CreateMissileObjectDTMAProcessInput:
        return data_utils.decode_dict(data_class=CreateMissileObjectDTMAProcessInput,data=body)

if __name__ == "__main__":
    CreateMissileObjectDTMA().run()