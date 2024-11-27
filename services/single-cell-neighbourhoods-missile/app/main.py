# ExpressionsMissile, ProteinMarkers, K(k-means value) -> TissueArchitectureMissile


from dataclasses import field, dataclass
from enum import Enum
from typing import Any

from cdb_cellmaps.data import MissileNeighbourhoods, MissileMetadata, MissileClusters, MissileExpressionSpatialData
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, Clustering

# Libraries for interfacing between python and R environment
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector

# Data Models


# https://rpy2.github.io/doc/v2.9.x/html/introduction.html

@dataclass
class TissueArchitectureMissileProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            neighbourhoods: bool
        data_flow: DataFlow

    @dataclass
    class Data:
        missile_metadata: MissileMetadata
        missile_clusters: MissileClusters
        missile_spatial_data: MissileExpressionSpatialData


    @dataclass 
    class ServiceParameters:
        k: int = field(default=10, metadata={"max": 15, "min": 3})
        number_of_cells: int = field(default=10, metadata={"max": 15, "min": 3})

    service_parameters: ServiceParameters
    system_parameters: SystemParameters
    data: Data


@dataclass
class TissueArchitectureMissileProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        neighbourhoods: MissileNeighbourhoods
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class TissueArchitectureMissile(Clustering,Automated):
    _ROUTING_KEY = "TissueArchitectureMissile"

    def process(self, prefix, input: TissueArchitectureMissileProcessInput) -> TissueArchitectureMissileProcessOutput:
        # Load R Functions in Python
        from rpy2.robjects.packages import STAP # type: ignore
        import rpy2.robjects as ro # type: ignore
        from rpy2.robjects.vectors import StrVector #type: ignore
        from rpy2.robjects import pandas2ri # type: ignore
        from rpy2.robjects.conversion import localconverter # type: ignore
       # Load in R function
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
            a = ro.conversion.py2rpy(input.data.missile_metadata.read())
            b = ro.conversion.py2rpy(input.data.missile_clusters.read())
            c = ro.conversion.py2rpy(input.data.missile_spatial_data.read())

        # Call R Fuction
        mobj = rfuncs.cellNeighbourhoods(
            a,
            b,
            c,
            input.service_parameters.number_of_cells,
            input.service_parameters.k
        )

        
        
        with localconverter(ro.default_converter + pandas2ri.converter):
            d = ro.conversion.rpy2py(mobj)
        
        # Implement R method using rpy2
        return TissueArchitectureMissileProcessOutput(
            data=TissueArchitectureMissileProcessOutput.Data(
                neighbourhoods=MissileClusters.write(
                    df=d,
                    prefix=prefix,
                    filename='missile_neighbourhoods'
                )
            )
        )
    
    def deserialize_process_input(self, body) -> TissueArchitectureMissileProcessInput:
        return data_utils.decode_dict(data_class=TissueArchitectureMissileProcessInput,data=body)


if __name__ == '__main__':
    TissueArchitectureMissile().run()