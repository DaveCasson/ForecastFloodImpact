# ForecastFloodImpact

Connecting hydrological forecasts to flood impact modelling

The purpose of this repository is to estimate the return period of forecasted flood events. This is done by translating large domain, gridded forecast data to return periods at specific stations.

This repository contains scripts accessing:
- real-time hydrological measurements,
- long-term hydrological measurement records,
- maximum annual statistics for discharge, and
- analysis and forecast data from the NSRPS system.

This is used in conjunction with the Flood Forecast Framework (REF). This open software toolbox is used to generate return periods based on historic records.


## Repository Structure

- 📂 `notebooks/`: Collection of Jupyter Notebooks used to demonstrate data collection and processing
- 📂 `scripts/`: Functions used in the data processing and analyses carried out in the Notebooks.
- 📂 `settings/`: Settings for running the forecasting workflow.
- 📂 `docs/`: Documentation and instructions for running the wor
- 📄 `requirements.txt`: Lists the Python packages required for reproducing the workflow.


Citations:
