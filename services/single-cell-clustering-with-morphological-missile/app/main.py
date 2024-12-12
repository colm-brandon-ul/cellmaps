# ExpressionsMissile, MetaDataMissile, ProteinMarkers,WhichMetadata, K(number of neightbours) -> SingleCellPhenotypesMissile
# ExpressionsMissile, ProteinMarkers, K(number of neightbours) -> SingleCellPhenotypesMissile

from dataclasses import field, dataclass
from enum import Enum

from cdb_cellmaps.data import MissileExpressionCounts, MissileMetadata, ProteinChannelMarkers,MissileClusters
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Automated, Clustering

# Data Models


# https://rpy2.github.io/doc/v2.9.x/html/introduction.html

@dataclass
class SingleCellClusteringWithMorphologicalMissileProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            missile_clusters: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class Data:
        missile_expression_counts: MissileExpressionCounts
        missile_metadata: MissileMetadata
        

    @dataclass
    class WorkflowParameters:
        protein_channel_markers: ProteinChannelMarkers

    @dataclass 
    class ServiceParameters:
        numNeighbours: int = field(default=20,metadata={"max": 30, "min": 3})

    service_parameters: ServiceParameters = ServiceParameters()
    workflow_parameters: WorkflowParameters
    system_parameters: SystemParameters
    data: Data


@dataclass
class SingleCellClusteringWithMorphologicalMissileProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        missile_clusters: MissileClusters
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class SingleCellClusteringWithMorphologicalMissile(Clustering,Automated):
    _ROUTING_KEY = "SingleCellClusteringWithMorphologicalMissile"
    def process(self, prefix, input: SingleCellClusteringWithMorphologicalMissileProcessInput) -> SingleCellClusteringWithMorphologicalMissileProcessOutput:
        
         # Load R Functions in Python
        from rpy2.robjects.packages import STAP # type: ignore
        import rpy2.robjects as ro # type: ignore
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
            a = ro.conversion.py2rpy(input.data.missile_expression_counts.read())
            b = ro.conversion.py2rpy(input.data.missile_metadata.read())


        # Call R Fuction
        mobj = rfuncs.clusterMISSILeWithMetadata(
            a,
            b,
            ro.StrVector(input.workflow_parameters.protein_channel_markers.encode()),
            input.service_parameters.numNeighbours
        )

        with localconverter(ro.default_converter + pandas2ri.converter):
            c = ro.conversion.rpy2py(mobj)
        
        # Implement R method using rpy2
        return SingleCellClusteringWithMorphologicalMissileProcessOutput(
            data=SingleCellClusteringWithMorphologicalMissileProcessOutput.Data(
                missile_clusters=MissileClusters.write(
                    c,
                    prefix=prefix,
                    file_name='missile_clusters'
                )
            )
        )
    
    def deserialize_process_input(self, body) -> SingleCellClusteringWithMorphologicalMissileProcessInput:
        return data_utils.decode_dict(data_class=SingleCellClusteringWithMorphologicalMissileProcessInput,data=body)



if __name__ == "__main__":
    SingleCellClusteringWithMorphologicalMissile().run()    