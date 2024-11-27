FROM python:3.9-slim as builder

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY app/ app/
COPY tests/ tests/
# Run the tests
RUN python -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM python:3.9-slim


COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY --from=builder /app /app

WORKDIR /app

CMD ["python", "main.py"]
LABEL cincodebio.schema='{"abstract_concept": "FeatureExtraction", "service_type": "automated", "service_name": "XtracitDTMA", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "dearrayed_tissue_micro_array_missile_fcs", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "dearrayed_tissue_micro_array", "type": "DearrayedTissueMicroArray", "default_value": null, "metadata": null, "optional": false}, {"name": "dearrayed_tissue_micro_array_cell_segmentation_masks", "type": "DearrayedTissueMicroArrayCellSegmentationMask", "default_value": null, "metadata": null, "optional": false}]}, "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "nuclear_markers", "type": "NuclearMarkers", "default_value": null, "metadata": null, "optional": false}, {"name": "protein_channel_markers", "type": "ProteinChannelMarkers", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "dearrayed_tissue_micro_array_missile_fcs", "type": "DearrayedTissueMicroArrayMissileFCS", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}' \ 
 cincodebio.ontology_version='cdb_cellmaps~0.0.1+ds.0.0.1.0.0.10'