FROM continuumio/miniconda3 as builder

# install python 3.7.4
COPY requirements.txt .
COPY app/ app/
COPY tests/ tests/
RUN conda install -c conda-forge python=3.7 -y  \
    && conda install -c conda-forge  cytoolz==0.10.0 \
    && pip install -r requirements.txt --no-cache-dir

# Run the tests
RUN python -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM continuumio/miniconda3

COPY --from=builder /app /app
COPY requirements.txt .

RUN conda install -c conda-forge python=3.7 -y  \
    && conda install -c conda-forge  cytoolz==0.10.0 \
    && pip install -r requirements.txt --no-cache-dir
    

WORKDIR /app

CMD ["python", "main.py"]
LABEL cincodebio.schema='{"abstract_concept": "CellSegmentation", "service_type": "automated", "service_name": "CellSegDTMA", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "service_parameters", "type": "ServiceParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "dearrayed_tissue_micro_array_cell_segmentation_masks", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "dearrayed_tissue_micro_array", "type": "DearrayedTissueMicroArray", "default_value": null, "metadata": null, "optional": false}]}, "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "nuclear_stain", "type": "NuclearStain", "default_value": null, "metadata": null, "optional": false}]}, "ServiceParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "overlap", "type": "int", "default_value": "80", "metadata": null, "optional": false}, {"name": "threshold", "type": "int", "default_value": "20", "metadata": null, "optional": false}, {"name": "increase_factor", "type": "int", "default_value": "1", "metadata": null, "optional": false}, {"name": "grow_mask", "type": "bool", "default_value": "True", "metadata": null, "optional": false}, {"name": "grow_pixels", "type": "int", "default_value": "10", "metadata": null, "optional": false}, {"name": "grow_method", "type": "GrowMethod", "default_value": "GrowMethod.Sequential", "metadata": null, "optional": false}], "GrowMethod": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "Sequential", "value": "Sequential"}]}}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "dearrayed_tissue_micro_array_cell_segmentation_masks", "type": "DearrayedTissueMicroArrayCellSegmentationMask", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}' \ 
 cincodebio.ontology_version='cellmaps_sdk~0.1.0'