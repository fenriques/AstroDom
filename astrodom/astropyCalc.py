from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
import numpy as np


class AstropyCalc:

    def __init__(self):
        self.coord = 10

    def getAltAzCoord(self, ra, dec, obsTime, obsLon, obsLat):

        if ra != '' and dec != '' and obsTime != '' and obsLon != '' and obsLat != '':
            objectCoord = SkyCoord(ra, dec,  unit="deg")

            obsLocation = EarthLocation(
                lat=obsLat*u.deg, lon=obsLon*u.deg, height=0*u.m)
            time = Time(obsTime)

            objectAltAz = objectCoord.transform_to(
                AltAz(obstime=time, location=obsLocation))

            return objectAltAz
        return None
