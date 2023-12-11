import numpy as np
import pandas as pd
from .census import _download_file
import requests_cache

session = requests_cache.CachedSession('./cache/http_geocode.cache')

def census_incorporated_cities():
    df_coords = _get_census_incorporated_places()
    # df = df[df.STNAME == 'Alabama']
    df_pop = _get_census_population_data()
    popcols=[]
    for col in df_pop.columns():
        if col.startswith('POP'):
            popcols.append(col)

    print(popcols)
    raise

    # df2 = df2[df2.STNAME == 'Alabama']
    # foo = df.join(df2, on=['NAME', 'STNAME'])
    df = pd.merge( df_coords, df_pop, on=['NAME', 'STNAME'], how='left')
    df


def _get_census_population_data(cols=['name', 'state', 'population', 'settlement', 'name_long'], popcolumn='POPESTIMATE2022',
                     url='https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv'):
    r = session.get(url)
    df = pd.concat(pd.read_html(io.StringIO(r.text)))
    df['settlement'] = df.NAME.str.rsplit(' ').str[-1]


def _get_census_incorporated_places(url='https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_incplace_current.html'):
    r = session.get(url)
    atoms = r.text.split(' <a href="')
    df_incorporated_places = pd.DataFrame()
    for atom in atoms:
        if atom.startswith('Files/acs23/'):
            atoms2 = atom.split('">')
            state, __ = atoms2[1].split('</a')
            state = ' '.join(state.split())  # collapse whitespace
            url = f"https://tigerweb.geo.census.gov/tigerwebmain/{atoms2[0]}"
            r = session.get(url)
            if not 'No Data' in r.text:
                import io
                df = pd.concat(pd.read_html(io.StringIO(r.text)))
                df['STNAME'] = state
                df_incorporated_places = pd.concat([df_incorporated_places, df])
    return df_incorporated_places



def get_census_data(cols=['name', 'state', 'population', 'settlement', 'name_long'], popcolumn='POPESTIMATE2022',
                    url='https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv'):
    _download_file(url)
    df = pd.read_csv('cache/sub-est2022.csv')
    df['settlement'] = df.NAME.str.rsplit(' ').str[-1]

    # df['settlement'] = np.nan # lowercase columns were created here, CAPCASE were created by the US Census Bureau
    return df
    df['name'] = np.nan

    # filter out breakdowns by county, inside outside the city limits, etc.  Should leave us with just cities, towns, etc.
    df = df[df.PLACE > 0]  # filter out state and county populations
    df = df[ df.COUNTY == 0]  # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.contains( ' and ')]  # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.endswith( ' government')]  # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.endswith( ' (balance)')]  # filter out partial populations of cities and towns that extend into multiple counties
    df = df[~df.NAME.str.endswith( ' County')]  # filter out broad county wide population couds
    df = df[~df.NAME.str.endswith( ' county')]  # filter out broad county wide population couds
    df = df[~df.NAME.str.endswith( ' metro')]  # filter out broad county wide population couds
    df = df[~df.NAME.str.startswith( 'Balance of ')]  # filter out partial populations of cities and towns that extend into multiple counties
    # print(df[df.NAME.str.contains('Robles')])

    # cleanup inconsistencies
    df.NAME.replace('Urban Honolulu CDP', 'Honolulu city', inplace=True)
    df.NAME.replace('El Paso de Robles (Paso Robles) city', 'Paso Robles city', inplace=True)
    df.NAME.replace('Ranson corporation', 'Ranson city', inplace=True)
    df.NAME.replace('Princeton', 'Princeton municipality', inplace=True)  # make name consistent
    df.NAME.replace('Islamorada, Village of Islands village', 'Islamorada village', inplace=True)  # make name consistent
    df.NAME.replace('Carson City', 'Carson City city', inplace=True)  # make name consistent
    # jkl=df[(df.NAME.str.contains('Town city')&(df.STNAME=='Massachusetts'))]
    # print(jkl)
    # raise

    # move town, city, etc. to a new column
    df['settlement'] = df.NAME.str.rsplit(' ').str[-1]
    df['name'] = df.NAME.str.rsplit(' ').str[:-1].str.join(' ')

    # deduplicate
    df['dupe'] = df.duplicated(subset=['NAME', 'STNAME'])
    df = df[
        (df.dupe == False) | ((df.dupe == True) & (df.CONCIT == 0))]  # keep the colsolidated city if present
    df['dupe'] = df.duplicated(subset=['NAME', 'STNAME'])  # recheck for duplicate rows
    df = df[
        df.dupe == False]  # dropping duplicate village of Oakwood, Ohio. Unclear why there are two entries with different placeids in Census data.

    df['state']=df['STNAME']
    df['population']=df[popcolumn]
    df['name_long']=df['name']+', '+df['state']

    return df[cols]

    df = df[df.STNAME == 'North Carolina']
    df = df[['NAME', 'STATE', 'POPESTIMATE2022']]
    df.sort_values(by='POPESTIMATE2022', inplace=True)