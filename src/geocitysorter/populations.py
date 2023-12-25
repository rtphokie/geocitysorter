import numpy as np
import pandas as pd
import requests_cache
from platformdirs import user_cache_dir

from .census import _download_file

cachedir = user_cache_dir("geocitysorter", "trice")
session = requests_cache.CachedSession(f'{cachedir}/http_geocode.cache')


def get_census_data(cols=['name', 'state', 'population', 'settlement', 'name_long'], popcolumn='POPESTIMATE2022',
                    url='https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv'):
    _download_file(url)
    df = pd.read_csv(f'{cachedir}/sub-est2022.csv')
    df['settlement'] = df.NAME.str.rsplit(' ').str[-1]

    df['name'] = np.nan

    # filter out breakdowns by county, inside outside the city limits, etc.  Should leave us with just cities, towns, etc.
    df = df[df.PLACE > 0]  # filter out state and county populations
    df = df[df.COUNTY == 0]  # filter out partial populations of cities and towns that extend into multiple counties
    # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.contains(' and ')]
    # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.endswith(' government')]
    # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.endswith(' (balance)')]
    df = df[~df.NAME.str.endswith(' County')]  # filter out broad county wide population couds
    df = df[~df.NAME.str.endswith(' county')]  # filter out broad county wide population couds
    df = df[~df.NAME.str.endswith(' metro')]  # filter out broad county wide population couds
    # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.startswith('Balance of ')]

    # cleanup inconsistencies
    df.NAME.replace('Urban Honolulu CDP', 'Honolulu city', inplace=True)
    df.NAME.replace('El Paso de Robles (Paso Robles) city', 'Paso Robles city', inplace=True)
    df.NAME.replace('Ranson corporation', 'Ranson city', inplace=True)
    df.NAME.replace('Princeton', 'Princeton municipality', inplace=True)  # make name consistent
    # make name consistent
    df.NAME.replace('Islamorada, Village of Islands village', 'Islamorada village', inplace=True)
    df.NAME.replace('Carson City', 'Carson City city', inplace=True)  # make name consistent

    # move town, city, etc. to a new column
    df['settlement'] = df.NAME.str.rsplit(' ').str[-1]
    df['name'] = df.NAME.str.rsplit(' ').str[:-1].str.join(' ')

    # deduplicate
    df['dupe'] = df.duplicated(subset=['NAME', 'STNAME'])
    # keep the colsolidated city if present
    df = df[(df.dupe == False) | ((df.dupe == True) & (df.CONCIT == 0))]
    df['dupe'] = df.duplicated(subset=['NAME', 'STNAME'])  # recheck for duplicate rows
    # dropping duplicate village of Oakwood, Ohio. Unclear why there are two entries with different placeids in Census data.
    df = df[df.dupe == False]

    df['state'] = df['STNAME']
    df['population'] = df[popcolumn]
    df['name_long'] = df['name'] + ', ' + df['state']

    return df[cols]
