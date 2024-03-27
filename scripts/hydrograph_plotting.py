import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from nsrps_data_access import bias_correct_forecast

def convert_to_daily_mean(df, variable, date_col='DATETIME'):
    """
    Convert the df DataFrame to daily mean values for the "LEVEL" and "DISCHARGE" columns.

    Args:
    df (DataFrame): Pandas DataFrame containing the realtime data with columns: DATETIME, STATION_NUMBER, STATION_NAME, LEVEL, DISCHARGE.

    Returns:
    DataFrame: Pandas DataFrame with daily mean values for the "LEVEL" and "DISCHARGE" columns.
    """
    # Convert the "DATETIME" column to datetime type
    df[date_col] = pd.to_datetime(df[date_col])

    # Set the "DATETIME" column as the index
    df.set_index(date_col, inplace=True)

    # Resample the DataFrame to daily frequency and calculate the mean for "LEVEL" and "DISCHARGE" columns
    daily_mean_df = df[variable].resample('D').mean()

    return daily_mean_df

def add_thresholds(threshold_df,station_number, ax):

    # Define different line styles
    # Define more line styles to ensure uniqueness
    line_styles = [(0, (5, 10)),'--', '-.', ':', (0, (3, 5, 1, 5)),'-', (0, (1, 10)), (0, (5, 1)), 
                (0, (3, 1, 1, 1)), (0, (3, 10, 1, 10))]

    # Adjust alpha for less pronounced lines
    alpha_value = 0.6
    
    # Cycle through the line styles for different return periods
    for i, row in threshold_df.iterrows():
        t_year = row['T_yrs']
        value = row[station_number]
        line_style = line_styles[i % len(line_styles)]
        ax.axhline(y=value, color='red', linestyle=line_style,alpha=alpha_value, label=f'T-{t_year} years')

    return ax
    
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
    #index_order = pd.date_range(start='2023-10-01', end='2024-09-30', freq='D').strftime('%m-%d')
    #historic_range_df = historic_range_df.reindex(index_order)

    # Get current year
    current_year = pd.to_datetime('today').year
    # If current month is October, November, or December, set the year to next year
    if pd.to_datetime('today').month not in [10, 11, 12]:
        # Subtract 1 from current year
        water_year_start = current_year - 1
        water_year_end = current_year
    else:
        water_year_start = current_year
        water_year_end = current_year + 1

    # Convert current year to string
    water_year_start = str(water_year_start)
    water_year_end = str(water_year_end)

    new_index = []
    for date in historic_range_df.index:
        month, day = date.split('-')
        if month in ['10', '11', '12']:
            new_date = f"{month}-{day}-{water_year_start}"
        else:
            new_date = f"{month}-{day}-{water_year_end}"

        new_index.append(new_date)
    
    # Make new_index a DatetimeIndex
    new_index = pd.to_datetime(new_index)

    # Create new DataFrame with modified index
    historic_range_df_with_year = pd.DataFrame(historic_range_df.values, index=new_index, columns=historic_range_df.columns)
    #Sort the index
    historic_range_df_with_year.sort_index(inplace=True)

    return historic_range_df_with_year

def plot_annual_hydrograph_statistics(station_number,variable, historic_range_df, realtime_df, forecast_df=None, analysis_df=None, threshold_df=None,forecast_bias_corrected_df=None, save_png=False, png_path=None,): 

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

    # Plot the main hydrograph
    ax1.fill_between(historic_range_df.index, historic_range_df['Max'], historic_range_df['Min'], color='lightblue', alpha=0.3, label='Max-Min Range')
    ax1.fill_between(historic_range_df.index, historic_range_df['90th'], historic_range_df['10th'], color='skyblue', alpha=0.3, label='90-10 Percentile Range')
    ax1.fill_between(historic_range_df.index, historic_range_df['75th'], historic_range_df['25th'], color='steelblue', alpha=0.3, label='25-75 Percentile Range')
    ax1.plot(realtime_df.index, realtime_df.values, color='black', label='Real Time Gauge')
    if forecast_df is not None:
        ax1.plot(forecast_df.index, forecast_df.values, color='green', label='NSRPS Forecast')
    if forecast_bias_corrected_df is not None:
        ax1.plot(forecast_bias_corrected_df.index, forecast_bias_corrected_df.values, color='purple', label='NSRPS Forecast Bias Corrected')
    if analysis_df is not None:
        ax1.scatter(analysis_df.index, analysis_df.values, color='grey', label='NSRPS Analysis')
    ax1.set_title(f'{variable} Hydrograph for Complete Water Year, Station {station_number}')
    ax1.set_ylabel(variable)
    #ax1.set_ylim(0,)
    ax1.set_xlim(historic_range_df.index[0], historic_range_df.index[-1])
    ax1.grid(True)
    
    #Check if threshold_df is not empty or None
    if threshold_df is not None:
        add_thresholds(threshold_df,station_number, ax1)
 
    ax1.legend()

    #Combine index of realtime_df and forecast_df
    if forecast_df is not None:
        combined_index = realtime_df.index.union(forecast_df.index)
    else:
        combined_index = realtime_df.index
    #Subset the data to the period of interest (defined by realtime_df_daily.index)
    historic_range_df = historic_range_df.loc[combined_index]
    
    # Plot the zoomed-in hydrograph
    ax2.fill_between(historic_range_df.index, historic_range_df['Max'], historic_range_df['Min'], color='lightblue', alpha=0.3, label='Max-Min Range')
    ax2.fill_between(historic_range_df.index, historic_range_df['90th'], historic_range_df['10th'], color='skyblue', alpha=0.3, label='90-10 Percentile Range')
    ax2.fill_between(historic_range_df.index, historic_range_df['75th'], historic_range_df['25th'], color='steelblue', alpha=0.3, label='25-75 Percentile Range')
    ax2.plot(realtime_df.index, realtime_df.values, color='black', label='Real Time Gauge')
    if forecast_df is not None:
        ax2.plot(forecast_df.index, forecast_df.values, color='green', label='NSRPS Forecast')
    if forecast_bias_corrected_df is not None:
        ax2.plot(forecast_bias_corrected_df.index, forecast_bias_corrected_df.values, color='purple', label='NSRPS Forecast Bias Corrected')
    if analysis_df is not None:
        ax2.scatter(analysis_df.index, analysis_df.values, color='grey', label='NSRPS Analysis')
    ax2.set_title(f'{variable} for Real-Time and Forecasted Data, Station {station_number}')
    ax2.set_xlabel('Day of the Year')
    ax2.set_ylabel(variable)

    ax2.legend()
    ax2.grid(True)

    # Set the x-axis limits of the zoomed-in hydrograph to match the range of realtime_df_daily.index
    ax2.set_xlim(combined_index[0],)
    #Set lower y-axis limit to 0
    ax2.set_ylim(0,)

    plt.tight_layout()
    plt.show()

def plot_detailed_hydrograph(station_number,variable, historic_df, realtime_df, forecast_df=None,analysis_df=None, threshold_df=None,forecast_bias_corrected_df=None, save_png=False, png_path=None):

    historic_range_df = calculate_daily_percentiles_of_historic_data(historic_df,variable)

    realtime_daily_df = convert_to_daily_mean(realtime_df, variable)

    if forecast_df is not None:
        forecast_df = convert_to_daily_mean(forecast_df,'Discharge',date_col='time')

    if forecast_bias_corrected_df is not None:
        forecast_bias_corrected_df = convert_to_daily_mean(forecast_bias_corrected_df,'Discharge',date_col='time')

    if analysis_df is not None:
        analysis_df = convert_to_daily_mean(analysis_df,'Discharge',date_col='time')

    plot_annual_hydrograph_statistics(station_number, variable, historic_range_df, realtime_daily_df,forecast_df,analysis_df,threshold_df,forecast_bias_corrected_df, save_png, png_path)

    return None
