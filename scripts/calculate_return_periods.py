import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculate_return_periods(realtime_df, forecast_df, threshold_df, station_number):

    merged_df = pd.concat([realtime_df, forecast_df])
    station_data = merged_df[merged_df['STATION_NUMBER'] == station_number]

    # Initialize a result dataframe
    result = pd.DataFrame(index=station_data.index)

    # Extract threshold values for the specified station
    station_thresholds = threshold_df[['T_yrs', station_number]].sort_values(by='T_yrs', ascending=False)

    # Check exceedance
    for datetime, row in station_data.iterrows():
        discharge = row['DISCHARGE']
        exceeded_thresholds = station_thresholds[station_thresholds[station_number] <= discharge]['T_yrs']
        max_exceeded_threshold = exceeded_thresholds.max() if not exceeded_thresholds.empty else 'Less than 2 year'
        result.at[datetime, 'Exceedance'] = max_exceeded_threshold

    return result

def plot_exceedance(result,station):
    # Predefined set of colors
    color_map = {
        'Less than 2 year': 'green',
        2: 'green',       # 2-year threshold color
        5: 'yellow',     # 5-year threshold color
        10: 'orange',    # 10-year threshold color
        20: 'red',       # 20-year threshold color
        50: 'purple',    # 50-year threshold color
        100: 'black'     # 100-year threshold color
        # Add more colors if there are more thresholds
    }

    # Handle any unspecified statuses by a default color
    default_color = 'gray'

    # Plotting
    plt.figure(figsize=(12, 6))
    for status in result['Exceedance'].unique():
        color = color_map.get(status, default_color)
        to_plot = result[result['Exceedance'] == status]
        plt.scatter(to_plot.index, np.full(to_plot.shape[0], status), color=color, label=status)

    plt.xlabel('DateTime')
    plt.ylabel('Return Period')
    plt.title(f'Return Period Plot for Station {station}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

