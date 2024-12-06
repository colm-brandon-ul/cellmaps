FROM continuumio/miniconda3:4.12.0 as builder

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY app/ app/
COPY tests/ tests/

# Run the tests
RUN python -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM continuumio/miniconda3:4.12.0

COPY --from=builder /app /app
COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /app

CMD ["python", "main.py"]
LABEL cincodebio.schema='{"abstract_concept": "TechnicalVarianceCorrection", "service_type": "automated", "service_name": "AceWSI", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "WholeSlideImage", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "whole_slide_image", "type": "WholeSlideImage", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}' \ 
 cincodebio.ontology_version='cdb_cellmaps~0.0.1+ds.0.0.1.0.2.0'