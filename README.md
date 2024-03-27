# ForecastFloodImpact

Connecting hydrological forecasts to flood impact modelling.

The purpose of this repository is to demonstrate the forecasting of return period flood events, based on publicly available hydrological data.


This is done by accessing real time and forecasted data, primarily from the MSC GeoMet - GeoMet-OGC-API. In particular, using Python scripts and Jupyter Notebooks to:
- access real-time hydrological measurements,
- access long-term historic hydrological measurements,
- access annual statistics for discharge, and
- analysis and forecast data from the NSRPS system.

This is used in conjunction with the recently released [Flood Frequency Analysis Framework](https://www.sciencedirect.com/science/article/abs/pii/S136481522400001X). This open software toolbox is used to generate return periods based on historic records.

The result is near-real time and forecast return periods, that could be used for connection to hydraulic and/or flood impact modelling.


## Repository Structure

- 📂 `notebooks/`: Collection of Jupyter Notebooks used to demonstrate data collection and processing
- 📂 `scripts/`: Functions used in the data processing and analyses carried out in the Notebooks.
- 📂 `settings/`: Settings for running the forecasting workflow.
- 📂 `docs/`: Documentation and instructions for running the workflows
- 📂 `flood_frequency_analysis/`: Flood Frequency Analysis for select locations
- 📂 `gis_data/`: Supporting GIS data for the test watershed
- 📄 `requirements.txt`: Lists the Python packages required for reproducing the workflow.


## Instructions

#### Running Jupyter notebooks
The workflows for this repository are contained in Jupyter Notebooks. For the installation of Jupyter Notebooks, please refer to the [Getting Started Instructions](./docs/GettingStarted.md) here to get set up with the python environment.

Once set up, 3 Jupyter Notebooks should be run in sequence:
- [01 - Access Hydro Observations](./notebooks/01_access_hydro_observations.ipynb)
- [02 - Access NRSPS Analysis and Forecasts](./notebooks/02_access_nsrps_analysis_and_forecasts.ipynb)
- [03 - Calculate realtime and forecasted return levels](./notebooks/02_access_nsrps_analysis_and_forecasts.ipynb)

These workflows will walk the user through accessing and processing the historic, realtime and forecasted hydrological data.

#### Configuration and Settings

The configuration for the the workflows are available in a [simple configuration file](../settings/general_settings.yaml) in the settings folder. This configuration file points to gis data and csv files that contain the metadata used to access and plot hydrological data.


#### Flood Frequency Analysis

The calculation for return periods is done with an open source toolbox for [Flood Frequency Analysis Framework](https://www.sciencedirect.com/science/article/abs/pii/S136481522400001X). The results from that toolbox for select stations of interest is contained within this repository. As mentioned in the disclaimer below, these are derived for demonstration purposes only.

## Disclaimer

This repository and code base is developed for research and demonstration purposes only. It connects to publicly available data sources that may be considered experimental. No operational decision or engineering making should be made from this repository or its contents. Please refer to the MIT license for further details.

## Citations

Vidrio-Sahagún, C. T., Ruschkowski, J., He, J., Pietroniro, A. (2024). A practice-oriented framework for stationary and nonstationary flood frequency analysis. Environmental Modelling & Software, 105940, ISSN 1364-8152, https://doi.org/10.1016/j.envsoft.2024.105940
