from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
from typing import Optional
import requests

import tifffile #type: ignore

from cdb_cellmaps.data import MembraneMarkers, NuclearMarkers, NuclearStain, ProteinChannelMarker, ProteinChannelMarkers, TissueMicroArray, TissueMicroArrayProteinChannel
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import Interactive, Start
from cdb_cellmaps._config import Config as _Config

from PIL import Image
Image.MAX_IMAGE_PIXELS = None



if _Config.DEBUG() == False:
    # from hippo.data_management import data_management #type: ignore
    from cdb_cellmaps._utils import download_stacked_tiff_locally
    from cdb_cellmaps._raw_data import RAW_TMA,read_raw_data,get_experiment_data_urls
else:
    import numpy as np
    from cdb_cellmaps._cli_utils import TestGenerator



# What comes from the execution environment
@dataclass
class InitTMAPrepareTemplateInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            tissue_micro_array: bool
            nuclear_stain: bool
            nuclear_markers: bool
            membrane_markers: bool
            protein_channel_markers: bool
        data_flow: DataFlow
    system_parameters: SystemParameters

# The HTML Front end
@dataclass
class InitTMAPrepareTemplateOutput:
    html: str

# What the user submits from the Interaction
@dataclass
class InitTMAProcessInput:
    @dataclass
    class WorkflowParameters:
        experiment_data_id: str
        nuclear_stain: Optional[NuclearStain]
        nuclear_markers: Optional[NuclearMarkers]
        membrane_markers: Optional[MembraneMarkers]
        protein_channel_markers: ProteinChannelMarkers
        
        
    workflow_parameters: WorkflowParameters

# What is returned to the Execution Environment
@dataclass
class InitTMAProcessOutput:
    @dataclass
    class WorkflowParameters:
        nuclear_stain: Optional[NuclearStain]
        nuclear_markers: Optional[NuclearMarkers]
        membrane_markers: Optional[MembraneMarkers]
        protein_channel_markers: ProteinChannelMarkers
    
    @dataclass
    class Data:
        tissue_micro_array: TissueMicroArray

    class Control(str, Enum):
        success = 'success'

    data: Data
    # If there is no decision made in the Control set default to success
    workflow_parameters: WorkflowParameters
    control: Control = Control.success
    


class InitTMA(Start,Interactive):
    _ROUTING_KEY = 'InitTMA'
    _a = 'prepare-template'
    _b = 'process'

    def __init__(self) -> None:
        super().__init__()

    def deserialize_prepare_template_input(self, body) -> InitTMAPrepareTemplateInput:
        # Can this be abstract away?
        return data_utils.decode_dict(data_class=InitTMAPrepareTemplateInput,data=body)


    def prepare_template(self, prefix, submit_url, input: InitTMAPrepareTemplateInput) -> InitTMAPrepareTemplateOutput:
        if _Config.DEBUG() == False:
            # Get the experimental data, this reads the raw data from the minio, and returns a list of dictionaries
            experimental_data = read_raw_data(ExperimentClass = RAW_TMA())

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
        template = self.env.get_template("form-tma.html")

        # This needs to be replaced
        return InitTMAPrepareTemplateOutput(
            html=template.render(endpoint=submit_url,  
                           experimentaldata=experimental_data,
                           inputSelection=asdict(input.system_parameters.data_flow)))

    def deserialize_process_input(self,body) -> InitTMAProcessInput:
        return data_utils.decode_dict(data_class=InitTMAProcessInput,data=body)

    def process(self, prefix, input: InitTMAProcessInput) -> InitTMAProcessOutput:
        protein_channel_markers = ProteinChannelMarkers()
        # Temporary Fix for methods which directly interact with the Minio -> Need to abstract this away
        if _Config.DEBUG() == False:
            # Based on the form selections / get the TIFF file and the markers.txt file
            urls = get_experiment_data_urls(
                ExperimentClass=RAW_TMA(),
                prefix_name=input.workflow_parameters.experiment_data_id+'/',)


            # Save the Tiff stack locally
            large_tiff_local_dir  = download_stacked_tiff_locally(urls['tiff_name'])
            logging.warning(f"LOCAL NAME :{large_tiff_local_dir}")
        
            # Get & Parse Channel Markers txt file and add to points
            response = requests.get(urls['channel_markers'])


            for l in response.text.split('\n'):
                if l.rstrip() != '':
                    protein_channel_markers.append(ProteinChannelMarker(l.rstrip()))
        else:
            
            # Add mock protein channel markers
            protein_channel_markers.append(ProteinChannelMarker('A0'))
            # generate a mock tiff file
            
            large_tiff_local_dir = 'tf.ome.tiff'
            tifffile.imwrite(large_tiff_local_dir,np.array(TestGenerator.random_image_8bit()), compression='zlib')
            


        
        # Use tifffile to partially read the Tiff file
        tf = tifffile.TiffFile(large_tiff_local_dir)
    
        # Iterate over the Tiff layers and save off the images as grayscale tiffs
        channel_shapes = []
        temp = TissueMicroArray()
        for i,p_chan in enumerate(protein_channel_markers):
            p_channel_tiff = tf.pages[i]
            channel_shapes.append(p_channel_tiff.shape)
            # Need to come up with a means of getting the prefix in
            temp[p_chan] = TissueMicroArrayProteinChannel.write(
                data=Image.fromarray(p_channel_tiff.asarray()),
                prefix=prefix,
                file_name=p_chan)
            

        # Santity Check, ensure that all the protein channels written to the object storage are the same dimension
        assert len(set(channel_shapes)) == 1, 'Not all the selected Images are off the same Dimension, is the Marker List correct?'


        # Deleting the locally stored instance of the full size image
        tf.close()
        os.remove(large_tiff_local_dir)
        
        
        
        # logging.warning(args)
        return InitTMAProcessOutput(
                    data=InitTMAProcessOutput.Data(
                        tissue_micro_array=temp
                    ),
                    workflow_parameters= InitTMAProcessOutput.WorkflowParameters(
                        nuclear_stain= input.workflow_parameters.nuclear_stain,
                        nuclear_markers= input.workflow_parameters.nuclear_markers,
                        membrane_markers= input.workflow_parameters.membrane_markers,
                        protein_channel_markers= protein_channel_markers
                    )
                )

if __name__ == "__main__":
    InitTMA().run()