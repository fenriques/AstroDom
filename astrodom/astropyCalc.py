from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
import numpy as np

"""
Some useful calculation are made here using AstroPy.
- 'getAltAzCoord' is used when importing FITS header to
calculate alt/az coord given the target coord and 
time/location.
- (TBD) 'moonPath' will be used to show the moon path
in charts.
- (TBD) 'WcsCoord': overlaps wcs to image detail.
"""


class AstropyCalc:
    def __init__(self, app):
        self.coord = 10
        self.app = app

    def coordConversion(self, ra, dec):

        if ra != "" and dec != "":
            if self.app.conf["coordFormat"]["description"] == "Hour Angle":
                radec = ra + " " + dec
                c = SkyCoord(radec, unit=(u.hourangle, u.deg))
                return c
            elif self.app.conf["coordFormat"]["description"] == "Decimal":
                c = SkyCoord(ra, dec, unit=(u.deg, u.deg))
                return c
        return None

    def longLatConversion(self, long, lat):
        if long != "" and lat != "":
            if self.app.conf["coordFormat"]["description"] == "Hour Angle":
                longLat = long + " " + lat
                s = SkyCoord(longLat, unit=(u.deg, u.deg))
                return s
            elif self.app.conf["coordFormat"]["description"] == "Decimal":
                s = SkyCoord(long, lat, unit=(u.deg, u.deg))
                return s

        return None

    def getAltAzCoord(self, ra, dec, obsTime, obsLon, obsLat):

        if ra != "" and dec != "" and obsTime != "" and obsLon != "" and obsLat != "":
            objectCoord = SkyCoord(ra, dec, unit="deg")

            obsLocation = EarthLocation(
                lat=obsLat * u.deg, lon=obsLon * u.deg, height=0 * u.m
            )
            time = Time(obsTime)

            objectAltAz = objectCoord.transform_to(
                AltAz(obstime=time, location=obsLocation)
            )

            return objectAltAz
        return None
