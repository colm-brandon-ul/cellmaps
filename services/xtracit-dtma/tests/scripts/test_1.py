# Imports - all from standard library
import unittest
import subprocess
import os
import json
from uuid import uuid4
import shutil
from pathlib import Path

from cdb_cellmaps.data import *
from cdb_cellmaps._test_utils import validate_versus_schema


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


class AutomatedTest(unittest.TestCase):
    def test_script_execution(self):
        # Copy existing environment variables
        env = os.environ.copy()
        # add the ones needed for the script
        env['CELLMAPS_DEBUG'] = 'True'
        env['CINCODEBIO_ROUTING_KEY'] = 'test.process'
        env['CINCODEBIO_JOB_ID'] = uuid4().hex
        env['CINCODEBIO_WORKFLOW_ID'] = uuid4().hex


        # This needs to be generated for the service from the schema
        env['CINCODEBIO_DATA_PAYLOAD'] = json.dumps({'system_parameters': {'data_flow': {'dearrayed_tissue_micro_array_missile_fcs': True}}, 'workflow_parameters': {'nuclear_markers': ['A0'], 'protein_channel_markers': ['A0','A1','A2']}, 'data': {'dearrayed_tissue_micro_array': {'A0': {'A0': {'url': 'tests/data/dearrayed_tissue_micro_array/A0/A0.ome.tiff'},'A1': {'url': 'tests/data/dearrayed_tissue_micro_array/A0/A0.ome.tiff'},'A2': {'url': 'tests/data/dearrayed_tissue_micro_array/A0/A0.ome.tiff'}}}, 'dearrayed_tissue_micro_array_cell_segmentation_masks': {'A0': {'nucleus_mask': {'url': 'tests/data/dearrayed_tissue_micro_array_cell_segmentation_masks/A0/Anucleus_mask.ome.tiff'}, 'membrane_mask': {'url': 'tests/data/dearrayed_tissue_micro_array_cell_segmentation_masks/A0/Amembrane_mask.ome.tiff'}}}}})

        # Run the script
        result = subprocess.run(['python3', 'app/main.py'], capture_output=True, text=True, env=env)

        # Check if the script ran without errors
        self.assertEqual(result.returncode, 0, msg=f"Script failed with the following error: {result.stderr} and {result.stdout}")

        # Check if the process-output.json file exists
        with open(f"{env['CINCODEBIO_JOB_ID']}/process-output.json") as json_file:
            po = json.load(json_file)  
        
        OutputSchema = {'data': {'dearrayed_tissue_micro_array_missile_fcs': 'DearrayedTissueMicroArrayMissileFCS'}, 'control': {'CLASS_TYPE': 'enum', 'FIELDS': [{'name': 'success', 'value': 'success'}]}}
        # assert it versus the output schema

        try: 
            validate_versus_schema(OutputSchema, po)
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
            except Exception:
                ...

if __name__ == '__main__':
    unittest.main()
