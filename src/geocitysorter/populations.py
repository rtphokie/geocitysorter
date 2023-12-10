import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from .utils import download_file


def get_census_data(cols=['name', 'state', 'population', 'settlement'], popcolumn='POPESTIMATE2022',
                    url='https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv'):
    download_file(url)
    df_cb = pd.read_csv('cache/sub-est2022.csv')
    df_cb['settlement'] = np.nan # lowercase columns were created here, CAPCASE were created by the US Census Bureau
    df_cb['name'] = np.nan

    # filter out breakdowns by county, inside outside the city limits, etc.  Should leave us with just cities, towns, etc.
    df_cb = df_cb[df_cb.PLACE > 0]  # filter out state and county populations
    df_cb = df_cb[ df_cb.COUNTY == 0]  # filter out partial populations of cities and towns that extend into multiple counties
    df_cb = df_cb[~df_cb.NAME.str.endswith( ' government')]  # filter out partial populations of cities and towns that extend into multiple counties
    df_cb = df_cb[~df_cb.NAME.str.endswith( ' (balance)')]  # filter out partial populations of cities and towns that extend into multiple counties
    df_cb = df_cb[~df_cb.NAME.str.endswith( ' County')]  # filter out partial populations of cities and towns that extend into multiple counties
    df_cb = df_cb[~df_cb.NAME.str.startswith( 'Balance of ')]  # filter out partial populations of cities and towns that extend into multiple counties

    # cleanup inconsistencies
    df_cb.NAME.replace('Ranson corporation', 'Ranson city', inplace=True)
    df_cb.NAME.replace('Princeton', 'Princeton municipality', inplace=True)  # make name consistent
    df_cb.NAME.replace('Carson City', 'Carson City city', inplace=True)  # make name consistent

    # move town, city, etc. to a new column
    df_cb['settlement'] = df_cb.NAME.str.rsplit(' ').str[-1]
    df_cb['name'] = df_cb.NAME.str.rsplit(' ').str[:-1].str.join(' ')

    # deduplicate
    df_cb['dupe'] = df_cb.duplicated(subset=['NAME', 'STNAME'])
    df_cb = df_cb[
        (df_cb.dupe == False) | ((df_cb.dupe == True) & (df_cb.CONCIT == 0))]  # keep the colsolidated city if present
    df_cb['dupe'] = df_cb.duplicated(subset=['NAME', 'STNAME'])  # recheck for duplicate rows
    df_cb = df_cb[
        df_cb.dupe == False]  # dropping duplicate village of Oakwood, Ohio. Unclear why there are two entries with different placeids in Census data.

    df_cb['state']=df_cb['STNAME']
    df_cb['population']=df_cb[popcolumn]

    return df_cb[cols]

    df = df_cb[df_cb.STNAME == 'North Carolina']
    df = df[['NAME', 'STATE', 'POPESTIMATE2022']]
    df.sort_values(by='POPESTIMATE2022', inplace=True)