from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
import os
from typing import Any, List, Tuple, Optional
import requests

import tifffile #type: ignore

from cellmaps_sdk.data import MembraneMarkers, NuclearMarkers, NuclearStain, ProteinChannelMarker, ProteinChannelMarkers, WholeSlideImage, WholeSlideImageProteinChannel
from cellmaps_sdk import data_utils
from cellmaps_sdk.process import Automated, Interactive, Service, Start
# from cellmaps_sdk._utils import read_minio
from cellmaps_sdk._config import Config as _Config


if _Config.DEBUG() == False:
    from cellmaps_sdk._utils import download_stacked_tiff_locally
    from cellmaps_sdk._raw_data import RAW_WSI,read_raw_data,get_experiment_data_urls
else:
    from cellmaps_sdk._cli_utils import TestGenerator

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

@dataclass
class InitWSIPrepareTemplateInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            whole_slide_image: bool
            nuclear_stain: bool
            nuclear_markers: bool
            membrane_markers: bool
            protein_channel_markers: bool
        data_flow: DataFlow

    system_parameters: SystemParameters

@dataclass
class InitWSIPrepareTemplateOutput:
    html: str

@dataclass
class InitWSIProcessInput:
    @dataclass
    class WorkflowParameters:
        experiment_data_id: str
        nuclear_stain: Optional[NuclearStain]
        nuclear_markers: Optional[NuclearMarkers]
        membrane_markers: Optional[MembraneMarkers]
        
    workflow_parameters: WorkflowParameters

@dataclass
class InitWSIProcessOutput:
    @dataclass
    class WorkflowParameters:
        nuclear_stain: Optional[NuclearStain]
        nuclear_markers: Optional[NuclearMarkers]
        membrane_markers: Optional[MembraneMarkers]
        protein_channel_markers: ProteinChannelMarkers
    
    @dataclass
    class Data:
        whole_slide_image: WholeSlideImage

    class Control(str, Enum):
        success = 'success'

    data: Data
    workflow_parameters: WorkflowParameters
    control: Control = Control.success


class InitWSI(Start,Interactive):
    _ROUTING_KEY = 'InitWSI'
    _a = 'prepare-template'
    _b = 'process'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_prepare_template_input(self, body) -> InitWSIPrepareTemplateInput:
        return data_utils.decode_dict(data_class=InitWSIPrepareTemplateInput,data=body)


    def prepare_template(self, prefix, submit_url, input: InitWSIPrepareTemplateInput) -> InitWSIPrepareTemplateOutput:
        # read_minio
        if _Config.DEBUG() == False:
            # Get the experimental data, this reads the raw data from the minio, and returns a list of dictionaries
            experimental_data = read_raw_data(ExperimentClass = RAW_WSI())
        else:
            # Create mock experimental data (for testing purposes only)
            experimental_data = [
                {
                "experiment_name" : 'some_key',
                "tiff_name" : 'some_tiff_name',
                "channel_markers" : ['A0']
                }
            ]
        logging.warning(f"DEBUG: {experimental_data}")
        template = self.env.get_template("form-wsi.html")
        # This needs to be replaced


        return InitWSIPrepareTemplateOutput(
            html=template.render(endpoint=submit_url,  
                           experimentaldata=experimental_data,
                           inputSelection=asdict(input.system_parameters.data_flow)))

    

    def deserialize_process_input(self,body) -> InitWSIProcessInput:
        return data_utils.decode_dict(data_class=InitWSIProcessInput,data=body)
    
    def process(self, prefix, input: InitWSIProcessInput) -> InitWSIProcessOutput:
        protein_channel_markers = ProteinChannelMarkers()
        # Temporary Fix for methods which directly interact with the Minio -> Need to abstract this away
        if _Config.DEBUG() == False:
            # Based on the form selections / get the urls for the experiment data
                # the keys for these urls are defined in the RAW_WSI (each files cdb_file_tag)
            urls = get_experiment_data_urls(
                ExperimentClass=RAW_WSI(),
                prefix_name=input.workflow_parameters.experiment_data_id+'/',)


            # Save the Tiff stack locally
            large_tiff_local_dir  = download_stacked_tiff_locally(urls['tiff_name'])
            logging.warning(f"LOCAL NAME :{large_tiff_local_dir}")
        
            # Get & Parse Channel Markers txt file and add to points
            response = requests.get(urls['channel_markers'])

            # store as a list of ProteinChannelMarker objects
            for l in response.text.split('\n'):
                if l.rstrip() != '':
                    protein_channel_markers.append(ProteinChannelMarker(l.rstrip()))
        else:
            
            # Add mock protein channel markers
            protein_channel_markers.append(ProteinChannelMarker('A0'))
            # generate a mock tiff file
            import numpy as np
            large_tiff_local_dir = 'tf.ome.tiff'
            tifffile.imwrite(large_tiff_local_dir,np.array(TestGenerator.random_image_8bit()), compression='zlib')
            

        # Use tifffile to partially read the Tiff file
        tf = tifffile.TiffFile(large_tiff_local_dir)

        channel_shapes = []
        temp = WholeSlideImage()

        for i,p_chan in enumerate(protein_channel_markers):
            p_channel_tiff = tf.pages[i]
            channel_shapes.append(p_channel_tiff.shape)
            # Need to come up with a means of getting the prefix in
            temp[p_chan] = WholeSlideImageProteinChannel.write(
                Image.fromarray(p_channel_tiff.asarray()),
                prefix=prefix,
                image_name=p_chan)

        
        # Santity Check, ensure that all the protein channels written to the object storage are the same dimension
        assert len(set(channel_shapes)) == 1, 'Not all the selected Images are off the same Dimension, is the Marker List correct?'


        # Deleting the locally stored instance of the full size image
        tf.close()
        os.remove(large_tiff_local_dir)

        return InitWSIProcessOutput(
            data=InitWSIProcessOutput.Data(
                whole_slide_image=temp
            ),
            workflow_parameters=InitWSIProcessOutput.WorkflowParameters(
                nuclear_stain=input.workflow_parameters.nuclear_stain,
                nuclear_markers=input.workflow_parameters.nuclear_markers,
                membrane_markers=input.workflow_parameters.membrane_markers,
                protein_channel_markers= protein_channel_markers
            )
        )
    
if __name__ == "__main__":
    InitWSI().run()