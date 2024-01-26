import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

def convert_to_daily_mean(realtime_df, variable, date_col='DATETIME'):
    """
    Convert the realtime_df DataFrame to daily mean values for the "LEVEL" and "DISCHARGE" columns.

    Args:
    realtime_df (DataFrame): Pandas DataFrame containing the realtime data with columns: DATETIME, STATION_NUMBER, STATION_NAME, LEVEL, DISCHARGE.

    Returns:
    DataFrame: Pandas DataFrame with daily mean values for the "LEVEL" and "DISCHARGE" columns.
    """
    # Convert the "DATETIME" column to datetime type
    realtime_df[date_col] = pd.to_datetime(realtime_df[date_col])

    # Set the "DATETIME" column as the index
    realtime_df.set_index(date_col, inplace=True)

    # Resample the DataFrame to daily frequency and calculate the mean for "LEVEL" and "DISCHARGE" columns
    daily_mean_df = realtime_df[variable].resample('D').mean()

    return daily_mean_df

def calculate_daily_percentiles_of_historic_data(df, variable):
    """
    Calculate the daily percentiles for the discharge data.
    
    Args:
    df (DataFrame): Pandas DataFrame containing the discharge data with a 'DATE' column.
    
    Returns:

    tuple: Three DataFrames containing the max-min, 90-10 percentile, and 25-75 percentile ranges.
    """
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['MONTH_DAY'] = df['DATE'].dt.strftime('%m-%d')

    historic_range_df = {}
    max_min_range = {}
    percentile_range_1 = {}
    percentile_range_2= {}

    for month_day in df['MONTH_DAY'].unique():
        daily_values = df[df['MONTH_DAY'] == month_day][variable].dropna()
        if len(daily_values) == 0:
            continue
        max_min_range[month_day] = [daily_values.max(), daily_values.min()]
        percentile_range_1[month_day] = [np.percentile(daily_values, 90), np.percentile(daily_values, 10)]
        percentile_range_2[month_day] = [np.percentile(daily_values, 75), np.percentile(daily_values, 25)]

    historic_range_df = pd.concat([pd.DataFrame.from_dict(max_min_range, orient='index', columns=['Max', 'Min']),
                            pd.DataFrame.from_dict(percentile_range_1, orient='index', columns=['90th', '10th']),
                            pd.DataFrame.from_dict(percentile_range_2, orient='index', columns=['75th', '25th'])], axis=1)

    # Sort the index in the desired order
    index_order = pd.Index(pd.date_range(start='2000-10-01', end='2001-09-30')).strftime('%m-%d')
    historic_range_df = historic_range_df.reindex(index_order)

    return historic_range_df

def plot_annual_hydrograph_statistics(station_number,variable, historic_range_df, realtime_df_daily, save_png=False, png_path=None): 

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))# sharex=True)

    # Plot the main hydrograph
    ax1.fill_between(historic_range_df.index, historic_range_df['Max'], historic_range_df['Min'], color='lightblue', alpha=0.3, label='Max-Min Range')
    ax1.fill_between(historic_range_df.index, historic_range_df['90th'], historic_range_df['10th'], color='skyblue', alpha=0.3, label='90-10 Percentile Range')
    ax1.fill_between(historic_range_df.index, historic_range_df['75th'], historic_range_df['25th'], color='steelblue', alpha=0.3, label='25-75 Percentile Range')
    ax1.plot(realtime_df_daily.index, realtime_df_daily.values, color='red', label='RealTime')
    ax1.set_title(f'{variable} Hydrograph for Complete Water Year, Station {station_number}')
    ax1.set_ylabel(variable)
    ax1.legend()
    ax1.set_ylim(0,)
    ax1.set_xlim(historic_range_df.index[0], historic_range_df.index[-1])
    ax1.grid(True)

    # Format the x-axis tick labels
    ax1.set_xticks(np.arange(0, len(historic_range_df), step=len(historic_range_df)//12))
    ax1.set_xticklabels([date[0:5] for date in historic_range_df.index[::len(historic_range_df)//12]], rotation=45)

    #Subset the data to the period of interest (defined by realtime_df_daily.index)
    historic_range_df = historic_range_df.loc[realtime_df_daily.index]
    
    # Plot the zoomed-in hydrograph
    ax2.fill_between(historic_range_df.index, historic_range_df['Max'], historic_range_df['Min'], color='lightblue', alpha=0.3, label='Max-Min Range')
    ax2.fill_between(historic_range_df.index, historic_range_df['90th'], historic_range_df['10th'], color='skyblue', alpha=0.3, label='90-10 Percentile Range')
    ax2.fill_between(historic_range_df.index, historic_range_df['75th'], historic_range_df['25th'], color='steelblue', alpha=0.3, label='25-75 Percentile Range')
    ax2.plot(realtime_df_daily.index, realtime_df_daily.values, color='red', label='RealTime')
    ax2.set_title(f'{variable} for Real-Time and Forecasted Data, Station {station_number}')
    ax2.set_xlabel('Day of the Year')
    ax2.set_ylabel(variable)
    ax2.legend()
    ax2.grid(True)

    # Set the x-axis limits of the zoomed-in hydrograph to match the range of realtime_df_daily.index
    ax2.set_xlim(realtime_df_daily.index[0], realtime_df_daily.index[-1])
    #Set lower y-axis limit to 0
    ax2.set_ylim(0,)

    ax2.set_xticks(np.arange(0, len(historic_range_df), step=len(historic_range_df)//12))
    ax2.set_xticklabels([date[0:5] for date in historic_range_df.index[::len(historic_range_df)//12]], rotation=45)

    plt.tight_layout()
    plt.show()

    if save_png:
        plt.savefig(png_path, dpi=300)

def plot_realtime_hydrograph_with_historical_ranges(station_number,variable,historic_df, realtime_df, save_png=False, png_path=None):

    historic_range_df = calculate_daily_percentiles_of_historic_data(historic_df,variable)

    realtime_df_daily = convert_to_daily_mean(realtime_df,variable)

    month_day = realtime_df_daily.index.strftime('%m-%d')
    daily_mean_df = pd.DataFrame(realtime_df_daily.values, index=month_day)
    
    plot_annual_hydrograph_statistics(station_number, variable, historic_range_df, daily_mean_df,save_png, png_path)

if __name__ == '__main__':

    df = pd.read_csv('/Users/drc858/GitHub/ForecastFloodImpact/output/historic/05BL022_historic.csv')
    realtime_df = pd.read_csv('/Users/drc858/GitHub/ForecastFloodImpact/output/realtime/05BL022_realtime.csv')
    png_path = '/Users/drc858/GitHub/ForecastFloodImpact/output/05BL022_hydrograph.png'
    variable = 'DISCHARGE'

    plot_realtime_hydrograph_with_historical_ranges('05BL022',variable, df, realtime_df, save_png=True, png_path=png_path)