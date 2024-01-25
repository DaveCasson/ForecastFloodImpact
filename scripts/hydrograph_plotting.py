import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

def convert_to_daily_mean(realtime_df):
    """
    Convert the realtime_df DataFrame to daily mean values for the "LEVEL" and "DISCHARGE" columns.

    Args:
    realtime_df (DataFrame): Pandas DataFrame containing the realtime data with columns: DATETIME, STATION_NUMBER, STATION_NAME, LEVEL, DISCHARGE.

    Returns:
    DataFrame: Pandas DataFrame with daily mean values for the "LEVEL" and "DISCHARGE" columns.
    """
    # Convert the "DATETIME" column to datetime type
    realtime_df['DATETIME'] = pd.to_datetime(realtime_df['DATETIME'])

    # Set the "DATETIME" column as the index
    realtime_df.set_index('DATETIME', inplace=True)

    # Resample the DataFrame to daily frequency and calculate the mean for "LEVEL" and "DISCHARGE" columns
    daily_mean_df = realtime_df['DISCHARGE'].resample('D').mean()

    return daily_mean_df

def calculate_daily_percentiles_of_historic_data(df):
    """
    Calculate the daily percentiles for the discharge data.
    
    Args:
    df (DataFrame): Pandas DataFrame containing the discharge data with a 'DATE' column.
    
    Returns:

    tuple: Three DataFrames containing the max-min, 90-10 percentile, and 25-75 percentile ranges.
    """
    df['MONTH_DAY'] = df['DATE'].dt.strftime('%m-%d')
    max_min_range = {}
    percentile_90_10 = {}
    percentile_25_75 = {}

    for month_day in df['MONTH_DAY'].unique():
        daily_values = df[df['MONTH_DAY'] == month_day]['DISCHARGE'].dropna()
        if len(daily_values) == 0:
            continue
        max_min_range[month_day] = [daily_values.max(), daily_values.min()]
        percentile_90_10[month_day] = [np.percentile(daily_values, 90), np.percentile(daily_values, 10)]
        percentile_25_75[month_day] = [np.percentile(daily_values, 75), np.percentile(daily_values, 25)]

    max_min_df = pd.DataFrame.from_dict(max_min_range, orient='index', columns=['Max', 'Min'])
    percentile_90_10_df = pd.DataFrame.from_dict(percentile_90_10, orient='index', columns=['90th', '10th'])
    percentile_25_75_df = pd.DataFrame.from_dict(percentile_25_75, orient='index', columns=['75th', '25th'])

    # Sort the index in the desired order
    index_order = pd.Index(pd.date_range(start='2000-10-01', end='2001-09-30')).strftime('%m-%d')
    max_min_df = max_min_df.reindex(index_order)
    percentile_90_10_df = percentile_90_10_df.reindex(index_order)
    percentile_25_75_df = percentile_25_75_df.reindex(index_order)

    return max_min_df, percentile_90_10_df, percentile_25_75_df

def plot_annual_hydrograph_statistics(max_min_df, percentile_90_10_df, percentile_25_75_df, realtime_df_daily):
    """
    Plot the hydrograph with percentile ranges.

    Args:
    max_min_df (DataFrame): DataFrame containing max-min range.
    percentile_90_10_df (DataFrame): DataFrame containing 90-10 percentile range.
    percentile_25_75_df (DataFrame): DataFrame containing 25-75 percentile range.
    realtime_df_daily (DataFrame): DataFrame containing the daily mean values for the "DISCHARGE" column.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))# sharex=True)

    # Plot the main hydrograph
    ax1.fill_between(max_min_df.index, max_min_df['Max'], max_min_df['Min'], color='lightblue', alpha=0.3, label='Max-Min Range')
    ax1.fill_between(percentile_90_10_df.index, percentile_90_10_df['90th'], percentile_90_10_df['10th'], color='skyblue', alpha=0.3, label='90-10 Percentile Range')
    ax1.fill_between(percentile_25_75_df.index, percentile_25_75_df['75th'], percentile_25_75_df['25th'], color='steelblue', alpha=0.3, label='25-75 Percentile Range')
    ax1.plot(realtime_df_daily.index, realtime_df_daily.values, color='red', label='RealTime')
    ax1.set_title('Hydrograph for Complete Water Year')
    ax1.set_ylabel('Discharge')
    ax1.legend()
    ax1.set_ylim(0,)
    ax1.set_xlim(max_min_df.index[0], max_min_df.index[-1])
    ax1.grid(True)

    # Format the x-axis tick labels
    ax1.set_xticks(np.arange(0, len(max_min_df), step=len(max_min_df)//12))
    ax1.set_xticklabels([date[0:5] for date in max_min_df.index[::len(max_min_df)//12]], rotation=45)

    #Subset the data to the period of interest (defined by realtime_df_daily.index)
    max_min_df = max_min_df.loc[realtime_df_daily.index]
    percentile_90_10_df = percentile_90_10_df.loc[realtime_df_daily.index]
    percentile_25_75_df = percentile_25_75_df.loc[realtime_df_daily.index]

    # Plot the zoomed-in hydrograph
    ax2.fill_between(max_min_df.index, max_min_df['Max'], max_min_df['Min'], color='lightblue', alpha=0.3, label='Max-Min Range')
    ax2.fill_between(percentile_90_10_df.index, percentile_90_10_df['90th'], percentile_90_10_df['10th'], color='skyblue', alpha=0.3, label='90-10 Percentile Range')
    ax2.fill_between(percentile_25_75_df.index, percentile_25_75_df['75th'], percentile_25_75_df['25th'], color='steelblue', alpha=0.3, label='25-75 Percentile Range')
    ax2.plot(realtime_df_daily.index, realtime_df_daily.values, color='red', label='RealTime')
    ax2.set_title('Hydrograph for Real-Time and Forecasted Data')
    ax2.set_xlabel('Day of the Year')
    ax2.set_ylabel('Discharge')
    ax2.legend()
    ax2.grid(True)

    # Set the x-axis limits of the zoomed-in hydrograph to match the range of realtime_df_daily.index
    ax2.set_xlim(realtime_df_daily.index[0], realtime_df_daily.index[-1])
    #Set lower y-axis limit to 0
    ax2.set_ylim(0,)

    ax2.set_xticks(np.arange(0, len(max_min_df), step=len(max_min_df)//12))
    ax2.set_xticklabels([date[0:5] for date in max_min_df.index[::len(max_min_df)//12]], rotation=45)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df = pd.read_csv('/Users/drc858/GitHub/ForecastFloodImpact/output/historic/05BL022_historic.csv')
    realtime_df = pd.read_csv('/Users/drc858/GitHub/ForecastFloodImpact/output/realtime/05BL022_realtime.csv')

    realtime_df_daily = convert_to_daily_mean(realtime_df)

    month_day = realtime_df_daily.index.strftime('%m-%d')
    #realtime_df_daily.set_index(month_day, inplace=True)

    #Create a new dataframe with month_day as index
    daily_mean_df = pd.DataFrame(realtime_df_daily.values, index=month_day)

            

    df['DATE'] = pd.to_datetime(df['DATE'])
    max_min_df, percentile_90_10_df, percentile_25_75_df = calculate_daily_percentiles_of_historic_data(df)
    plot_annual_hydrograph_statistics(max_min_df, percentile_90_10_df, percentile_25_75_df, daily_mean_df)




