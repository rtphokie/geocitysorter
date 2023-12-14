import geopy.distance
import pandas as pd

from .census import census_incorporated_cities
from .populations import get_census_data

pd.set_option('display.max_rows', None)


# https://packaging.python.org/en/latest/tutorials/packaging-projects/
#

def main(rings=5, order='furthest'):
    '''
    offers a tool to help identify the right points to label on a map, not just by population or distance, but a
    combination of the two.

    When labeling a map simply by population, labels for cities like Minneapolis and St. Paul Minnesota or Raleigh and
    Durham, North Carolina can overlap making them unreadable. Considering only population can create large gaps
    that could otherwise provide meaning (e.g. Barstow population 25k but in a largely empty part of the
    California desert)

    orders a geopaandas dataoframe distributing geographical locations by distance from other more "relevant" points
    not just by population (or any other value) but also distance.  This aids in labeling maps in away that prevents
    both crowding (preferring the largest of a closely group set of cities) and large gaps of nothing on the map.

    The most populous city is always ordered first.  Distances to the remaining cities is them calculated, then
    those distances are organized into numbered rings (0 to furthest point divided by the number of rings). The
    most populated city in the outer (or inner or mid, see the order option) is added next in the order.  This
    repeated until all cities are ordered.  Cities at the bottom are very close to the cities on the top.


    :param df:    Pandas (or GeoPandas) dataframe containing at minimum: city, state, population, latitude, longitude
                  columns
                  todo: optionally derive latitude and longitude columns from centroid of geometry column in
                        GeoPandas dataframe
                  todo: value column as an option, defaulted to population
    :param rings: number of rings to logically draw around each city when generalizing distance between a given city and
                  the others that have already been ordered as more "relevant".  (default: 5)
    :param order: how the next point is selected
                  furthest: the most populous city in the furthest ring
                  nearest: the most populous city in the nearest ring
                  mid: the most populous city in the middle ring

    :return: ordered pandas (or geopandas) dataframe
    '''
    # df = census_incorporated_cities()
    import geopandas as gpd
    gdf = gpd.read_file('../data/incorporated_cities_uscensus_min.json')
    gdf = gdf[gdf.state == 'North Carolina']
    gdf.sort_values(by='population', ascending=False, inplace=True)
    gdf['id'] = gdf.city + gdf.state + gdf.population.astype(str)  # unique identifier

    gdf_ordered = pd.DataFrame([gdf.iloc[0]])
    gdf = gdf[~gdf.id.isin(gdf_ordered.id.unique())]
    gdf['dist'] = 0

    # for id, lng, lat in zip(gdf_ordered.id, gdf_ordered.longitude, gdf_ordered.latitude):
    #     print(id, lng, lat)
    gdf_distances = pd.DataFrame()

    # find distances to each of the remaining cities from the cities that have already been ordered
    for n, labeled_row in gdf_ordered.iterrows():
        gdf['dist'] = gdf.apply(lambda row: geopy.distance.geodesic((labeled_row['latitude'], labeled_row['longitude']),
                                                                    (row['latitude'], row['longitude']),
                                                                    ellipsoid='WGS-84').km, axis=1)
        gdf_distances = pd.concat([gdf_distances, gdf])
    gdf_distances.sort_values(by='dist', ascending=False, inplace=True)

    # find width of the rings by dividing the furthest point by the number of rings
    ringwidth = gdf.iloc[0].dist / rings
    print(ringwidth)
    gdf_distances.dist = round(
        gdf_distances.dist / ringwidth)  # convert that distance to a numbered bin, larger are further away
    gdf_distances.sort_values(by=['dist', 'population'], ascending=False, inplace=True)
    furthest_most_populous_row = gdf_distances.iloc[0]
    print(f"adding {furthest_most_populous_row.city}")
    gdf_ordered = pd.concat([gdf_ordered, pd.DataFrame(
        [furthest_most_populous_row])])  # append most populous city in outer most ring to ordered list
    gdf = gdf[~gdf.id.isin(gdf_ordered.id.unique())]

    print(gdf_ordered)
    return (gdf_ordered)
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


def calcdist(coord1, coord2):
    dist = geopy.distance.geodesic(coord1, coord2, ellipsoid='WGS-84').km
    return dist
