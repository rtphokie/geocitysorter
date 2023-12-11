import os
import shelve
import zipfile

import requests
import requests_cache


def _download_file(url):
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


# https://nominatim.org/release-docs/develop/api/Overview/
def _geocode(s, use_cache=True, service='https://geocode.maps.co/search?q='):
    # https://geocode.maps.co
    s=s.replace(' Town, Massachusetts', ', Massachusetts') #
    result = None
    import time
    os.makedirs('cache', exist_ok=True)
    session = requests_cache.CachedSession('./cache/http_geocode.cache')
    with shelve.open('cache/geocode.cache') as db:
        if s not in db.keys() or not use_cache or db[s] is None:
            url = f"{service}{s.replace(' ', '+')},+United States"
            # url = f"https://nominatim.openstreetmap.org/search?format=json&q={s.replace(' ', '+')},+United States"
            r = session.get(url)
            if not r.from_cache:
                time.sleep(1)  # free tier of maps.co has a very reasonable 1 second throttle limit
            if r.ok:
                data = r.json()
                from pprint import pprint
                # pprint(data)
                previmportant=0
                theone={'importance': 0}
                for x in r.json():
                    if x['importance'] > theone['importance'] and x['type'] in ['administrative', 'census', 'city', 'town', 'hamlet', 'townhall', 'village']:
                        if 'lat' in x.keys():
                            theone =x
            else:
                print(s)
                print(url)
                print(r.text)
                return None
            if 'lat' in theone.keys():
                result={'lat': float(theone['lat']),
                        'lng': float(theone['lon']),
                        'from_cache': r.from_cache,
                        'display_name': theone['display_name'],
                        'importance': theone['importance'],
                        'osm_id': theone['osm_id'],
                        }
            elif 'geocode.maps.co' in service:
                db[s]=None
                db.close()
                return _geocode(s, service='https://nominatim.openstreetmap.org/search?format=json&q=')

            # missing open stream map data
            if result is None:
                if s == 'Burlington, New Jersey':
                    result={'lat': 40.078307,
                            'lng':  -74.853328,
                            'from_cache': True,
                            'display_name': 'Burlington, New Jersey, United States',
                            'importance': 0.5,
                            'osm_id': None,
                            }
                elif s == 'Credit River, Minnesota':
                    result = {'lat': 44.673889, 'lng': -93.358889,
                              'display_name': 'Credit River, Minnesota, United States',
                              'from_cache': True, 'importance': 0.5, 'osm_id': None,
                              }
                elif s == 'Lancaster, New York':
                    result = {'lat': 42.906111, 'lng':-78.633889,
                              'display_name': 'Lancaster, New York, United States',
                              'from_cache': True, 'importance': 0.5, 'osm_id': None,
                              }
                elif s == 'Corning, New York':
                    result = {'lat': 42.148056, 'lng': -77.056944,
                              'display_name': 'Corning, New York, United States',
                              'from_cache': True, 'importance': 0.5, 'osm_id': None,
                              }
                elif s == 'James Island, South Carolina':
                    result={'lat': 32.737778, 'lng': -79.942778,
                            'from_cache': True, 'importance': 0.5, 'osm_id': None,
                            }
                elif s == 'Cahokia Heights, Illinois':
                    result={'lat': 40.6170,
                            'lng': -89.6046,
                            'from_cache': True,
                            'display_name': 'Cahokia Heights, Illinois, United States',
                            'importance': 0.5,
                            'osm_id': None,
                            }
                elif s == 'Inverness, Florida':
                    result={'lat': -82.34027,
                            'lng': 28.83917,
                            'from_cache': True,
                            'display_name': 'Inverness, Florida, United States',
                            'importance': 0.5,
                            'osm_id': None,
                            }
                else:
                    print(url)
                    print(f"{s} types")
                    for x in data:
                        print(x['type'])
                    if 'geocode.maps.co' in service:
                        db[s] = None
                        db.close()
                        return _geocode(s, service='https://nominatim.openstreetmap.org/search?format=json&q=')
            try:
                db[s]=result
            except:
                print(f'need to revisit {s}', '-'*20)
                pass
        else:
            result=db[s]
            result['from_cache']=True

    return result
