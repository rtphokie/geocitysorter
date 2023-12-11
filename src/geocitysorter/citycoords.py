import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
from .utils import _download_file



def get_city_coords(cols=['state_usps', 'state', 'name', 'name_long', 'COUNTY', 'LATITUDE', 'LONGITUDE'],
                    url='https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv'):
    filename = _download_file(url)
    df = pd.read_csv(filename)
    df['state_usps']=df['STATE_CODE']
    df['state']=df['STATE_NAME']
    df['name']=df['CITY']
    df['name_long']=df['name']+', '+df['state']

    print(df.columns)


    return df[cols]