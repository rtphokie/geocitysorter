import geopy.distance
import pandas as pd

from .census import census_incorporated_cities
from .populations import get_census_data

pd.set_option('display.max_rows', None)


# https://packaging.python.org/en/latest/tutorials/packaging-projects/
#

def main(df, rings=5, order='furthest', valuecolumn='population'):
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

    This is not an efficient routine


    :param df:   Pandas (or GeoPandas) dataframe containing at minimum: city, state, population, latitude, longitude
                  columns
                  todo: optionally derive latitude and longitude columns from centroid of geometry column in
                        GeoPandas dataframe
                  todo: value column as an option, defaulted to population
    :param rings: number of rings to logically draw around each city when generalizing distance between a given city and
                  the others that have already been ordered as more "relevant".  (default: 5)
    :param order: how the next point is selected
                  furthest: the most populous city in the furthest ring, useful for intelligently ordering
                            points on a map by population (the point of this function)
                  nearest: the most populous city in the nearest ring, useful for finding the most relevant
                           point "near" a given point such as the largest city nearby
                  central: the most populous city in the middle ring, seemed a useful option to include

    :return: ordered pandas (or geopandas) dataframe
    '''

    if 'city' not in df.columns or 'state' not in df.columns:
        raise ValueError(f"expected city and state columns")


    df.sort_values(by=valuecolumn, ascending=False, inplace=True)
    df['id'] = df.city + df.state + df.population.astype(str)  # unique identifier

    if order == 'furthest':
        df_ordered = pd.DataFrame([df.iloc[0]])
    elif order == 'nearest':
        raise ValueError(f"{order} ordering not yet implemented")
    elif order == 'central':
        raise ValueError(f"{order} ordering not yet implemented")
    else:
        raise ValueError(f"{order} not supported, please specify one of nearest (default), furthest, or central")


    df_distances = pd.DataFrame()
    while df.shape[0] > 0:
        # remove cities already ordered from the todo list, and the running list of distances to cities yet to be ordered
        df = df[~df.id.isin(df_ordered.id.unique())]
        if df_distances.shape[0] > 0:
            df_distances = df_distances[~df_distances.id.isin(df_ordered.id.unique())]

        print(df.shape[0], df_distances.shape[0], df_ordered.shape[0])

        # calculated distance to the remaining cities from the one most recently added to the ordered list
        labeled_row=df_ordered.iloc[-1]
        # find distances to each of the remaining cities from the cities that have already been ordered
        df['dist'] = df.apply(lambda row: geopy.distance.geodesic((labeled_row['latitude'], labeled_row['longitude']),
                                                                    (row['latitude'], row['longitude']),
                                                                    ellipsoid='WGS-84').km, axis=1)
        # add those distances to this already ordered point to the scratchpad
        df_distances = pd.concat([df_distances, df])
        df_scratchpad = df_distances.copy()
        if order =='furthest':
            df_scratchpad.sort_values(by=['city', 'state','dist'], ascending=True, inplace=True)
            df_scratchpad = df_scratchpad.drop_duplicates(subset=["city", "state"], keep="first")
        else:
            raise ValueError(f"{order} not supported, please specify one of nearest (default), furthest, or central")

        df_scratchpad['ringnumber']=None


        # find width of the rings by dividing the furthest point by the number of rings
        furthest= df.dist.max()
        ringwidth = furthest / rings

        # convert that distance to a numbered ring (bin), larger ring numbers are further away
        # round function forces a single ring
        df_scratchpad.ringnumber = round( df_scratchpad.dist / ringwidth)

        df_scratchpad.sort_values(by=['ringnumber',valuecolumn], ascending=False, inplace=True)

        if order == 'furthest':
            furthest_most_populous_row = df_scratchpad.iloc[0]
        elif order == 'nearest':
            raise ValueError(f"{order} ordering not yet implemented")
        elif order == 'central':
            raise ValueError(f"{order} ordering not yet implemented")
        else:
            raise ValueError(f"{order} not supported, please specify one of nearest (default), furthest, or central")

        # append most populous city in outer most ring to ordered list
        df_ordered = pd.concat([df_ordered, pd.DataFrame( [furthest_most_populous_row])])
        df = df[~df.id.isin(df_ordered.id.unique())]

        # print(f"adding {furthest_most_populous_row.city} {df_ordered.shape[0]}/{df.shape[0]}")
        # remove that row from the todolist


    return (df_ordered.drop(columns=['ringnumber', 'dist']))
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
