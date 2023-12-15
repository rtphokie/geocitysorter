import unittest

import geopandas as gpd
import pandas as pd

from geocitysorter import census_incorporated_cities, main

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


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

    def test_census(self):
        gdf = census_incorporated_cities()
        self.assertEqual(19820, gdf.shape[0])
        gdf.to_file('../data/incorporated_cities_uscensus.json', driver="GeoJSON")
        gdf_lower48 = gdf[~gdf.state.isin(['Alaska', 'Hawaii', 'Puerto Rico'])]
        gdf_lower48.to_file('../data/incorporated_cities_uscensus_lower48.json', driver="GeoJSON")
        gdf_lower48[gdf_lower48.population >= 10000].to_file('../data/incorporated_cities_uscensus_min.json',
                                                             driver="GeoJSON")

    @unittest.skip('expensive')
    def test_plot(self):
        gdf = gpd.read_file('../data/incorporated_cities_uscensus_min.json')
        gdf.sort_values(by=['population'], inplace=True, ascending=False)
        self.assertEqual(3198, gdf.shape[0])
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
        # gdf[gdf.state=='North Carolina'].plot(ax=ax)
        gdf.plot(ax=ax)
        plt.show()
        #     gdf_cities_to_plot[(gdf_cities_to_plot.population <= 15000) & (gdf_cities_to_plot.population > 10000)].plot(ax=ax, color='pink')

        print(gdf)


    def test_VANC(self):
        # df = census_incorporated_cities()
        import geopandas as gpd
        gdf = gpd.read_file('../data/incorporated_cities_uscensus_min.json')

        states = ["North Carolina"]
        gdf = gdf[gdf.state.isin(states)]
        gdf_orderd=main(gdf, verbose=True, first='capital', rings=5)
        gdf_orderd.to_csv('aaaa_5.csv')
        self.assertEqual(gdf.shape,gdf_orderd.shape)
        print(gdf_orderd)
        crs = "EPSG:4326"
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
        fig.tight_layout()
        ax.axis('off')
        gdf_orderd.plot(ax=ax, markersize=1, color='k')
        plt.savefig('foo.png', dpi=300)




    def test_VANC(self):
        # df = census_incorporated_cities()
        import geopandas as gpd
        gdf = gpd.read_file('../data/incorporated_cities_uscensus_min.json')

        states = ["North Carolina","Virginia"]
        gdf = gdf[gdf.state.isin(states)]
        gdf_orderd=main(gdf, verbose=True, first='capital', rings=5)
        gdf_orderd.to_csv('aaaa_5.csv')
        self.assertEqual(gdf.shape,gdf_orderd.shape)
        print(gdf_orderd)
        return
        crs = "EPSG:4326"
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
        fig.tight_layout()
        ax.axis('off')
        gdf_orderd.plot(ax=ax, markersize=1, color='k')
        plt.savefig('foo.png', dpi=300)


        import geopandas as gpd
        # gdf_orderd = gpd.GeoDataFrame(gdf_orderd, geometry=gpd.points_from_xy(gdf_orderd.longitude, gdf_orderd.latitude), crs=crs)
        # print(gdf_orderd)
        # import os
        # os.makedirs('../data', exist_ok=True)
        # gdf.to_file('../data/cities_uscb.json', driver="GeoJSON")


#
#     # build geopandas dataframe of US States from Census Bureau shape files
#     gdf_us = gpd.read_file('cache/cb_2018_us_state_20m/cb_2018_us_state_20m.shp')
#     fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
#     pd.set_option('display.max_columns', None)
#     gdf_lower48=gdf_us[~gdf_us.STUSPS.isin(['AK', 'HI', 'PR'])]
#
# #     plt.savefig('foo.png')
#

if __name__ == '__main__':
    unittest.main()
