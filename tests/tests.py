import pickle
import unittest

import geopandas as gpd
import geopy
import pandas as pd

from geocitysorter import census_incorporated_cities, order_geo_dataframe, cities_us, capital_cities, uscb_shapefiles

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_region_20m.zip

class TestDataFiles(unittest.TestCase):
    def test_capitals(self):
        gpd = capital_cities()
        self.assertEqual(gpd.shape[0], 96)
        self.assertTrue('Austin' in list(gpd.city))  # US
        self.assertTrue('Oaxaca de Juarez' in list(gpd.city))  # Mexico
        self.assertTrue('Yellowknife' in list(gpd.city))  # Canada

    def test_cities(self):
        gpd = cities_us()
        self.assertEqual(gpd.shape[0], 19820)
        self.assertTrue('geometry' in gpd.columns)
        self.assertTrue('city' in gpd.columns)
        self.assertTrue('state' in gpd.columns)


class SomeTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        super(SomeTest, cls).tearDownClass()
        # os.system('pip uninstall -y geocitysorter')

    @classmethod
    def setUpClass(cls):
        super(SomeTest, cls).setUpClass()
        # get info on all US cities once, use it across multiple tests
        cls.gdf_us = census_incorporated_cities()

        # os.system('cd ..; python3 -m build --wheel')
        # os.system('cd ..; pip install --upgrade dist/*whl')
        # os.system('cd ..; pip install --force-reinstall dist/*whl')

    @unittest.skip('used only to generate JSON files once')
    def test_create_json_files(self):
        gdf = census_incorporated_cities()

        self.assertEqual(19820, gdf.shape[0])
        gdf.to_file('../data/incorporated_cities_uscensus.json', driver="GeoJSON")
        gdf_lower48 = gdf[~gdf.state.isin(['Alaska', 'Hawaii', 'Puerto Rico'])]
        gdf_lower48.to_file('../data/incorporated_cities_uscensus_lower48.json', driver="GeoJSON")
        gdf_lower48[gdf_lower48.population >= 10000].to_file('../data/incorporated_cities_uscensus_min.json',
                                                             driver="GeoJSON")

    def test_NC(self):
        gdf = self.gdf_us[self.gdf_us.state == 'North Carolina']
        gdf_ordered = order_geo_dataframe(gdf)
        self.assertEqual(gdf.shape[0], gdf_ordered.shape[0])

        first_10_cities = list(gdf_ordered.city[:10])
        for x in ['Charlotte', 'Raleigh', 'Murphy', 'Boone', 'Kill Devil Hills']:
            self.assertTrue(x in first_10_cities, f'expected {x} in first 10 cities')

    def test_CA(self):
        gdf = self.gdf_us[self.gdf_us.state == 'California']
        gdf_ordered = order_geo_dataframe(gdf)
        self.assertEqual(gdf.shape[0], gdf_ordered.shape[0])

        first_10_cities = list(gdf_ordered.city[:10])
        for x in ['Los Angeles', 'Sacramento', 'Salinas', 'Needles', 'Crescent City']:
            self.assertTrue(x in first_10_cities, f'expected {x} in first 10 cities')

    def test_WY(self):
        gdf = self.gdf_us[self.gdf_us.state == 'Wyoming']
        gdf_ordered = order_geo_dataframe(gdf)
        self.assertEqual(gdf.shape[0], gdf_ordered.shape[0])

        first_10_cities = list(gdf_ordered.city[:10])
        for x in ['Cheyenne', 'Evanston', 'Jackson', 'Sundance', 'Green River']:
            self.assertTrue(x in first_10_cities, f'expected {x} in first 10 cities')


if __name__ == '__main__':
    unittest.main()
