# WholeSlideImageMissileFCS -> MissileExpressions, MissileMetaData
from dataclasses import dataclass
from enum import Enum

from cdb_cellmaps.data import WholeSlideImageMissileFCS, MissileMetadata,MissileExpressionCounts, MissileExpressionSpatialData,ProteinChannelMarkers

from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, DataTransformation



# https://rpy2.github.io/doc/v2.9.x/html/introduction.html

@dataclass
class CreateMissileObjectWSIProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            missile_metadata : bool
            missile_counts: bool
            missile_spatial_data: bool
        data_flow: DataFlow

    @dataclass
    class WorkflowParameters:
        protein_channel_markers: ProteinChannelMarkers

    @dataclass
    class Data:
        whole_slide_image_missile_fcs: WholeSlideImageMissileFCS

    workflow_parameters: WorkflowParameters
    system_parameters: SystemParameters
    data: Data


@dataclass
class CreateMissileObjectWSIProcessOutput:
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


class CreateMissileObjectWSI(DataTransformation,Automated):
    _ROUTING_KEY = "CreateMissileObjectWSI"
    def process(self, prefix, input: CreateMissileObjectWSIProcessInput) -> CreateMissileObjectWSIProcessOutput:
        
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
        # Load in R function
        with open(current_directory / 'rfunc.r', 'r') as f:
            r_script = f.read()
        rfuncs = STAP(r_script, 'rfunc')
        
        with localconverter(ro.default_converter + pandas2ri.converter):
            df = ro.conversion.py2rpy(input.data.whole_slide_image_missile_fcs.read()) 

        # Call R Fuction
        mobj = rfuncs.createMISSILeWSI(
            df,
            ro.StrVector(input.workflow_parameters.protein_channel_markers.encode()) #Convert channel Markers to string vector
        )

        with localconverter(ro.default_converter + pandas2ri.converter):
            a = ro.conversion.rpy2py(mobj.do_slot('counts'))
            b = ro.conversion.rpy2py(mobj.do_slot('spatialdata'))
            c = ro.conversion.rpy2py(mobj.do_slot('metadata'))
        

        # Implement R method using rpy2
        return CreateMissileObjectWSIProcessOutput(
            data=CreateMissileObjectWSIProcessOutput.Data(
                missile_counts= MissileExpressionCounts.write(
                            a, # gets rdf and coverts to pandas
                            prefix=prefix,
                            file_name='counts'
                        ),
                missile_spatial_data=MissileExpressionSpatialData.write(
                            b, # gets rdf and coverts to pandas
                            prefix=prefix,
                            file_name='spatial_data'
                        ),
                missile_metadata= MissileMetadata.write(
                        c, # gets rdf and coverts to pandas
                        prefix=prefix,
                        file_name='meta_data' 
                    )
                )
            )
    
    def deserialize_process_input(self, body) -> CreateMissileObjectWSIProcessInput:
        return data_utils.decode_dict(data_class=CreateMissileObjectWSIProcessInput,data=body)


if __name__ == "__main__":
    CreateMissileObjectWSI().run()