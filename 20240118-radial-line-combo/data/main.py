import pandas as pd
import numpy as np
import datetime

# Generate date range for the current year
current_year = datetime.datetime.now().year - 1
start_date = f'{current_year}-01-01'
end_date = f'{current_year}-12-31'
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Generate synthetic weather data with seasonality
weather_data = {
    'Date': date_range,
    'Temperature': np.random.normal(loc=25, scale=5, size=len(date_range)),  # Hotter summers
    'Precipitation': np.random.uniform(0, 5, size=len(date_range))
}

# Convert the weather_data dictionary to a DataFrame
weather_df = pd.DataFrame(weather_data)

# Simulate seasonality for winter months (colder temperatures)
winter_months = [12, 1, 2]
weather_df.loc[weather_df['Date'].dt.month.isin(winter_months), 'Temperature'] -= 15  # More substantial decrease for colder winters

# Generate synthetic energy consumption data with seasonality
energy_data = {
    'Date': date_range,
    'EnergyConsumption': np.random.normal(loc=100, scale=10, size=len(date_range))
}

# Convert the energy_data dictionary to a DataFrame
energy_df = pd.DataFrame(energy_data)

# Simulate seasonality for peak winter and peak summer months
peak_winter_months = [12, 1]
peak_summer_months = [6, 7]
energy_df.loc[energy_df['Date'].dt.month.isin(peak_winter_months), 'EnergyConsumption'] += 20
energy_df.loc[energy_df['Date'].dt.month.isin(peak_summer_months), 'EnergyConsumption'] += 10

# Merge the datasets on the 'Date' column
merged_df = pd.merge(weather_df, energy_df, on='Date')

# Set time component to midnight
merged_df['Date'] = merged_df['Date'].dt.floor('D')

# Set time to the beginning of the day
merged_df['Date'] += pd.to_timedelta('00:00:01')

# Extract date-related information
merged_df['DayNumber'] = merged_df['Date'].dt.dayofweek

# Calculate WeekNumber
merged_df['WeekNumber'] = merged_df['Date'].dt.strftime('%W').astype(int) + 1

# Extract month-related information
merged_df['MonthNumber'] = merged_df['Date'].dt.month
merged_df['MonthName'] = merged_df['Date'].dt.month_name()

# Save the dataset to a CSV file
merged_df.to_csv('current_year_weather_energy_dataset.csv', index=False)
