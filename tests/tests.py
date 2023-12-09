import os
import unittest
import zipfile

import requests


# https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_region_20m.zip


def download_file(url):
    os.makedirs('cache', exist_ok=True)
    local_filename = f"cache/{os.path.basename(url)}"
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


class SomeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(SomeTest, cls).setUpClass()

    #    os.system('cd ..; python3 -m build --wheel')

    def setUp(self):
        download_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_region_20m.zip')
        download_file('https://simplemaps.com/static/data/us-cities/1.77/basic/simplemaps_uscities_basicv1.77.zip')

    def test_one(self):
        print('one')


if __name__ == '__main__':
    unittest.main()
