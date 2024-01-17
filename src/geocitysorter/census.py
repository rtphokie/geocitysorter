import io
import os
import pickle
import zipfile

import geopandas as gpd
import pandas as pd
import requests
import requests_cache

from .geocitysorter import capital_cities
from platformdirs import user_cache_dir

cachedir = user_cache_dir("geocitysorter", "trice")
session = requests_cache.CachedSession(f'{cachedir}/http_census_gov.cache')


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
                               columnstokeep=['city', 'state', 'population', 'latitude', 'longitude']):
    '''

    fetches population and coordinate data for nearly 20k incorporated cities from the United States Census Bureau and
    merges them into a GeoPandas Dataframe with columns for city, state, latest population estimate, latitude, longitude
    along with land and water size information.

    :param crs: coordinate reference system to apply to resulting GeoDataFrame, defaults to ESPG:4326 the familiar
                latitude/longitude coordinate system based on the Earth's center of mass
    :param columnstokeep: columns to be returned, defaults to the list above
    :return:GeoPandas Dataframe of incorporated cities
    '''
    picklefile = f'{cachedir}/census_incorporated_cities.pickle'
    try:
        with open(picklefile, 'rb') as fp:
            gdf = pickle.load(fp)
    except:
        df_pop = _get_census_data()

        df_pop['population'] = df_pop[_most_recent_population_column(df_pop.columns)]

        df_coords = _get_census_incorporated_places()

        df = pd.merge(df_pop, df_coords, on=['NAME', 'STNAME'], how='left')
        df.rename(columns={"BASENAME": "city", "STNAME": "state", "CENTLAT": "latitude", "CENTLON": "longitude", },
                  errors="raise", inplace=True)
        df = df[columnstokeep]

        df.drop_duplicates(inplace=True)  # USCB population data includes some breakouts by county and other methods that result in duplicate data when we drop the other fields we dont need
        df.dropna(subset=['longitude', 'latitude'], inplace=True)
        df = df.dropna()
        df.city = df.city.str.replace(' County unified government (balance)', '')
        df.city = df.city.str.replace(' County metro government (balance)', '')
        df.city = df.city.str.replace(' metropolitan government (balance)', '')
        df.city = df.city.str.replace(' County consolidated government (balance)', '')
        df.city = df.city.str.replace(' (balance)', '')
        df.city = df.city.str.replace('Athens-Clarke', 'Athens')
        df.city = df.city.str.replace('Augusta-Richmond', 'Augusta')
        df.city = df.city.str.replace('Cusseta-Chattahoochee County', 'Cusseta')
        df.city = df.city.str.replace('Helena-West Helena', 'Helena')
        df.city = df.city.str.replace('Nashville-Davidson', 'Nashville')
        df.city = df.city.str.replace('Louisville/Jefferson', 'Louisville')
        df.city = df.city.str.replace('Hartsville/Trousdale County', 'Hartsiville')
        #  note state capitals
        df_capitals = capital_cities()
        df_capitals['capital'] = 'state'
        df = df.merge(df_capitals, left_on=['city', 'state'], right_on=['city', 'state', ], how='left')
        i = df[df['state'] == 'District of Columbia'].index.values[0]
        df.loc[i, "capital"] = "federal"
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
    picklefile = f'{cachedir}/get_census_incorporated_places.pickle'
    try:
        with open(picklefile, 'rb') as fp:
            df_incorporated_places = pickle.load(fp)
        if df_incorporated_places.shape[0] < 9999:
            raise ValueError
    except:
        r = session.get(url)
        if not r.ok:
            raise BaseException(f"error {r.status_code} accessing {url}")
        atoms = r.text.split(' <a href="')
        df_incorporated_places = pd.DataFrame()
        for atom in atoms:
            if atom.startswith('Files/'):
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
    local_filename = f"{cachedir}/{os.path.basename(url)}"
    result = local_filename
    local_extraction_dir = f"{cachedir}/{os.path.splitext(os.path.basename(os.path.basename(url)))[0]}"

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
