import unittest
import pickle
import geopy

import geopandas as gpd
import pandas as pd

from geocitysorter import census_incorporated_cities, main, uscb_cities, capital_cities, uscb_shapefiles

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


    def test_min_dist(self):
        gdf = gpd.read_file('../data/incorporated_cities_uscensus_min.json')
        states = ["North Carolina"]


    def test_images_for_readme(self):
        # df = census_incorporated_cities()
        # from importlib import resources as impresources
        # from . import templates

        # gdf = gpd.read_file('../data/incorporated_cities_uscensus.json')
        gdf = uscb_cities()

        # states = ["Colorado"]
        # states = ["South Dakota"]
        # states = ["Alabama"]
        # states = ["Michigan"]
        # states = ["Kentucky"]
        states = ["Kentucky"]
        # states = ["California"]
        # states = ["Texas", 'Oklahoma']
        # states = ["California", 'Nevada']
        # states = ["North Carolina", 'South Carolina']
        # states = ["Texas"]
        # states = ["Minnesota"]
        # states = ["Wyoming"]
        # states = ["North Carolina"]

        crs = "EPSG:4326"
        picklefilename='_'.join(states)
        try:
            with open(f'cache/{picklefilename}.pkl', 'rb') as fp:
                gdf_orderd = pickle.load(fp)
        except:
            gdf = gdf[gdf.state.isin(states)]

            gdf.sort_values(by=['city', 'state', 'population'], ascending=False, inplace=True)
            gdf.drop_duplicates(subset=["city", "state"], keep="first", inplace=True)  # when capital is the larget city
            gdf_orderd=main(gdf, verbose=True, first='both', rings=2)

            gdf['dist']=None  # the function adds this
            gdf['ratio']=None  # the function adds this
            # self.assertEqual(gdf.shape,gdf_orderd.shape)
            gdf_orderd= gpd.GeoDataFrame(gdf_orderd, crs=gdf.crs, geometry=gdf_orderd.geometry)
            gdf_orderd.to_crs(crs, inplace=True)
            gdf_orderd.reset_index(inplace=True)

            with open(f'cache/{picklefilename}.pkl', 'wb') as fp:
                pickle.dump(gdf_orderd, fp)
                print(f"dumped cache of {gdf_orderd.shape[0]} for {picklefilename}")


        us = uscb_shapefiles()
        us.to_crs(crs, inplace=True)
        if gdf_orderd.crs != 'EPSG:4326':
            print("warning, assuming World Geodetic System 1984 (WGS-84)")

        # dist between western and eastern most cities.
        city_bounds = gdf_orderd.total_bounds
        width_km = geopy.distance.geodesic( (city_bounds[1], city_bounds[0]), (city_bounds[3], city_bounds[2]), ellipsoid='WGS-84').km
        print(gdf_orderd)

        numcities=min(20,gdf_orderd.shape[0])
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
        us[us.NAME.isin(states)].plot(ax=ax, color="lightblue", edgecolor='k')
        fig.tight_layout()
        ax.axis('off')
        gdf_orderd['marker_size']= 50*(gdf_orderd.population / gdf_orderd.population.max())+10

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
        ax.axis('off')
        us[us.NAME.isin(states)].plot(ax=ax, color="lightblue", edgecolor='grey')

        df_o=gdf_orderd[(gdf_orderd.dist > width_km/10)|(gdf_orderd.dist.isna())]
        numcities=df_o.shape[0]
        print(df_o)
        # df_o.plot(ax=ax, markersize=df_o.marker_size, color='k')
        df_o.plot(ax=ax, markersize= 20, color='k')
        plt.title(f'by geopopulation')
        for x, y, label in zip(df_o.geometry.x, df_o.geometry.y, df_o.city):
            ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
        plt.savefig('foo_2.png', dpi=300)
        plt.savefig(f'../images/{"_".join(states)}_geopop.png', dpi=300)



        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 9))
        ax.axis('off')
        us[us.NAME.isin(states)].plot(ax=ax, color="lightblue", edgecolor='grey')
        df_u=gdf_orderd.sort_values(by='population', ascending=False).head(numcities)
        df_u.plot(ax=ax, markersize=20, color='k')
        for x, y, label in zip(df_u.geometry.x, df_u.geometry.y, df_u.city):
            ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
        plt.title(f'by population')
        plt.savefig('foo_3.png', dpi=300)
        plt.savefig(f'../images/{"_".join(states)}_pop.png', dpi=300)


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
