from astropy.coordinates import get_body
import numpy as np
from astropy.coordinates import EarthLocation
from astropy.time import Time
import ephem
from datetime import datetime
def calculate_moon_position(obstime, location):
    obstime = datetime.strptime(obstime, '%Y-%m-%dT%H:%M:%S')

    observer = ephem.Observer()
    observer.lon = str(location.lon.deg)
    observer.lat = str(location.lat.deg)
    observer.date = obstime

    moon = ephem.Moon(observer)
    ra = moon.ra
    dec = moon.dec
    print(f"RA DEC Moon on {obstime} {ra}, {dec} ")
    ra_decimal = ra * 180.0 / np.pi
    dec_decimal = dec * 180.0 / np.pi
    return ra_decimal, dec_decimal

# Example usage

def calculate_moon_phase(obstime):
        obstime = datetime.strptime(obstime, '%Y-%m-%dT%H:%M:%S')

        # Create an observer at a neutral location (Greenwich, UK)
        observer = ephem.Observer()
        observer.lon = '0'  # Longitude of Greenwich
        observer.lat = '0'  # Latitude of Greenwich
        observer.date = ephem.Date(obstime)  # Set the observation date
        moon = ephem.Moon(observer)
        phase_illumination = moon.moon_phase * 100

        return phase_illumination

def calculate_angular_separation(obstime, sitelat, sitelong, ra, dec):
    obstime = datetime.strptime(obstime, '%Y-%m-%dT%H:%M:%S')

    observer = ephem.Observer()
    observer.lon = str(sitelong)
    observer.lat = str(sitelat)
    observer.date = ephem.Date(obstime)
    moon = ephem.Moon(observer)
    target = ephem.FixedBody()
    target._ra = ra
    target._dec = dec
    target.compute(observer)
    
    separation = ephem.separation(moon, target)
    separation_degrees = np.degrees(separation)
    print(f"Angular separation in degrees: {separation_degrees}")
    return separation

# Example usage
obstime = '2024-03-14T00:31:32'  # Observation time
ra = '51.8553'  # Right Ascension of the target object
dec = '354.6981'  # Declination of the target object
location = EarthLocation(lat=31.2064, lon=-7.8664)  
sitelat = 31.2064	
sitelong = -7.8664
separation = calculate_angular_separation(obstime, sitelat, sitelong, ra, dec)
print(f"Angular separation: {separation}")
print(calculate_moon_phase(obstime))

moon_ra, moon_dec = calculate_moon_position(obstime, location)
print(f"Moon RA: {moon_ra}, Moon Dec: {moon_dec}")