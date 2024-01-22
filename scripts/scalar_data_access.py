# Import needed modules

from datetime import date
from owslib.ogcapi.features import Features
import pandas as pd
import yaml
from pprint import pprint

from pathlib import Path
# Set up logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_real_time_data(stations, start_date, end_date, output_dir, output_suffix='', limit=10000):
    """
    Retrieve real-time hydrometric data for a given time period and save it to CSV files.
    
    Parameters:
    - stations (list): List of hydrometric station IDs.
    - start_date (datetime.date): Start date of the time period.
    - end_date (datetime.date): End date of the time period.
    - output_dir (str or pathlib.Path): Directory path where the output CSV files will be saved.
    - output_suffix (str, optional): Suffix to be added to the output CSV file names. Default is an empty string.
    - limit (int, optional): Maximum number of data points to retrieve per station. Default is 10000.
    
    Returns:
    - None
    
    Raises:
    - ValueError: If no water level data is returned for any station.
    """
    
    time_ = f"{start_date}/{end_date}"
    logger.info(f"Retrieving hydrometric data for the period {time_}")

    # List of stations with no water level data
    stations_without_data = []

    # Data retrieval and creation of the data frames
    for station in stations:

        # Retrieval of water level data
        hydro_data = oafeat.collection_items(
            "hydrometric-realtime",
            limit=limit,
            datetime=time_,
            STATION_NUMBER=station,
        )

        # Creation of a data frame if there is data for the chosen time period
        if hydro_data["features"]:
            
            # Creation of a dictionary in a format compatible with Pandas
            historical_data_format = [
                {
                    # Note coordinates can be pulled as below, but they are not currently used
                    #"LATITUDE": el["geometry"]["coordinates"][1],
                    #"LONGITUDE": el["geometry"]["coordinates"][0],
                    **el["properties"],
                }
                for el in hydro_data["features"]
            ]
            # Creation of the data frame
            historical_data_df = pd.DataFrame(
                historical_data_format,
                columns=[
                    "STATION_NUMBER",
                    "STATION_NAME",
                    "DATETIME",
                    "LEVEL",
                    "DISCHARGE"
                ],
            )
            
            # Detect and convert data types of columns
            historical_data_df = historical_data_df.infer_objects(copy=False)

            # Creating an index with the date in a datetime format
            historical_data_df["DATETIME"] = pd.to_datetime(
                historical_data_df["DATETIME"]
            )
            historical_data_df.set_index(["DATETIME"], inplace=True, drop=True)
            
            # Output data frame to csv file
            output_csv_path = Path(output_dir,f'{station}{output_suffix}.csv')
            historical_data_df.to_csv(output_csv_path, index=True)

            logger.info(f"Data output to {output_csv_path}")
        
        # If there is no data for the chosen time period, the station
        # will be removed from the dataset
        else:
            stations_without_data.append(station)

    # Removing hydrometric stations without water level data from the station list
    for station in stations_without_data:
        logger.warning(
            f"Station {station} has no water level data for the chosen time period."
        )
        stations.remove(station)

    # Raising an error if no station is left in the list
    if not stations:
        raise ValueError(
            f"No water level data was returned, please check the query."
        )
    
def retrieve_historic_data(stations, start_date, end_date, output_dir, output_suffix, limit=5000):
    """
    Retrieve historic hydrometric data for a given time period and save it to CSV files.

    Parameters:
    - stations (list): List of hydrometric station IDs to retrieve data for.
    - start_date (date): Start date of the time period.
    - end_date (date): End date of the time period.
    - output_dir (str or Path): Directory path to save the output CSV files.
    - output_suffix (str): Suffix to add to the output CSV file names.
    - limit (int): Maximum number of data points to retrieve per station.

    Returns:
    - None
    """

    time_ = f"{start_date}/{end_date}"
    logger.info(f"Retrieving hydrometric data for the period {time_}")

    # List of stations with no water level data
    stations_without_data = []

    # Data retrieval and creation of the data frames
    for station in stations:

        # Retrieval of water level data
        hydro_data = oafeat.collection_items(
            "hydrometric-daily-mean",
            datetime=time_,
            limit=limit,
            STATION_NUMBER=station,
        )

        # Creation of a data frame if there is data for the chosen time period
        if hydro_data["features"]:
            
            # Creation of a dictionary in a format compatible with Pandas
            historical_data_format = [
                {
                    **el["properties"],
                }
                for el in hydro_data["features"]
            ]
            # Creation of the data frame
            historical_data_df = pd.DataFrame(
                historical_data_format,
                columns=[
                    "STATION_NUMBER",
                    "STATION_NAME",
                    "DATE",
                    "DISCHARGE"
                ],
            )
            
            # Detect and convert data types of columns
            historical_data_df = historical_data_df.infer_objects(copy=False)

            # Creating an index with the date in a datetime format
            historical_data_df["DATE"] = pd.to_datetime(
                historical_data_df["DATE"]
            )
            historical_data_df.set_index(["DATE"], inplace=True, drop=True)
            
            # Output data frame to csv file
            output_csv_path = Path(output_dir,f'{station}{output_suffix}.csv')
            historical_data_df.to_csv(output_csv_path, index=True)

            logger.info(f"Data output to {output_csv_path}")
        
        # If there is no data for the chosen time period, the station
        # will be removed from the dataset
        else:
            stations_without_data.append(station)

    # Removing hydrometric stations without water level data from the station list
    for station in stations_without_data:
        logger.warning(
            f"Station {station} has no water level data for the chosen time period."
        )
        stations.remove(station)

    # Raising an error if no station is left in the list
    if not stations:
        raise ValueError(
            f"No water level data was returned, please check the query."
        )

if __name__ == "__main__":
    # Read yaml file
    config_file = "../settings/bow_watershed_settings.yaml"
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Config file: {pprint(config)}")

    # Read in the list of hydrometric stations
    hydro_stations_df = pd.read_csv(config["hydro_stations_csv"])
    search_stations = hydro_stations_df["ID"].tolist()
    logger.info(f"Hydrometric stations: {search_stations}")   

    # Create an instance of the Features class
    oafeat = Features("https://api.weather.gc.ca/")

    # Start and end of the time period for which the data will be retrieved
    end_date = date.today()
    years_to_search = 100
    days_to_search = years_to_search * 365

    start_date = end_date - pd.Timedelta(days=days_to_search)

    output_dir = Path('../output/historic')
    output_suffix = '_historic'

    retrieve_historic_data(search_stations, start_date, end_date, output_dir, output_suffix,limit=days_to_search)