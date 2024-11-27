# Imports - all from standard library
import unittest
import subprocess
import os
import json
from uuid import uuid4
import shutil
from pathlib import Path
import logging

from cdb_cellmaps.data import *
from cdb_cellmaps._test_utils import validate_versus_schema, is_valid_html


#recursive function to check if all the files referenced in the json exist
def print_urls(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'url':
                print(value)
                assert os.path.exists(value) == True, f'{value} does not exist'
            else:
                print_urls(value)
    elif isinstance(data, list):
        for item in data:
            print_urls(item)


class InteractiveTest(unittest.TestCase):
    def test_script_execution(self):
        # Copy existing environment variables
        env = os.environ.copy()
        # add the ones needed for the script
        env['CELLMAPS_DEBUG'] = 'True'
        env['CINCODEBIO_JOB_ID'] = uuid4().hex
        env['CINCODEBIO_WORKFLOW_ID'] = uuid4().hex
        env['CINCODEBIO_BASE_URL'] = 'http://localhost:8000' # This is mock url


        # This needs to be generated for the service from the schema
        env['CINCODEBIO_DATA_PAYLOAD'] = json.dumps({'system_parameters': {'data_flow': {'whole_slide_image': True, 'nuclear_stain': True, 'nuclear_markers': True, 'membrane_markers': True, 'protein_channel_markers': True}}})
        env['CINCODEBIO_ROUTING_KEY'] = 'test.prepare-template'

        # Run the script and test prepare-template
        result = subprocess.run(['python3', 'app/main.py'], capture_output=True, text=True, env=env)

        # Check if the script ran without errors
        self.assertEqual(result.returncode, 0, msg=f"Script failed with the following error: {result.stderr} and {result.stdout}")

        # Check if the process-output.json file exists
        with open(f"{env['CINCODEBIO_JOB_ID']}/prepare-template-output.json") as json_file:
            po = json.load(json_file)  
        
        # assert it versus the output schema - this is always a url? 
        PrepareTemplateOutputSchema = {'html': 'str'}

        # Check if all the files referenced in process-output.json exist
        try:
            frontend_url = po['url']
            # Check if the file is readable and if it is valid html
            is_valid_html(frontend_url)
        except Exception as e:
            self.fail(f"Error reading rendered front-end template {e}")

        # Specify the directories to remove
        directories = [Path(os.getcwd()) / env['CINCODEBIO_JOB_ID'], Path(os.getcwd()) / env['CINCODEBIO_WORKFLOW_ID']]

        # Remove the directories
        for directory in directories:
            try:
                shutil.rmtree(directory)
            except Exception as e:
                ...
           

        # Now test the process implementation

        # This needs to be generated for the service from the schema
        env['CINCODEBIO_DATA_PAYLOAD'] = json.dumps({'workflow_parameters': {'experiment_data_id': 'ysUdjRqbMj', 'nuclear_stain': 'A0', 'nuclear_markers': ['A0'], 'membrane_markers': ['A0']}})
        env['CINCODEBIO_ROUTING_KEY'] = 'test.process'

        # Run the script
        result = subprocess.run(['python3', 'app/main.py'], capture_output=True, text=True, env=env)

        # Check if the script ran without errors
        self.assertEqual(result.returncode, 0, msg=f"Script failed with the following error: {result.stderr} and {result.stdout}")

        # Check if the process-output.json file exists
        with open(f"{env['CINCODEBIO_JOB_ID']}/process-output.json") as json_file:
            po = json.load(json_file)  
        
        # assert it versus the output schema
        ProcessOutputSchema = {'data': {'whole_slide_image': 'WholeSlideImage'}, 'workflow_parameters': {'nuclear_stain': 'NuclearStain', 'nuclear_markers': 'NuclearMarkers', 'membrane_markers': 'MembraneMarkers', 'protein_channel_markers': 'ProteinChannelMarkers'}, 'control': {'CLASS_TYPE': 'enum', 'FIELDS': [{'name': 'success', 'value': 'success'}]}}

        try: 
            validate_versus_schema(ProcessOutputSchema, po)
        except Exception as e:
            self.fail(f"The output file doesn't match the Output Schema {e}")

        # Check if all the files referenced in process-output.json exist
        try:
            if 'data' in po.keys():
                print_urls(po['data'])
        except Exception as e:
            self.fail(f"Atleast one file which referenced in process-output does not exist {e}")

        # Specify the directories to remove
        directories = [Path(os.getcwd()) / env['CINCODEBIO_JOB_ID'], Path(os.getcwd()) / env['CINCODEBIO_WORKFLOW_ID']]

        # Remove the directories
        for directory in directories:
            try:
                shutil.rmtree(directory)
            except Exception as e:
                ...
if __name__ == '__main__':
    unittest.main()
