FROM sccecincodebio/rpy2-base-image:latest as builder

COPY install-dependencies.r .
COPY requirements.txt .
COPY r-requirements.txt .
# This may not work for BIOCONDUCTOR packages
RUN Rscript install-dependencies.r r-requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY app/ app/
COPY tests/ tests/

# Run the tests
RUN python3 -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM sccecincodebio/rpy2-base-image:latest 

COPY install-dependencies.r .
COPY r-requirements.txt .
COPY requirements.txt .

RUN Rscript install-dependencies.r r-requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
# This may not work for BIOCONDUCTOR packages
COPY --from=builder /app /app

WORKDIR /app

CMD ["python3", "main.py"]

LABEL cincodebio.schema='{"abstract_concept": "Clustering", "service_type": "automated", "service_name": "TissueArchitectureMissile", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "neighbourhoods", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "missile_metadata", "type": "MissileMetadata", "default_value": null, "metadata": null, "optional": false}, {"name": "missile_clusters", "type": "MissileClusters", "default_value": null, "metadata": null, "optional": false}, {"name": "missile_spatial_data", "type": "MissileExpressionSpatialData", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "neighbourhoods", "type": "MissileNeighbourhoods", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}' \ 
 cincodebio.ontology_version='cdb_cellmaps~0.0.1+ds.0.0.1.0.2.6'