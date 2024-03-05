# WholeSlideImageMissileFCS -> MissileExpressions, MissileMetaData
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cellmaps_sdk.data import  MissileClusters, MissileNeighbourhoods, Plot

from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, Plotting

from PIL import Image
import numpy as np

# https://rpy2.github.io/doc/v2.9.x/html/introduction.html

@dataclass
class PlotCellNeighbourhoodsHeatmapMissileProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            heatmap: bool
        data_flow: DataFlow

    @dataclass
    class Data:
        single_cell_clusters: MissileClusters
        single_cell_neighbourhoods: MissileNeighbourhoods

    # Will implement Service Parameters later
    system_parameters: SystemParameters
    data: Data


@dataclass
class PlotCellNeighbourhoodsHeatmapMissileProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        heatmap: Plot 
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class PlotCellNeighbourhoodsHeatmapMissile(Plotting,Automated):
    _ROUTING_KEY = "PlotCellNeighbourhoodsHeatmapMissile"
    def process(self, prefix, input: PlotCellNeighbourhoodsHeatmapMissileProcessInput) -> PlotCellNeighbourhoodsHeatmapMissileProcessOutput:
        
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
            a = ro.conversion.py2rpy(input.data.single_cell_clusters.read())
            b = ro.conversion.py2rpy(input.data.single_cell_neighbourhoods.read())

        # Call R Fuction
        mobj = rfuncs.neighbourhoodEnrichment(
            a,
            b,
        )
        

        # Implement R method using rpy2
        return PlotCellNeighbourhoodsHeatmapMissileProcessOutput(
            data=PlotCellNeighbourhoodsHeatmapMissileProcessOutput.Data(
                heatmap=Plot.write(
                    img = Image.fromarray(
                        (np.array(mobj)*255).astype(np.uint8), 
                        mode='RGB'), #Convert to PIL image
                    prefix=prefix,
                    image_name='cell_neighbourhoods_heatmap',
                )
            )
        )
    
    def deserialize_process_input(self, body) -> PlotCellNeighbourhoodsHeatmapMissileProcessInput:
        return data_utils.decode_dict(data_class=PlotCellNeighbourhoodsHeatmapMissileProcessInput,data=body)


if __name__ == '__main__':
    PlotCellNeighbourhoodsHeatmapMissile().run()