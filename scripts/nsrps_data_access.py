# Description: This script contains functions to retrieve scalar data from the Environment and Climate Change Canada (ECCC) API.
# data
import warnings
import re
import time
import configparser
from datetime import datetime, timedelta
import xarray as xr 
import pandas as pd
import numpy as np
from shapely.geometry import Point

# web map services 
from owslib.wms import WebMapService
from owslib.wcs import WebCoverageService
from owslib.wcs import Authentication
from owslib.ogcapi.features import Features

import threading

# Plot the forecast data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_wms_service_for_forecast_times(layer_name, login,iso_format="%Y-%m-%dT%H:%M:%SZ"):
    """
    Query the WMS service for the forecast times available for the layer
    """
    # first querying the WMS for time metadata
    wms = WebMapService(f'https://geo.weather.gc.ca/geomet?&SERVICE=WMS&LAYERS={layer_name}',
                        version='1.3.0',
                        auth=Authentication(username=login['Username'], password=login['Password']),
                        timeout=300)
    first_datetime, last_datetime, datetime_interval = wms[layer_name].dimensions['time']['values'][0].split('/')
    oldest_fcst, newest_fcast, interval = wms[layer_name].dimensions['reference_time']['values'][0].split('/')

    # convert dates to datetime objects
    
    first = datetime.strptime(first_datetime, iso_format)
    last = datetime.strptime(last_datetime, iso_format)

    # remove anything that isn't a number from the datetime interval (time between forecasts)
    intvl = int(re.sub(r'\D', '', datetime_interval))

    # create a list of forecast datetimes (we will add these to the requested data)
    fcasthrs = [first]
    while first < last:
        first = first + timedelta(hours=intvl)
        fcasthrs.append(first)

    return newest_fcast, fcasthrs

def query_wms_service_for_analysis_times(layer_name, login,iso_format="%Y-%m-%dT%H:%M:%SZ"):
    """
    Query the WMS service for the forecast times available for the layer
    """
    # first querying the WMS for time metadata
    wms = WebMapService(f'https://geo.weather.gc.ca/geomet?&SERVICE=WMS&LAYERS={layer_name}',
                        version='1.3.0',
                        auth=Authentication(username=login['Username'], password=login['Password']),
                        timeout=300)
    
    first_datetime, last_datetime, datetime_interval = wms[layer_name].dimensions['time']['values'][0].split('/')
    oldest_analysis, newest_analysis, interval = wms[layer_name].dimensions['reference_time']['values'][0].split('/')

    # convert dates to datetime objects
    
    first = datetime.strptime(oldest_analysis, iso_format)
    last = datetime.strptime(newest_analysis, iso_format)

    # remove anything that isn't a number from the datetime interval (time between forecasts)
    intvl = int(re.sub(r'\D', '', interval))

    # create a list of forecast datetimes (we will add these to the requested data)
    analysishrs = [first]
    while first < last:
        first = first + timedelta(hours=intvl)
        analysishrs.append(first)

    return first_datetime

def query_wcs_service_for_analysis_data(layer_name, login, newest_analysis, iso_format="%Y-%m-%dT%H:%M:%SZ"):
    """
    Query the WCS service for the analysis data
    """
    wcs = WebCoverageService(f'https://geo.weather.gc.ca/geomet?&SERVICE=WCS&COVERAGEID={layer_name}', 
                    auth=Authentication(username=login['Username'], password=login['Password']),
                    version='2.0.1',
                    timeout=300)

    response = wcs.getCoverage(identifier=[layer_name], 
                               format='image/netcdf', 
                               subsettingcrs='EPSG:4326', 
                               subsets=[('lat', 50, 52.0), ('lon', -117.0, -113.0)],
                               DIM_REFERENCE_TIME=newest_analysis,
                               TIME=newest_analysis)
    ds = xr.open_dataset(response.read()).load()
    ds = ds.expand_dims(time=[datetime.strptime(newest_analysis, iso_format)])
    
    return ds

def query_wcs_service_for_forecast_data(layer_name, login, newest_fcast, fcasthrs, iso_format="%Y-%m-%dT%H:%M:%SZ"):

    def fetch_data(hr, layer_name, arrys, idx):
        logger.info(f'Querying {newest_fcast}m lead time {hr}')
        response = wcs.getCoverage(identifier=[layer_name], 
                                   format='image/netcdf', 
                                   subsettingcrs='EPSG:4326', 
                                   subsets=[('lat', 50, 52.0), ('lon', -117.0, -113.0)],
                                   DIM_REFERENCE_TIME=newest_fcast, 
                                   TIME=hr)
        ds = xr.open_dataset(response.read()).load()
        ds = ds.expand_dims(time=[fcasthrs[idx] + timedelta(hours=time_zone)])
        arrys[idx] = ds

    fcasthrs_str = [datetime.strftime(hr, iso_format) for hr in fcasthrs]

    wcs = WebCoverageService(f'https://geo.weather.gc.ca/geomet?&SERVICE=WCS&COVERAGEID={layer_name}', 
                    auth=Authentication(username=login['Username'], password=login['Password']),
                    version='2.0.1',
                    timeout=300)

    time_zone = -7

    arrys = [None] * len(fcasthrs_str)
    threads = []

    for i, hr in enumerate(fcasthrs_str):
        thread = threading.Thread(target=fetch_data, args=(hr, layer_name, arrys, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    fcasts = xr.concat([ds for ds in arrys if ds is not None], dim='time')
    
    return fcasts
    

def extract_station_from_grid(station, input_ds):
    """
    Extract from the grided data for a given station
    """

    # Extract the station location
    station_location = Point(station[1]['MODEL_LONGITUDE'], station[1]['MODEL_LATITUDE'])

    # Extract the station data
    station_data = input_ds.sel(lon=station_location.x, lat=station_location.y, method='nearest')

    return station_data

def bias_correct_forecast(measurements, model):
    
    # Ensure both dataframes are sorted by index
    measurements = measurements.sort_index()
    model = model.sort_index()

    # Find the last overlapping time
    last_overlap_time = measurements.index.intersection(model.index).max()

    # If there's no overlap, use the last time of the measurements dataframe
    if pd.isna(last_overlap_time):
        last_overlap_time = measurements.index[-1]

    # Get the last measurement value
    last_measurement_value = measurements.loc[last_overlap_time, 'DISCHARGE']

    # Get the corresponding model value at the overlap time
    if last_overlap_time in model.index:
        last_model_value = model.loc[last_overlap_time, 'Discharge']
    else:
        last_model_value = model.iloc[0]['Discharge']

    # Calculate the correction factor
    correction_factor = last_measurement_value - last_model_value

    # Apply the correction to the model dataframe
    model['Discharge'] = model['Discharge'].apply(lambda x: x + correction_factor)

    return model