import os

import pandas as pd
import geopandas as gpd
from tqdm import tqdm

from .populations import get_census_data
from .census import census_incorporated_cities


# https://packaging.python.org/en/latest/tutorials/packaging-projects/
#

def main():
    # df = census_incorporated_cities()
    import geopandas as gpd
    gdf = gpd.read_file('../data/incorporated_cities_uscensus_min.json')
    gdf=gdf[gdf.STATE=='North Carolina']
    gdf.sort_values(by='POPULATION', ascending=False, inplace=True)
    gdf['id']=gdf.CITY+gdf.STATE+gdf.POPULATION.astype(str)

    gdf_ordered=pd.DataFrame([gdf.iloc[0]])
    gdf=gdf[~gdf.id.isin(gdf_ordered.id.unique())]

    for id,lng,lat in zip(gdf_ordered.id, gdf_ordered.longitude, gdf_ordered.latitude ):
        print(id,lng,lat)
    # while gdf.shape[0] > 0:
    #     gdf




    # df_cb = get_census_data()
    # # # df_cb=df_cb.sort_values(by='name_long', ascending=False)
    # #
    # # df = df_cb[df_cb.population >= 100]
    # # pbar = tqdm(total=df.shape[0])
    # #
    # # georesults={}
    # # for n, row in df.iterrows():
    # #     pbar.set_description(row['name_long'])
    # #     pbar.update(1)
    # #     data = _geocode(row['name_long'])
    # #     if data is not None:
    # #         georesults[row['name_long']]={ 'lat': data['lat'], 'lng': data['lng'] }
    # #     else:
    # #         print(f" no data for {row['name_long']}")
    # #     # except:
    # #     #     pass
    # # df_coords = pd.DataFrame.from_dict(georesults, orient='index').reset_index()
    # # df_coords.rename(columns={'index': 'name_long'}, inplace=True)
    # # print('pop', df.shape)
    # # print('coords', df_coords.shape)
    # #
    # # df = pd.merge(df, df_coords, on="name_long")
    # print('merge', df.shape)
    #
    # crs = "EPSG:4326"
    # import geopandas as gpd
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat), crs=crs)
    # print(gdf)
    # os.makedirs('../data', exist_ok=True)
    # gdf.to_file('../data/cities_uscb.json', driver="GeoJSON")
    #
    #
