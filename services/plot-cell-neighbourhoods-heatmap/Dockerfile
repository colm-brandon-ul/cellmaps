FROM sccecincodebio/rpy2-base-image:latest as builder

COPY app/ app/
COPY tests/ tests/

COPY install-dependencies.r .
COPY requirements.txt .
COPY r-requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
# This may not work for BIOCONDUCTOR packages
RUN Rscript install-dependencies.r r-requirements.txt

# Run the tests
RUN python3 -m unittest discover -s tests/scripts/ -p 'test_*.py' 


# Second stage: build the final image without test data
FROM sccecincodebio/rpy2-base-image:latest 

COPY --from=builder /app /app

COPY install-dependencies.r .
COPY r-requirements.txt .
COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
# This may not work for BIOCONDUCTOR packages
RUN Rscript install-dependencies.r r-requirements.txt

WORKDIR /app

CMD ["python3", "main.py"]









LABEL cincodebio.schema="{"abstract_concept": "Plotting", "service_type": "automated", "service_name": "PlotCellNeighbourhoodsHeatmapMissile", "process_input": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "system_parameters", "type": "SystemParameters", "default_value": null, "metadata": null, "optional": false}, {"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}], "SystemParameters": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data_flow", "type": "DataFlow", "default_value": null, "metadata": null, "optional": false}], "DataFlow": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "heatmap", "type": "bool", "default_value": null, "metadata": null, "optional": false}]}}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "single_cell_clusters", "type": "MissileClusters", "default_value": null, "metadata": null, "optional": false}, {"name": "single_cell_neighbourhoods", "type": "MissileNeighbourhoods", "default_value": null, "metadata": null, "optional": false}]}}, "process_output": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "data", "type": "Data", "default_value": null, "metadata": null, "optional": false}, {"name": "control", "type": "Control", "default_value": "Control.success", "metadata": null, "optional": false}], "Control": {"CLASS_TYPE": "enum", "FIELDS": [{"name": "success", "value": "success"}]}, "Data": {"CLASS_TYPE": "dataclass", "FIELDS": [{"name": "heatmap", "type": "Plot", "default_value": null, "metadata": null, "optional": false}]}}, "prepare_template_input": null, "prepare_template_output": null}" \ 
 cincodebio.ontology_version="cellmaps_sdk~0.1.0"