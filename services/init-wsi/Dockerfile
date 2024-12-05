FROM continuumio/miniconda3 as builder

COPY requirements.txt .
COPY app/ app/
COPY tests/ tests/
RUN pip install -r requirements.txt --no-cache-dir
# Run the tests
RUN python -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM continuumio/miniconda3

COPY --from=builder /app /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /app

CMD ["python", "main.py"]
LABEL cincodebio.schema='{"abstract_concept": "Start", "service_type": "interactive", "service_name": "InitWSI", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}], "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "experiment_data_id", "type": "str", "default_value": null, "metadata": null, "optional": false}, {"name": "nuclear_stain", "type": "NuclearStain", "default_value": null, "metadata": null, "optional": true}, {"name": "nuclear_markers", "type": "NuclearMarkers", "default_value": null, "metadata": null, "optional": true}, {"name": "membrane_markers", "type": "MembraneMarkers", "default_value": null, "metadata": null, "optional": true}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "nuclear_stain", "type": "NuclearStain", "default_value": null, "metadata": null, "optional": true}, {"name": "nuclear_markers", "type": "NuclearMarkers", "default_value": null, "metadata": null, "optional": true}, {"name": "membrane_markers", "type": "MembraneMarkers", "default_value": null, "metadata": null, "optional": true}, {"name": "protein_channel_markers", "type": "ProteinChannelMarkers", "default_value": null, "metadata": null, "optional": false}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "WholeSlideImage", "default_value": null, "metadata": null, "optional": false}]}, "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}}, "prepare_template_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "bool", "default_value": null, "metadata": null, "optional": false}, {"name": "nuclear_stain", "type": "bool", "default_value": null, "metadata": null, "optional": false}, {"name": "nuclear_markers", "type": "bool", "default_value": null, "metadata": null, "optional": false}, {"name": "membrane_markers", "type": "bool", "default_value": null, "metadata": null, "optional": false}, {"name": "protein_channel_markers", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}}, "prepare_template_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "html", "type": "str", "default_value": null, "metadata": null, "optional": false}]}}' \ 
 cincodebio.ontology_version='cdb_cellmaps~0.0.1+ds.0.0.1.0.1.14'