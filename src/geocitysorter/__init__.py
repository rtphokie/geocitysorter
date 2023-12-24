import geopandas as gpd
import geopy.distance
import pandas as pd
import pkg_resources
from tqdm import tqdm

from .census import census_incorporated_cities
from .populations import get_census_data
from .geocitysorter import cities_us, capital_cities, uscb_shapefiles, order_geo_dataframe, calcdist

resource_package = __name__
# pd.set_option('display.max_rows', None)
#
#
# def cities_us():
#     resource_path = '/'.join(('geodata', 'incorporated_cities_uscensus.json'))  # Do not use os.path.join()
#     inp_file = pkg_resources.resource_stream(resource_package, resource_path)
#     return gpd.read_file(inp_file)
#
#
# def capital_cities():
#     resource_path = '/'.join(('geodata', 'capitals.csv'))  # Do not use os.path.join()
#     inp_file = pkg_resources.resource_stream(resource_package, resource_path)
#     return pd.read_csv(inp_file, on_bad_lines='skip', encoding='utf8')
#
#
# def uscb_shapefiles():
#     # download from https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
#     resource_path = '/'.join(
#         ('geodata', 'cb_2018_us_state_500k', 'cb_2018_us_state_500k.shp'))  # Do not use os.path.join()
#     inp_file = pkg_resources.resource_stream(resource_package, resource_path)
#     return gpd.read_file(inp_file.name)
#
#
# # https://packaging.python.org/en/latest/tutorials/packaging-projects/
# #
#
# def order_geo_dataframe(df_orig, rings=5, order='furthest', valuecolumn='population', starting_lat=None,
#                         starting_lng=None, verbose=False, first='both', citylist=[]):
#     '''
#     offers a tool to help identify the right points to label on a map, not just by population or distance, but a
#     combination of the two.
#
#     When labeling a map simply by population, labels for cities like Minneapolis and St. Paul Minnesota or Raleigh and
#     Durham, North Carolina can overlap making them unreadable. Considering only population can create large gaps
#     that could otherwise provide meaning (e.g. Barstow population 25k but in a largely empty part of the
#     California desert)
#
#     orders a geopaandas dataoframe distributing geographical locations by distance from other more "relevant" points
#     not just by population (or any other value) but also distance.  This aids in labeling maps in away that prevents
#     both crowding (preferring the largest of a closely group set of cities) and large gaps of nothing on the map.
#
#     The most populous city is always ordered first.  Distances to the remaining cities is them calculated, then
#     those distances are organized into numbered rings (0 to furthest point divided by the number of rings). The
#     most populated city in the outer (or inner or mid, see the order option) is added next in the order.  This
#     repeated until all cities are ordered.  Cities at the bottom are very close to the cities on the top.
#
#     This is not an efficient routine.  It calculates distance between n points ~(n^2/2) times
#
#
#     :param df_orig: Pandas (or GeoPandas) dataframe containing at minimum: city, state, population, latitude,
#                     longitude columns
#                     todo: optionally derive latitude and longitude columns from centroid of geometry column in
#                           GeoPandas dataframe
#                     todo: value column as an option, defaulted to population
#     :param rings:   number of rings to logically draw around each city when generalizing distance between a given city and
#                     the others that have already been ordered as more "relevant".  (default: 5)
#                     fewer rings favor larger cities
#     :param order:   how the next point is selected
#                     furthest: the most populous city in the furthest ring, useful for intelligently ordering
#                               points on a map by population (the point of this function)
#                     nearest: the most populous city in the nearest ring, useful for finding the most relevant
#                              point "near" a given point such as the largest city nearby
#     :param first:   capital: order state capitals first
#                     largest: order the largest city first (default)
#     :poram citylist: list of cities to include at top of resulting list
#
#     :return: ordered pandas (or geopandas) dataframe with two additional columns:
#              dist: kilometers to the closest city in the list above.
#     '''
#
#     if 'city' not in df_orig.columns or 'state' not in df_orig.columns:
#         raise ValueError(f"expected city and state columns in dataframe passed")
#     if first not in ['capital', 'largest', 'both']:
#         raise ValueError(
#             f"{first} not supported for as the first city to include, please specify capital (default) or largest")
#
#     df = df_orig.copy()  # we'll be chewing this dataframe down to nothing as we iterate, let's work on a copy
#     df.sort_values(by=[valuecolumn], ascending=False, inplace=True)
#     df.drop_duplicates(subset=["city", "state"], keep="first", inplace=True)  # when capital is the larget city
#     orig_rows = df.shape[0]
#     if df.shape[0] != df_orig.shape[0]:
#         raise Exception(f"dataframe has {df_orig.shape[0] - df.shape[0]} duplicate rows.")
#     # df.set_index(['city', 'state'], inplace=True)
#     df['id'] = df.city + df.state
#     df.sort_values(by=[valuecolumn], ascending=False, inplace=True)
#
#     df_ordered = df[df.city.isin(citylist)]
#     df = df[~df.id.isin(df_ordered.id.unique())]
#     if first in ['largest', 'both']:
#         df_ordered = pd.concat([df_ordered, pd.DataFrame([df.iloc[0]])])
#     if first in ['capital', 'both']:
#         df_capitals = capital_cities()
#         df_capitals['capital'] = True
#         df = df.merge(df_capitals, left_on=['city', 'state'], right_on=['city', 'state', ], how='left')
#         df_ordered = pd.concat([df_ordered, df[df.capital == True]])
#     df.sort_values(by=[valuecolumn], ascending=False, inplace=True)
#
#     if starting_lat is None or starting_lng or None:
#         starting_lat = starting_lng = 0.0
#
#     # seed the ordered list (with all columns) with the passed coordinates, defaulted to one arbitrarily far away
#     if df_ordered.shape[0] == 0:
#         df_ordered = pd.concat(
#             [df_ordered, pd.DataFrame([{'latitude': starting_lat, 'longitude': starting_lng, 'id': 'starting point'}])])
#     else:
#         df = df[~df.id.isin(df_ordered.id.unique())]
#
#     df_scratchpad = pd.DataFrame()
#     calcs = 0
#     if verbose:
#         pbar = tqdm(total=df.shape[0])
#
#     while df.shape[0] > 0:
#
#         # remove cities that have alrady been ordered from the running list for consideration
#
#         # calculate distances to remaining cities from the one most recently added
#         row_most_recently_ordered = df_ordered.iloc[-1]
#         df['dist'] = df.apply(lambda row: geopy.distance.geodesic((row_most_recently_ordered['latitude'],
#                                                                    row_most_recently_ordered['longitude']),
#                                                                   (row['latitude'], row['longitude']),
#                                                                   ellipsoid='WGS-84').km, axis=1)
#         calcs += df.shape[0]
#         # add those to the running list of distances to remaining cities
#         df_scratchpad = pd.concat([df_scratchpad, df])
#
#         df_scratchpad['ringnumber'] = None
#
#         # discard all but the smallest distance between already ordered cities and cities yet to be orderd
#         df_scratchpad.sort_values(by=['city', 'state', 'dist'], ascending=True, inplace=True)
#         df_scratchpad.drop_duplicates(subset=["city", "state"], keep="first", inplace=True)
#
#         # find width of the rings by dividing the furthest point by the number of rings
#         furthest = df_scratchpad.dist.max()
#         ringwidth = furthest / rings
#
#         # convert that distance to a numbered ring (bin), larger ring numbers are further away
#         # round function forces a single ring
#         df_scratchpad.ringnumber = round(df_scratchpad.dist / ringwidth)
#
#         df_scratchpad.sort_values(by=['capital', 'ringnumber', valuecolumn], ascending=False, inplace=True)
#
#         if order == 'furthest':
#             furthest_most_populous_row = df_scratchpad.iloc[0]
#         elif order == 'nearest':
#             raise ValueError(f"{order} ordering not yet implemented")
#         else:
#             raise ValueError(f"{order} not supported, please specify one of nearest (default), furthest, or central")
#
#         # append the city found to be next in the order
#         df_ordered = pd.concat([df_ordered, pd.DataFrame([furthest_most_populous_row])])
#
#         # remove cities already ordered from the todo list, and the running list of distances to cities yet to be ordered
#         df = df[~df.id.isin(df_ordered.id.unique())]
#         if row_most_recently_ordered.id == 'starting point':
#             df_scratchpad = pd.DataFrame()  # dump those distances, they were just for getting started
#             df_ordered = df_ordered[df_ordered.id != 'starting point']  # this is no longer needed either
#         else:
#             df_scratchpad = df_scratchpad[~df_scratchpad.id.isin(df_ordered.id.unique())]
#         if verbose:
#             pbar.update(1)
#             pbar.set_description(furthest_most_populous_row.city)
#
#     # return ordered list, removing the columns and row we added along the way
#     df_ordered.drop_duplicates(subset=["city", "state"], keep="first", inplace=True)  # when capital is the larget city
#     if orig_rows != df_ordered.shape[0]:
#         print(df_orig[~df_orig.isin(df_ordered.city.unique())])
#         print(df_orig)
#         raise Exception(
#             f"something went wrong, {df_orig.shape[0]} rows were passed but resulting dataframe as {df_ordered.shape[0]} rows")
#     if verbose:
#         print(f"{calcs:,} calculations for {df_orig.shape[0]}")
#
#     df_result = df_ordered[df_ordered.id != 'starting point']
#     df_result['ratio'] = df_result[valuecolumn] / df_result[valuecolumn].max()
#     df_result.reset_index(inplace=True)
#     df_result.drop(columns=['ringnumber', 'id', 'capital', 'index'], inplace=True)
#     if type(df_orig) == gpd.geodataframe.GeoDataFrame and type(df_result) != gpd.geodataframe.GeoDataFrame:
#         # all this mucking about with the dataframes can cause cause GeoPandas dataframe to devolve into a
#         # plain-ol Pandas dataframe, we should return the same type that was passed, restoring the same
#         # CRS and geometry column passed
#         df_result = gpd.GeoDataFrame(df_result, crs=df_orig.crs, geometry=df_result.geometry)
#
#     return df_result
#
#
# def calcdist(coord1, coord2):
#     dist = geopy.distance.geodesic(coord1, coord2, ellipsoid='WGS-84').km
#     return dist
