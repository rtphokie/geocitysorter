import io
import os
import pickle
import zipfile

import geopandas as gpd
import pandas as pd
import requests
import requests_cache

session = requests_cache.CachedSession('./cache/http_census_gov.cache')


def _most_recent_population_column(colstoconsider):
    # sorts a list of column names, returning the alphabetically last one
    # useful in picking the most recent population column from USCB CSVs
    popcols = []
    for col in colstoconsider:
        if 'POP' in col:
            popcols.append(col)
    popcols = sorted(popcols)
    latestpopcol = popcols[-1]
    return latestpopcol


def census_incorporated_cities(crs="EPSG:4326",
                               columnstokeep=['city', 'state', 'population', 'area_land', 'area_water', 'latitude',
                                              'longitude']):
    '''

    fetches population and coordinate data for nearly 20k incorporated cities from the United States Census Bureau and
    merges them into a GeoPandas Dataframe with columns for city, state, latest population estimate, latitude, longitude
    along with land and water size information.

    :param crs: coordinate reference system to apply to resulting GeoDataFrame, defaults to ESPG:4326 the familiar
                latitude/longitude coordinate system based on the Earth's center of mass
    :param columnstokeep: columns to be returned, defaults to the list above
    :return:GeoPandas Dataframe of incorporated cities
    '''
    os.makedirs('cache', exist_ok=True)
    picklefile = 'cache/census_incorporated_cities.pickle'
    try:
        with open(picklefile, 'rb') as fp:
            gdf = pickle.load(fp)
    except:
        df_pop = _get_census_data()
        df_pop['population'] = df_pop[most_recent_population_column(df_pop.columns)]

        df_coords = _get_census_incorporated_places()

        df = pd.merge(df_pop, df_coords, on=['NAME', 'STNAME'], how='left')
        df.rename(columns={"NAME": "city", "STNAME": "state",
                           "AREALAND": 'area_land', "AREAWATER": 'area_water',  # these might be useful
                           "CENTLAT": "latitude", "CENTLON": "longitude",
                           }, errors="raise", inplace=True)
        df = df[columnstokeep]
        df.drop_duplicates(
            inplace=True)  # USCB population data includes some breakouts by county and other methods that result in duplicate data when we drop the other fields we dont need
        df.dropna(subset=['longitude', 'latitude'], inplace=True)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=crs)
        with open(picklefile, 'wb') as fp:
            pickle.dump(gdf, fp)
    return gdf


def _get_census_data(
        url='https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv'):
    '''
    fetches general purpose population dataset from United States Census Bureau

    more info on the dataset: https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html

    :param url: url to fetch data from, defaults to 2022 data set
    :return: pandas dataframe with all dat
    '''

    os.makedirs('cache', exist_ok=True)

    r = session.get(url)
    if r.ok:
        df_populations = pd.read_csv(io.StringIO(r.text))
    else:
        raise BaseException(f"error {r.status_code} accessing {url}")
    return df_populations


def _get_census_incorporated_places(url='https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_incplace_current.html'):
    '''

    Retrieves state based tables of incorporated places from teh United States Census Bureau's Topologically Integrated
    Geographic Encoding and Referencing (TIGER), combining them into a single dataframe with city, state, longitude,
    and latitude.

    for more information on the dataset see the URL above

    :param url:
    :return: pandas dataframe (not a GeoPandas dataframe)
    '''
    os.makedirs('cache', exist_ok=True)
    picklefile = 'cache/_get_census_incorporated_places.pickle'
    try:
        with open(picklefile, 'rb') as fp:
            df_incorporated_places = pickle.load(fp)
    except:
        r = session.get(url)
        if not r.ok:
            raise BaseException(f"error {r.status_code} accessing {url}")
        atoms = r.text.split(' <a href="')
        df_incorporated_places = pd.DataFrame()
        for atom in atoms:
            if atom.startswith('Files/acs23/'):
                atoms2 = atom.split('">')
                state, __ = atoms2[1].split('</a')
                state = ' '.join(state.split())  # collapse whitespace
                url = f"https://tigerweb.geo.census.gov/tigerwebmain/{atoms2[0]}"
                r = session.get(url)
                if not r.ok:
                    raise BaseException(f"error {r.status_code} accessing {url}")
                if not 'No Data' in r.text:
                    import io
                    df = pd.concat(pd.read_html(io.StringIO(r.text)))
                    df['STNAME'] = state  # add a state column, using similar name as population data tables
                    df_incorporated_places = pd.concat([df_incorporated_places, df])
        with open(picklefile, 'wb') as fp:
            pickle.dump(df_incorporated_places, fp)

    return df_incorporated_places


def _download_file(url):
    # downloads a binary or text file from a URL, caching it locally
    os.makedirs('cache', exist_ok=True)
    local_filename = f"cache/{os.path.basename(url)}"
    result = local_filename
    local_extraction_dir = f"cache/{os.path.splitext(os.path.basename(os.path.basename(url)))[0]}"

    if not os.path.exists(local_filename):
        response = requests.get(url)

        if response.status_code == 200:
            print(local_filename)
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f'downloaded {local_filename} from {url}')
    if local_filename.endswith('.zip') and not os.path.exists(local_extraction_dir):
        with zipfile.ZipFile(local_filename, 'r') as zip_ref:
            zip_ref.extractall(local_extraction_dir)
            result = local_extraction_dir
    return result

#
# def _get_coords_from_wikipedia(s):
#     url = f"https://en.wikipedia.org/wiki/{s}"
#     r = session.get(url)
#     import re
#     stuff = re.search('<span class="geo">([\d\.\-]+); ([\d\-\.]+)</span>', r.text, re.IGNORECASE)
#     result = None
#     if stuff:
#         result = {'lat': float(stuff.group(1)),
#                   'lng': float(stuff.group(2)),
#                   'from_cache': r.from_cache,
#                   'display_name': f"{s}, United States",
#                   'importance': None,
#                   'osm_id': None,
#                   }
#     else:
#         print(url)
#     return result
#
#
# # https://nominatim.org/release-docs/develop/api/Overview/
# def _geocode(s, use_cache=True, service='https://geocode.maps.co/search?q='):
#     # https://geocode.maps.co
#     s = s.replace(' Town, Massachusetts', ', Massachusetts')  #
#     result = None
#     import time
#     os.makedirs('cache', exist_ok=True)
#     with shelve.open('cache/geocode.cache') as db:
#         if s not in db.keys() or not use_cache or db[s] is None:
#             url = f"{service}{s.replace(' ', '+')},+United States"
#             # url = f"https://nominatim.openstreetmap.org/search?format=json&q={s.replace(' ', '+')},+United States"
#             r = session.get(url)
#             if not r.from_cache:
#                 time.sleep(1)  # free tier of maps.co has a very reasonable 1 second throttle limit
#             if r.ok:
#                 data = r.json()
#                 # pprint(data)
#                 previmportant = 0
#                 theone = {'importance': 0}
#                 for x in r.json():
#                     if x['importance'] > theone['importance'] and x['type'] in ['administrative', 'census', 'city',
#                                                                                 'town', 'hamlet', 'townhall',
#                                                                                 'village']:
#                         if 'lat' in x.keys():
#                             theone = x
#             else:
#                 print(s)
#                 print(url)
#                 print(r.text)
#                 return None
#             if 'lat' in theone.keys():
#                 result = {'lat': float(theone['lat']),
#                           'lng': float(theone['lon']),
#                           'from_cache': r.from_cache,
#                           'display_name': theone['display_name'],
#                           'importance': theone['importance'],
#                           'osm_id': theone['osm_id'],
#                           }
#             elif 'geocode.maps.co' in service:
#                 db[s] = None
#                 db.close()
#                 return _geocode(s, service='https://nominatim.openstreetmap.org/search?format=json&q=')
#
#             # missing open stream map data
#             if result is None:
#                 if s == 'Burlington, New Jersey':
#                     result = {'lat': 40.078307,
#                               'lng': -74.853328,
#                               'from_cache': True,
#                               'display_name': 'Burlington, New Jersey, United States',
#                               'importance': 0.5,
#                               'osm_id': None,
#                               }
#                 elif s == 'Credit River, Minnesota':
#                     result = {'lat': 44.673889, 'lng': -93.358889,
#                               'display_name': 'Credit River, Minnesota, United States',
#                               'from_cache': True, 'importance': 0.5, 'osm_id': None,
#                               }
#                 elif s == 'Lancaster, New York':
#                     result = {'lat': 42.906111, 'lng': -78.633889,
#                               'display_name': 'Lancaster, New York, United States',
#                               'from_cache': True, 'importance': 0.5, 'osm_id': None,
#                               }
#                 elif s == 'Corning, New York':
#                     result = {'lat': 42.148056, 'lng': -77.056944,
#                               'display_name': 'Corning, New York, United States',
#                               'from_cache': True, 'importance': 0.5, 'osm_id': None,
#                               }
#                 elif s == 'James Island, South Carolina':
#                     result = {'lat': 32.737778, 'lng': -79.942778,
#                               'from_cache': True, 'importance': 0.5, 'osm_id': None,
#                               }
#                 elif s == 'Cahokia Heights, Illinois':
#                     result = {'lat': 40.6170,
#                               'lng': -89.6046,
#                               'from_cache': True,
#                               'display_name': 'Cahokia Heights, Illinois, United States',
#                               'importance': 0.5,
#                               'osm_id': None,
#                               }
#                 elif s == 'Inverness, Florida':
#                     result = {'lat': -82.34027,
#                               'lng': 28.83917,
#                               'from_cache': True,
#                               'display_name': 'Inverness, Florida, United States',
#                               'importance': 0.5,
#                               'osm_id': None,
#                               }
#                 else:
#                     print(url)
#                     print(f"{s} types")
#                     for x in data:
#                         print(x['type'])
#                     if 'geocode.maps.co' in service:
#                         db[s] = None
#                         db.close()
#                         return _geocode(s, service='https://nominatim.openstreetmap.org/search?format=json&q=')
#             try:
#                 db[s] = result
#             except:
#                 print(f'need to revisit {s}', '-' * 20)
#                 pass
#         else:
#             result = db[s]
#             result['from_cache'] = True
#
#     return result
