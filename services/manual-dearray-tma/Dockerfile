FROM continuumio/miniconda3:4.12.0 as builder

COPY requirements.txt .
COPY app/ app/
COPY tests/ tests/
RUN pip install --trusted-host host.docker.internal -i http://host.docker.internal:3141/colmbrandon/dev/ --no-cache-dir cellmaps_sdk && \
    pip install -r requirements.txt --no-cache-dir
# Run the tests
RUN python -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM continuumio/miniconda3:4.12.0

COPY --from=builder /app /app
COPY requirements.txt .
RUN pip install --trusted-host host.docker.internal -i http://host.docker.internal:3141/colmbrandon/dev/ --no-cache-dir cellmaps_sdk && \
    pip install -r requirements.txt --no-cache-dir

WORKDIR /app

CMD ["python", "main.py"]
























LABEL cincodebio.schema="{"abstract_concept": "DeArray", "service_type": "interactive", "service_name": "ManualDearrayTMA", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}], "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "rois", "type": "ROIs", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "rois", "type": "ROIs", "default_value": null, "metadata": null, "optional": false}]}, "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}}, "prepare_template_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "workflow_parameters", "type": "WorkflowParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "rois", "type": "ROIs", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "tissue_micro_array", "type": "TissueMicroArray", "default_value": null, "metadata": null, "optional": false}]}, "WorkflowParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "nuclear_stain", "type": "NuclearStain", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "html", "type": "str", "default_value": null, "metadata": null, "optional": false}]}}" \ 
 cincodebio.ontology_version="cellmaps_sdk~0.1.0"