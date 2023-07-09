import pandas as pd
import requests
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as mplPolygon
from cartopy.mpl.geoaxes import GeoAxes
from metpy.plots import USCOUNTIES
import datetime
from shapely.geometry import shape

tor_url = 'https://www.spc.noaa.gov/climo/reports/230226_rpts_filtered_torn.csv'
df_tor = pd.read_csv(tor_url)

hail_url = 'https://www.spc.noaa.gov/climo/reports/230226_rpts_hail.csv'
df_hail = pd.read_csv(hail_url)

wind_url = 'https://www.spc.noaa.gov/climo/reports/230226_rpts_wind.csv'
df_wind = pd.read_csv(wind_url)

for i in range(len(df_wind['Speed'])):
    value = df_wind['Speed'][i]
    if value != 'UNK':
        try:
            df_wind['Speed'][i] = float(value)
        except ValueError:
            df_wind['Speed'][i] = np.nan

url = 'https://mesonet.agron.iastate.edu/api/1/cow.json?wfo=OUN&begints=2023-02-26T12:00:00Z&endts=2023-02-27T12:00:00Z&hailsize=1&wind=58&phenomena=TO&phenomena=SV&phenomena=MA&phenomena=FF&phenomena=DS&lsrbuffer=15&warningbuffer=1'
response = requests.get(url)
data = response.json()

events = data['events']['features']
warning_data = []

for event in events:
    properties = event['properties']
    geometry = event['geometry']
    id = event['id']
    year = properties['year']
    wfo = properties['wfo']
    phenomena = properties['phenomena']
    eventid = properties['eventid']
    issue = properties['issue']
    expire = properties['expire']
    statuses = properties['statuses']
    fcster = properties['fcster']
    significance = properties['significance']
    parea = properties['parea']
    ar_ugcname = properties['ar_ugcname']
    status = properties['status']
    stormreports = properties['stormreports']
    stormreports_all = properties['stormreports_all']
    verify = properties['verify']
    lead0 = properties['lead0']
    areaverify = properties['areaverify']
    sharedborder = properties['sharedborder']

    warning_data.append([id, year, wfo, phenomena, eventid, issue, expire, statuses, fcster, significance,
                         parea, ar_ugcname, status, stormreports, stormreports_all, verify, lead0, areaverify,
                         sharedborder, geometry])

df = pd.DataFrame(warning_data, columns=['id', 'year', 'wfo', 'phenomena', 'eventid', 'issue', 'expire', 'statuses',
                                         'fcster', 'significance', 'parea', 'ar_ugcname', 'status', 'stormreports',
                                         'stormreports_all', 'verify', 'lead0', 'areaverify', 'sharedborder',
                                         'geometry'])

fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertConformal(central_longitude=-97.5, central_latitude=35.5))
ax.set_extent([-100, -96, 34, 37])

ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'), alpha=.75)
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle=':', linewidth=0.5)
ax.add_feature(USCOUNTIES.with_scale('5m'), linewidth=0.25, alpha=0.5)

colors = {'SV': 'yellow', 'TO': 'red', 'FF': 'green', 'MA': 'orange', 'DS': 'brown'}
zorders = {'TO': 4, 'SV': 3, 'MA': 1}

for index, row in df.iterrows():
    geometry = row['geometry']
    event_id = row['eventid']
    if geometry:
        try:
            geom_obj = shape(geometry)
            ax.add_geometries([geom_obj], crs=ccrs.PlateCarree(), edgecolor='black', facecolor=colors.get(row['phenomena'], 'gray'), lw=1, alpha=0.75, zorder=zorders.get(row['phenomena'], 2))
            centroid = geom_obj.centroid
            #ax.text(centroid.x, centroid.y, str(event_id), transform=ccrs.PlateCarree(), fontsize=8, ha='center', va='center')
        except Exception as e:
            print(f"Error processing geometry at index {index}: {e}")


for i in range(len(df_wind['Speed'])):
    value = df_wind['Speed'][i]
    if value != 'UNK':
        try:
            df_wind['Speed'][i] = float(value)
        except ValueError:
            df_wind['Speed'][i] = np.nan

for index, row in df_hail.iterrows():
    if row['Size'] >= 200:
        ax.scatter(row['Lon'], row['Lat'], transform=ccrs.PlateCarree(), marker='^', c='black', alpha=0.9, s=150, zorder=2, label='Large Hail Report (2"+)')
    else:
        ax.scatter(row['Lon'], row['Lat'], transform=ccrs.PlateCarree(), c='green', alpha=0.9, s=150, zorder=2, label='Hail Report')

for index, row in df_wind.iterrows():
    if (row['Speed'] != 'UNK' and row['Speed'] > 65):
        ax.scatter(row['Lon'], row['Lat'], transform=ccrs.PlateCarree(), marker='s', c='black', alpha=0.9, s=150, zorder=2, label='High Wind Report (65KT+)')
    else:
        ax.scatter(row['Lon'], row['Lat'], transform=ccrs.PlateCarree(), c='blue', alpha=0.9, s=150, zorder=2, label='Wind Report')

ax.scatter(df_tor['Lon'].astype(float), df_tor['Lat'].astype(float), transform=ccrs.PlateCarree(), c='red', label='Tornado Reports', s=150, zorder=4)

handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
unique_handles = [handles[labels.index(label)] for label in unique_labels]
plt.legend(unique_handles, unique_labels, loc='upper right')


plt.title('NWS OUN WFO Warnings and SPC LSRs Valid for 2/26/2023')
plt.show()
