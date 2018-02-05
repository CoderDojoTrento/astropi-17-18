from datetime import datetime
import ephem

# Always get the latest ISS TLE data from:
# http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html
iss = ephem.readtle('ISS (ZARYA)',
    '1 25544U 98067A   18027.96608769  .00002138  00000-0  39404-4 0  9997',
    '2 25544  51.6452 357.7352 0003803  57.4957 343.4832 15.54226828 96711'
)
iss.compute(datetime.utcnow())
print(iss.elevation)
