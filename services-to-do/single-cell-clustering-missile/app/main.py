# ExpressionsMissile, ProteinMarkers, K(number of neightbours) ->   

from dataclasses import field, dataclass
from enum import Enum
from typing import Any

from cellmaps_sdk.data import ProteinChannelMarkers,MissileExpressionCounts, MissileClusters
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, Clustering


# Data Models
# https://rpy2.github.io/doc/v2.9.x/html/introduction.html

@dataclass
class SingleCellClusteringMissileProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            missile_clusters: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class Data:
        missile_expressions_counts: MissileExpressionCounts

    @dataclass
    class WorkflowParameters:
        protein_channel_markers: ProteinChannelMarkers

    @dataclass 
    class ServiceParameters:
        numNeighbours: int = field(default=20,metadata={"max": 30, "min": 3})

    service_parameters: ServiceParameters
    workflow_parameters: WorkflowParameters
    system_parameters: SystemParameters
    data: Data


@dataclass
class SingleCellClusteringMissileProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        missile_clusters: MissileClusters
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


# Service Definition
class SingleCellClusteringMissile(Clustering,Automated):
    _ROUTING_KEY = "SingleCellClusteringMissile"
    def process(self, prefix, input: SingleCellClusteringMissileProcessInput) -> SingleCellClusteringMissileProcessOutput:
        

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

        # Read in MISSILE FCS list and conver to R DF
        with localconverter(ro.default_converter + pandas2ri.converter):
            a = ro.conversion.py2rpy(input.data.missile_expressions_counts.read())

        # Call R Fuction
        mobj = rfuncs.clusterMISSILe(
            a,
            ro.StrVector(input.workflow_parameters.protein_channel_markers.encode()) #Convert channel Markers to string vector
        )

        with localconverter(ro.default_converter + pandas2ri.converter):
            b = ro.conversion.rpy2py(mobj)
        

        
        # Implement R method using rpy2
        return SingleCellClusteringMissileProcessOutput(
            data=SingleCellClusteringMissileProcessOutput.Data(
                missile_clusters=MissileClusters.write(
                    df=b,
                    prefix=prefix,
                    filename='missile_clusters'
                )
            )
        )
    
    def deserialize_process_input(self, body) -> SingleCellClusteringMissileProcessInput:
        return data_utils.decode_dict(data_class=SingleCellClusteringMissileProcessInput,data=body)


if __name__ == '__main__':
    SingleCellClusteringMissile().run()