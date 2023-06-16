import pandas as pd
from metpy.plots import USCOUNTIES
import cartopy.crs as ccrs
import cartopy. feature as cfeature
import matplotlib.pyplot as plt
import datetime

url = 'https://www.spc.noaa.gov/climo/reports/today_torn.csv'

df_tor = pd.read_csv(url)

url = 'https://www.spc.noaa.gov/climo/reports/today_hail.csv'

df_hail = pd.read_csv(url)

url = 'https://www.spc.noaa.gov/climo/reports/today_wind.csv'

df_wind = pd.read_csv(url)

mapcrs = ccrs.LambertConformal(central_longitude=-85.6, central_latitude=44.3, standard_parallels=(30, 60)) 
datacrs = ccrs.PlateCarree()
proj = ccrs.Stereographic(central_longitude=-85, central_latitude=40)

now = datetime.datetime.utcnow()
now = now.strftime("%m/%d/%Y %H:%M")

fig = plt.figure(figsize=(16,12))
ax = fig.add_subplot(1, 1, 1, projection=mapcrs)
ax.set_extent([-85.5, -82, 41.5, 44.0], datacrs)
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'), alpha = .75)
ax.add_feature(USCOUNTIES.with_scale('5m'), linewidth=0.25, alpha = 0.5)

for i in range(len(df_wind['Speed'])):
    value = df_wind['Speed'][i]
    if value != 'UNK':
        try:
            df_wind['Speed'][i] = float(value)
        except ValueError:
            df_wind['Speed'][i] = np.nan
        
for index, row in df_hail.iterrows():
    if row['Size'] >= 200:
        ax.scatter(row['Lon'], row['Lat'],transform=datacrs, marker='^', c='black', alpha=0.7, s = 150, label = 'Large Hail Report (2"+)')
    else:
        ax.scatter(row['Lon'], row['Lat'],transform=datacrs, c='green', alpha=0.7, s=150, label='Hail Report')

for index, row in df_wind.iterrows():
    if (row['Speed'] != 'UNK' and row['Speed'] > 65):
        ax.scatter(row['Lon'], row['Lat'],transform=datacrs, marker = 's', c='black', alpha=0.7, s=150, label='High Wind Report (65KT+)')
    else:
        ax.scatter(row['Lon'], row['Lat'],transform=datacrs, c='blue', alpha=0.7, s=150, label='Wind Report')

ax.scatter(df_tor['Lon'].astype(float), df_tor['Lat'].astype(float), transform=datacrs, c='red', label='Tornado Reports', s = 150)

handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
unique_handles = [handles[labels.index(label)] for label in unique_labels]
ax.legend(unique_handles, unique_labels)

plt.title('SPC LSR valid for ' + str(now) +' UTC')
