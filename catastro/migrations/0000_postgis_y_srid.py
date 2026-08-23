"""
Migración base del stack espacial:
  1. Habilita la extensión PostGIS (idempotente).
  2. Registra el SRID 9377 (MAGNA-SIRGAS / CTM12) en spatial_ref_sys,
     necesario para las reproyecciones métricas de la Fase 4.

Se ejecuta ANTES de crear las tablas con geometría (0001_initial
depende de esta migración).
"""
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


# Definición oficial del EPSG:9377 (verificada contra IGAC/EPSG.io).
INSERT_9377 = """
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext)
SELECT 9377, 'EPSG', 9377,
'+proj=tmerc +lat_0=4 +lon_0=-73 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs +type=crs',
'PROJCS["MAGNA-SIRGAS 2018 / Origen-Nacional",GEOGCS["MAGNA-SIRGAS 2018",DATUM["Marco_Geocentrico_Nacional_de_Referencia_2018",SPHEROID["GRS 1980",6378137,298.257222101],TOWGS84[0,0,0,0,0,0,0]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","20046"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",4],PARAMETER["central_meridian",-73],PARAMETER["scale_factor",0.9992],PARAMETER["false_easting",5000000],PARAMETER["false_northing",2000000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","9377"]]'
WHERE NOT EXISTS (SELECT 1 FROM spatial_ref_sys WHERE srid = 9377);
"""

DELETE_9377 = "DELETE FROM spatial_ref_sys WHERE srid = 9377;"


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        CreateExtension("postgis"),
        migrations.RunSQL(sql=INSERT_9377, reverse_sql=DELETE_9377),
    ]
