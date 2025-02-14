import sqlite3
from astropy.coordinates import Angle
import astropy.units as u
from prettytable import PrettyTable

# Connect to the database
conn = sqlite3.connect('astrodom_database.db')
cursor = conn.cursor()

# Create a PrettyTable
table = PrettyTable()
# Add the target name and angle representation fields to the table
table.field_names = ["Target Name", "RA (decimal)", "RA (angle)", "DEC (decimal)", "DEC (angle)", "ALT (decimal)", "ALT (angle)", "AZ (decimal)", "AZ (angle)"]

# Fetch Target Name, RA, DEC, ALT, and AZ from the images table
cursor.execute("SELECT OBJECT, OBJECT_RA, OBJECT_DEC, OBJECT_ALT, OBJECT_AZ FROM images")
rows = cursor.fetchall()

# Close the database connection
conn.close()

# Convert values to decimal and angle representation and add to the table
for row in rows:
    target_name, ra, dec, alt, az = row
    ra_decimal = Angle(ra, unit=u.hour).degree if ra else None
    ra_angle = Angle(ra, unit=u.hour).to_string(unit=u.hour, sep=':') if ra else None
    dec_decimal = Angle(dec, unit=u.deg).degree if dec else None
    dec_angle = Angle(dec, unit=u.deg).to_string(unit=u.deg, sep=':') if dec else None
    alt_decimal = Angle(alt, unit=u.deg).degree if alt else None
    alt_angle = Angle(alt, unit=u.deg).to_string(unit=u.deg, sep=':') if alt else None
    az_decimal = Angle(az, unit=u.deg).degree if az else None
    az_angle = Angle(az, unit=u.deg).to_string(unit=u.deg, sep=':') if az else None
    table.add_row([target_name, ra_decimal, ra_angle, dec_decimal, dec_angle, alt_decimal, alt_angle, az_decimal, az_angle])

# Print the table
print(table)