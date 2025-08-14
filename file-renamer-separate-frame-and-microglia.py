import pandas as pd

df = pd.read_csv('/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Filaments/Individual Stats/combined_Filament_No._Sholl_Intersections.csv')  # or pd.read_excel(...)
df.rename(columns={'MicrogliaID': 'Unique_ID'}, inplace=True)
df[['Frame', 'MicrogliaID']] = df['Unique_ID'].str.extract(r'Frame_(\d+)_(\d+)')
df['Frame'] = df['Frame'].astype(int)
df['MicrogliaID'] = df['MicrogliaID'].astype(int)
df.to_csv('/Users/alexlawson/Masters-Data-Final/Live-imaging/Results/Statistics/Filaments/Combined stats/Filament_No._Sholl_Intersections.csv', index=False)


