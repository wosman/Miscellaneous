import urllib
import json


serviceurl = 'http://python-data.dr-chuck.net/geojson?'

address = raw_input('Enter location: ')
url = serviceurl + urllib.urlencode({'sensor':'false', 'address': address})
print 'Retrieving', url
uh = urllib.urlopen(url)
data = uh.read()
print 'Retrieved',len(data),'characters'

js = json.loads(str(data))

place_id = js["results"][0]["place_id"]
print 'Place id ' + place_id
