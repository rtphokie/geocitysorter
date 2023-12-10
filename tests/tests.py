import os
import numpy as np
import geopandas as gpd
import unittest
import pandas as pd
# import zipfile
# import pickle
import matplotlib.pyplot as plt
from geocitysorter import download_file, get_census_data

import requests


# https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_region_20m.zip

#
# def download_file(url):
#     os.makedirs('cache', exist_ok=True)
#     local_filename = f"cache/{os.path.basename(url)}"
#     local_extraction_dir = f"cache/{os.path.splitext(os.path.basename(os.path.basename(url)))[0]}"
#
#     if not os.path.exists(local_filename):
#         response = requests.get(url)
#
#         if response.status_code == 200:
#             print(local_filename)
#             with open(local_filename, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=1024):
#                     if chunk:
#                         f.write(chunk)
#             print(f'downloaded {local_filename} from {url}')
#     if local_filename.endswith('.zip') and not os.path.exists(local_extraction_dir):
#         with zipfile.ZipFile(local_filename, 'r') as zip_ref:
#             zip_ref.extractall(local_extraction_dir)
#

class SomeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(SomeTest, cls).setUpClass()
        # os.system('cd ..; python3 -m build --wheel')

    def setUp(self):
        # US states, from Census Bureau
        download_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip')
        #https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2020-2022/SUB-EST2022.pdf
        # download_file('https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv')
        download_file('https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv')

    def testuscbcities(self):
        df = get_census_data()
        print(df.columns)
        self.assertEqual(19466, df.shape[0])  # this is the

    def testcoords(self):


    # def test_one(self):
    #
    #     # build geopandas dataframe of US States from Census Bureau shape files
    #     gdf_us = gpd.read_file('cache/cb_2018_us_state_20m/cb_2018_us_state_20m.shp')
    #     fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
    #     pd.set_option('display.max_columns', None)
    #     gdf_lower48=gdf_us[~gdf_us.STUSPS.isin(['AK', 'HI', 'PR'])]
    #
    #     df_cb = pd.read_csv('cache/sub-est2022.csv')
    #     df_cb['settlement']=np.nan
    #     df_cb['name']=np.nan
    #     df_cb = df_cb[df_cb.PLACE >0]  # filter out state and county populations
    #     df_cb = df_cb[df_cb.COUNTY ==0]  # filter out partial populations of cities and towns that extend into multiple counties
    #     df_cb = df_cb[~df_cb.NAME.str.endswith(' government')]  # filter out partial populations of cities and towns that extend into multiple counties
    #     df_cb = df_cb[~df_cb.NAME.str.endswith(' (balance)')]  # filter out partial populations of cities and towns that extend into multiple counties
    #     df_cb = df_cb[~df_cb.NAME.str.endswith(' County')]  # filter out partial populations of cities and towns that extend into multiple counties
    #     df_cb = df_cb[~df_cb.NAME.str.startswith('Balance of ')]  # filter out partial populations of cities and towns that extend into multiple counties
    #     df_cb.NAME.replace('Ranson corporation', 'Ranson city', inplace=True)
    #     df_cb.NAME.replace('Princeton', 'Princeton municipality', inplace=True) # make name consistent
    #     df_cb.NAME.replace('Carson City', 'Carson City city', inplace=True) # make name consistent
    #
    #     df_cb['settlement'] = df_cb.NAME.str.rsplit(' ').str[-1]
    #     df_cb['name'] = df_cb.NAME.str.rsplit(' ').str[:-1].str.join(' ')
    #     df_cb['dupe'] = df_cb.duplicated(subset=['NAME', 'STNAME'])
    #     df_cb = df_cb[(df_cb.dupe == False) | ((df_cb.dupe == True) & (df_cb.CONCIT == 0))] # keep the colsolidated city if present
    #     df_cb['dupe'] = df_cb.duplicated(subset=['NAME', 'STNAME'])  # recheck for duplicate rows
    #     df_cb = df_cb[df_cb.dupe == False] # dropping duplicate village of Oakwood, Ohio. Unclear why there are two entries with different placeids in Census data.
    #
    #     df = df_cb[df_cb.STNAME=='North Carolina']
    #     df=df[['NAME', 'STATE', 'POPESTIMATE2022']]
    #     df.sort_values(by='POPESTIMATE2022', inplace=True)
    #
    #     print(df)
    #     pass
    #
    #     # build geopandas dataframe cities from simplemaps.com data
    #     # CSV file must have city name, state name, latitude, longitude and unique ID columns
    #     # df_cities = pd.read_csv('cache/simplemaps_uscities_basicv1.77/uscities.csv')
    #     # gdf_cities = gpd.GeoDataFrame(df_cities, geometry=gpd.points_from_xy(df_cities.lng, df_cities.lat),  crs="EPSG:4326")
    #     # gdf_cities=gdf_cities[~gdf_cities.state_id.isin(['AK', 'HI', 'PR'])]
    #     # gdf_cities=gdf_cities[gdf_cities.population > 10]
    #     # gdf_cities=gdf_cities.sort_values(by='population', ascending=False)
    #     # gdf_cities=gdf_cities.to_crs(gdf_us.crs)
    #
    #     # plot it
    #     gdf_states=gdf_us[gdf_us.STUSPS.isin(['VA', 'NC', 'SC'])]
    #     # gdf_cities_to_plot=gdf_cities[gdf_cities.state_id.isin(['VA', 'NC', 'SC'])]
    #     # gdf_states.plot(ax=ax, edgecolor='k', color='w', alpha=.3 )
    #
    #
    #
    #     print(gdf_cities_to_plot)
    #     print(gdf_cities_to_plot[['city', 'state_id', 'population', 'density']])
    #
    #     biggestcityrow = gdf_cities_to_plot.loc[gdf_cities_to_plot['population'].idxmax()]
    #
    #     gdf_cities_by_georelevance = gdf_cities_to_plot[gdf_cities_to_plot.id == biggestcityrow.id]
    #     gdf_cities_to_plot=gdf_cities_to_plot[~gdf_cities_to_plot.id.isin(gdf_cities_by_georelevance.id.unique())]
    #
    #
    #     gdf_cities_to_plot[gdf_cities_to_plot.population >= 100000].plot(ax=ax, color='r')
    #     gdf_cities_to_plot[(gdf_cities_to_plot.population > 50000) & (gdf_cities_to_plot.population < 100000)].plot(ax=ax, color='y')
    #     gdf_cities_to_plot[(gdf_cities_to_plot.population <= 25000) & (gdf_cities_to_plot.population > 20000)].plot(ax=ax, color='g')
    #     gdf_cities_to_plot[(gdf_cities_to_plot.population <= 20000) & (gdf_cities_to_plot.population > 15000)].plot(ax=ax, color='b')
    #     gdf_cities_to_plot[(gdf_cities_to_plot.population <= 15000) & (gdf_cities_to_plot.population > 10000)].plot(ax=ax, color='pink')
    #     plt.savefig('foo.png')



if __name__ == '__main__':
    unittest.main()
