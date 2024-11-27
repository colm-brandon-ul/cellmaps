# Use tensorflow/tensorflow as the base image
# Change the build arg to edit the tensorflow version.
# Only supporting python3.
ARG TF_VERSION=2.8.0

FROM tensorflow/tensorflow:${TF_VERSION} as builder

RUN apt-get update && apt-get install -y  \
    graphviz && \
    rm -rf /var/lib/apt/lists/* && \
    /usr/bin/python3 -m pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir && \
    pip install --no-deps  deepcell

COPY app/ app/
COPY tests/ tests/

    # Install deepcell seperately with no deps
# Run the tests
RUN python -m unittest discover -s tests/scripts/ -p 'test_*.py' 



# Second stage: build the final image without test data
FROM tensorflow/tensorflow:${TF_VERSION}

RUN apt-get update && apt-get install -y  \
    graphviz && \
    rm -rf /var/lib/apt/lists/* && \
    /usr/bin/python3 -m pip install --no-cache-dir --upgrade pip

COPY --from=builder /app /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir && \
    pip install --no-deps  deepcell

WORKDIR /app

CMD ["python", "main.py"]
LABEL cincodebio.schema='{"abstract_concept": "CellSegmentation", "service_type": "automated", "service_name": "DeepcellWSI", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image_cell_segmentation_masks", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "WholeSlideImage", "default_value": null, "metadata": null, "optional": false}]}, "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "nuclear_stain", "type": "NuclearStain", "default_value": null, "metadata": null, "optional": false}, {"name": "membrane_markers", "type": "MembraneMarkers", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image_cell_segmentation_masks", "type": "WholeSlideImageCellSegmentationMask", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}' \ 
 cincodebio.ontology_version='cdb_cellmaps~0.0.1+ds.0.0.1.0.0.7'
LABEL cincodebio.schema='{"abstract_concept": "CellSegmentation", "service_type": "automated", "service_name": "DeepcellWSI", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image_cell_segmentation_masks", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "WholeSlideImage", "default_value": null, "metadata": null, "optional": false}]}, "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "nuclear_stain", "type": "NuclearStain", "default_value": null, "metadata": null, "optional": false}, {"name": "membrane_markers", "type": "MembraneMarkers", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image_cell_segmentation_masks", "type": "WholeSlideImageCellSegmentationMask", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}' \ 
 cincodebio.ontology_version='cdb_cellmaps~0.0.1+ds.0.0.1.0.0.7'