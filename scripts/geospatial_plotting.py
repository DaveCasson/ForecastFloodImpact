import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.img_tiles import OSM
import pandas as pd


def plot_watershed_flowlines_stations(watershed_shapefile, flowlines_shapefile, stations_csv):
    # Read the shapefiles with GeoPandas
    watershed = gpd.read_file(watershed_shapefile)
    flowlines = gpd.read_file(flowlines_shapefile)
    stations =  pd.read_csv(stations_csv)

    # Ensure the shapefiles are not empty
    if watershed.empty or flowlines.empty:
        raise ValueError("One or both of the shapefiles are empty.")

    # Set up the figure and axis with Cartopy, using the OSM projection
    fig, ax = plt.subplots(figsize=(15, 15), subplot_kw={'projection': ccrs.PlateCarree()})

    # Add OSM basemap
    osm = OSM()
    ax.add_image(osm,10)

    # Reproject shapefiles to the same CRS as the basemap (Plate Carree - EPSG:4326)
    watershed = watershed.to_crs(epsg=4326)
    flowlines = flowlines.to_crs(epsg=4326)

    # Plot the shapefiles
    watershed.plot(ax=ax, edgecolor='green', facecolor='none',linewidth=1)
    flowlines.plot(ax=ax, color='blue',linewidth=0.5)  
    
    #ax.scatter(stations['Longitude'], stations['Latitude'], color='black', marker='x', s=50, label='Hydrometric Stations')

    for index, row in stations.iterrows():
            ax.scatter(row['Longitude'], row['Latitude'], color='black', marker='x', s=50)
            ax.text(row['Longitude'], row['Latitude'], row['Name / Nom'], fontsize=8, ha='right', va='bottom',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.5))

    # Add a title
    ax.set_title("Bow Watershed, Flowlines and Stations")

    plt.show()




