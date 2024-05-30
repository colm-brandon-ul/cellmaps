# MissileExpressions, ProteinMarkers -> , MissileClusterPlotImage(s)

from dataclasses import dataclass
from enum import Enum
from typing import Any
import numpy as np
from PIL import Image

from cellmaps_sdk.data import MissileClusters, ProteinChannelMarkers,MissileExpressionCounts, Plot
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, Plotting


# Data Models

# https://rpy2.github.io/doc/v2.9.x/html/introduction.html


# Uses GGPLOT ->

@dataclass
class PlotExpressionValuesMissileProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            cluster_plot_images: bool
        # core_equalised_image_split_dir: str
        data_flow: DataFlow

    @dataclass
    class Data:
        missile_expression_counts: MissileExpressionCounts
        missile_clusters: MissileClusters 


    @dataclass
    class WorkflowParameters:
        protein_channel_markers: ProteinChannelMarkers

    @dataclass
    class ServiceParameters:
        threshold_percent: int  = 0
        transpose_plot: bool = False

    service_parameters: ServiceParameters
    workflow_parameters: WorkflowParameters
    system_parameters: SystemParameters
    data: Data


@dataclass
class PlotExpressionValuesMissileProcessOutput:
    class Control(str, Enum):
        success = 'success'

    @dataclass
    class Data:
        cluster_plot_images : Plot 
    # If there is no decision made in the Control set default to success
    data: Data
    control: Control = Control.success


class PlotExpressionValuesMissile(Plotting,Automated):
    _ROUTING_KEY = "PlotExpressionValuesMissile"

    def process(self, prefix, input: PlotExpressionValuesMissileProcessInput) -> PlotExpressionValuesMissileProcessOutput:
        
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
            b = ro.conversion.py2rpy(input.data.missile_clusters.read())

        # Call R Fuction
        mobj = rfuncs.BubblePlotMissile(
            a,
            b,
            ro.StrVector(input.workflow_parameters.protein_channel_markers.encode()), #Convert channel Markers to string vector
            input.service_parameters.transpose_plot,
            input.service_parameters.threshold_percent,
            # the other service parameters can be added retrospectively
        )
        
        
        # Implement R method using rpy2
        return PlotExpressionValuesMissileProcessOutput(
            data=PlotExpressionValuesMissileProcessOutput.Data(
                cluster_plot_images=Plot.write(
                    img = Image.fromarray((np.array(mobj)*255).astype(np.uint8), mode='RGB'), #Convert to PIL image
                    prefix=prefix,
                    image_name='bubble_plot_missile'
                )
            )
        )
    
    def deserialize_process_input(self, body) -> PlotExpressionValuesMissileProcessInput:
        return data_utils.decode_dict(data_class=PlotExpressionValuesMissileProcessInput,data=body)


if __name__ == '__main__':
    PlotExpressionValuesMissile().run()