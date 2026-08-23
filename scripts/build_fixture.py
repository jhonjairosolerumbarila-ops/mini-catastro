"""Genera fixtures/initial_data.json con datos de ejemplo coherentes."""
import json
from datetime import datetime, timezone

SRID = 4326
AHORA = datetime.now(timezone.utc).isoformat()


def rect(xmin, ymin, xmax, ymax):
    ring = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]
    coords = ", ".join(f"{x} {y}" for x, y in ring)
    return f"SRID={SRID};MULTIPOLYGON ((({coords})))"


def numero_predial(i):
    return f"25754{str(i).zfill(25)}"


propietarios = [
    (1, "1015420001", "Maria Fernanda Rios", "mfrios@example.com", "3001112233"),
    (2, "79855102", "Carlos Andres Gomez", "cgomez@example.com", "3014445566"),
    (3, "52988771", "Laura Valentina Pena", "lpena@example.com", "3027778899"),
]

predios = [
    (1, 1, "Carrera 10 # 20-30", 1, "PH", rect(-74.0810, 4.6500, -74.0790, 4.6520)),
    (2, 2, "Carrera 9 # 20-15", 1, "NPH", rect(-74.0790, 4.6500, -74.0770, 4.6520)),
    (3, 3, "Calle 19 # 11-05", 2, "CONDOMINIO", rect(-74.0830, 4.6480, -74.0810, 4.6500)),
    (4, 4, "Vereda El Alto s/n", 3, "INFORMAL", rect(-74.0700, 4.6600, -74.0680, 4.6620)),
    (5, 5, "Calle 22 # 8-40", 1, "NPH", rect(-74.0770, 4.6520, -74.0750, 4.6540)),
]

zonas = [
    (1, "Inundacion Rio Fucha", "ALTO", rect(-74.0815, 4.6495, -74.0765, 4.6525)),
    (2, "Falla Geologica Oriente", "MEDIO", rect(-74.0835, 4.6475, -74.0805, 4.6505)),
    (3, "Remocion en Masa Ladera", "BAJO", rect(-74.0775, 4.6515, -74.0745, 4.6545)),
]

copropiedades = [(1, 1, 1, "60.00"), (2, 1, 2, "40.00")]

data = []

for pk, doc, nombre, correo, tel in propietarios:
    data.append({"model": "catastro.propietario", "pk": pk, "fields": {
        "documento_identidad": doc, "nombre_completo": nombre,
        "correo_electronico": correo, "telefono": tel,
        "creado_en": AHORA, "actualizado_en": AHORA}})

for pk, i, direccion, prop, cond, geom in predios:
    data.append({"model": "catastro.predio", "pk": pk, "fields": {
        "numero_predial": numero_predial(i), "nombre_direccion": direccion,
        "propietario": prop, "condicion_predio": cond, "poligono": geom,
        "creado_en": AHORA, "actualizado_en": AHORA}})

for pk, nombre, nivel, geom in zonas:
    data.append({"model": "catastro.zonariesgo", "pk": pk, "fields": {
        "nombre": nombre, "nivel_riesgo": nivel, "poligono": geom,
        "creado_en": AHORA, "actualizado_en": AHORA}})

for pk, predio, prop, pct in copropiedades:
    data.append({"model": "catastro.copropiedad", "pk": pk, "fields": {
        "predio": predio, "propietario": prop,
        "porcentaje_participacion": pct}})

with open("fixtures/initial_data.json", "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)

print(f"Fixture escrito con {len(data)} registros.")
