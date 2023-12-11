import os
from pprint import pprint
import numpy as np
import geopandas as gpd
import unittest
import pandas as pd
# import zipfile
# import pickle
import matplotlib.pyplot as plt
from geocitysorter import _download_file, get_census_data, get_city_coords, _geocode, main

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

import requests


# https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_region_20m.zip


class SomeTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        super(SomeTest, cls).tearDownClass()
        # os.system('pip uninstall -y geocitysorter')

    @classmethod
    def setUpClass(cls):
        super(SomeTest, cls).setUpClass()
        # os.system('cd ..; python3 -m build --wheel')
        # os.system('cd ..; pip install --upgrade dist/*whl')
        # os.system('cd ..; pip install --force-reinstall dist/*whl')

    def setUp(self):
        # US states, from Census Bureau
        _download_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip')
        _download_file('https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv')

    def testuscbcities(self):
        df = get_census_data()
        self.assertEqual(19466, df.shape[0])  # this is the
        print(df)

    def testcoords(self):
        df = get_city_coords()
        self.assertEqual(29880, df.shape[0])
        print(df)

    def testmerge(self):
        main()

    def testjkl(self):
        foo = _geocode('Credit River Township, Minnesota', use_cache=False)
        pprint(foo)


    def testgeocode(self):
        from pprint import pprint
        data = _geocode('Raleigh, NC')
        print(data['from_cache'])
        self.assertAlmostEqual(35.78, data['lat'], 2)
        self.assertAlmostEqual(-78.64, data['lng'], 2)
        self.assertTrue('Raleigh' in data['display_name'])
        data = _geocode('Raleigh, NC')
        self.assertTrue(data['from_cache'])

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
