# Mini-Catastro — Backend GIS (Django + GeoDjango + PostGIS)

Backend geoespacial para la gestión de **predios**, **propietarios** y
**zonas de riesgo**, con consultas espaciales sobre PostGIS expuestas como
API REST autenticada con JWT. Construido con Django 5, Django REST
Framework, GeoDjango, PostGIS y Docker.

## Stack técnico

| Componente | Versión |
|---|---|
| Django | 5.1.4 |
| Django REST Framework | 3.15.2 |
| djangorestframework-gis | 1.1 |
| djangorestframework-simplejwt | 5.3.1 |
| PostgreSQL / PostGIS | 16 / 3.4 |
| GDAL / GEOS / PROJ | 3.8 / 3.12 / 7.2 |
| Python | 3.12 |

## Arranque rápido (Docker)

Requisitos: Docker Desktop con integración WSL2 (en Windows) o Docker
Engine (en Linux).

```bash
# 1. Clonar y entrar
git clone https://github.com/jhonjairosolerumbarila-ops/mini-catastro.git
cd mini-catastro

# 2. Crear el archivo de entorno a partir de la plantilla
cp .env.example .env
# (editar .env y poner una DJANGO_SECRET_KEY y contrasenas propias)

# 3. Levantar base de datos PostGIS + backend Django
docker compose up --build
```
Cuando el log muestre `Starting development server at http://0.0.0.0:8000/`,
la API esta lista.

### Inicializar datos

El `entrypoint.sh` corre automaticamente al levantar el contenedor:
aplica migraciones (extension PostGIS + SRID 9377), crea el
superusuario (variables DJANGO_SUPERUSER_* del .env) y carga el
fixture de ejemplo.

Con `docker compose up` el backend queda listo, sin pasos manuales.
Superusuario por defecto: `admin` / `DJANGO_SUPERUSER_PASSWORD`.

## Autenticación (JWT)

Todos los endpoints requieren un token Bearer.

```bash
# Obtener token
curl -s -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"TU_PASSWORD"}'

# Usarlo
curl -s http://localhost:8000/api/predios/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Endpoints

### Propietarios (CRUD)
| Metodo | Ruta | Descripcion |
|---|---|---|
| GET/POST | `/api/propietarios/` | Listar / crear |
| GET/PUT/PATCH/DELETE | `/api/propietarios/{id}/` | Detalle (incluye sus predios) / editar / borrar |

### Predios (CRUD + consultas espaciales)
| Metodo | Ruta | Descripcion |
|---|---|---|
| GET/POST | `/api/predios/` | Listar / crear |
| GET | `/api/predios/{numero_predial}/` | Consulta por numero predial (incluye riesgos) |
| GET | `/api/predios/?condicion=PH` | Filtrar por condicion |
| GET | `/api/predios/?nivel_riesgo=ALTO` | Predios en zonas de un nivel de riesgo |
| GET | `/api/predios/por-ubicacion/?lon=&lat=` | Predio que contiene una coordenada |
| GET | `/api/predios/cercanos/?lon=&lat=&radio=` | Predios en un radio (metros) de un punto |
| GET | `/api/predios/{numero_predial}/riesgos/` | Riesgos que afectan al predio |

### Zonas de riesgo (CRUD + estadistica)
| Metodo | Ruta | Descripcion |
|---|---|---|
| GET/POST | `/api/zonas-riesgo/` | Listar / crear |
| GET | `/api/zonas-riesgo/estadisticas/` | Predios afectados por nivel de riesgo |

### Documentacion interactiva
- Swagger UI: `http://localhost:8000/api/docs/`
- Esquema OpenAPI: `http://localhost:8000/api/schema/`

## Decisiones tecnicas

### Doble SRID: almacenamiento vs. metrico
- **EPSG:4326 (WGS84)** para almacenar e intercambiar geometrias
  (estandar de GeoJSON y clientes web/QGIS/ArcGIS).
- **EPSG:9377 (MAGNA-SIRGAS / CTM12)** para calculos metricos: es el
  origen unico nacional adoptado por el IGAC para el catastro
  multiproposito. La consulta de radio reproyecta a 9377 con
  `Transform(...)` para medir en metros reales.

Nota: la version de PROJ del contenedor no incluye el EPSG:9377 de
serie. Se registra mediante una migracion idempotente
(`0000_postgis_y_srid`) con `RunSQL` + `reverse_sql`, garantizando
reproducibilidad desde cero.

### Geometria
`MultiPolygonField(srid=4326)` para predios y zonas: un predio puede
tener partes disjuntas. Indice espacial GiST activado (`spatial_index`).

### Modelo de datos y LADM-COL
- `Predio` ~ `LA_BAUnit` (unidad predial, Numero Predial Nacional 30 digitos).
- `Propietario` ~ `Interesado` (LA_Party).
- `Copropiedad` (tabla intermedia con porcentaje) ~ Derecho/RRR con cuota.
- `ZonaRiesgo` ~ gestion del riesgo de desastres (Ley 1523 de 2012).

La FK `Predio.propietario` usa `PROTECT`: no se elimina un titular con
predios (decision de dominio catastral).

### Verificacion cruzada
Cada consulta espacial de la API fue validada contra SQL crudo sobre
PostGIS (`ST_Intersects`, `ST_Contains`, `ST_DWithin` con `geography`),
confirmando resultados identicos.

## Escalabilidad

Optimizaciones implementadas:
- **Indices GiST** en geometrias: los cruces espaciales no escanean toda
  la tabla.
- **Agregacion en base de datos** (`Union`, `Count`): la estadistica no
  trae registros a Python.
- **`select_related` / `prefetch_related`**: evitan el problema N+1.
- **Paginacion** (20 por pagina) e **indices B-Tree** en campos de filtro.
- **JWT stateless**: facilita el escalado horizontal.

Siguientes pasos para gran escala (documentados conscientemente):
- Servir con **gunicorn** (incluido en requirements) + nginx en produccion,
  en lugar del `runserver` de desarrollo.
- Columna geometrica **pre-proyectada a 9377** con su propio indice GiST,
  para que la consulta de radio no reproyecte al vuelo.
- **Cache** (Redis) para respuestas costosas y poco cambiantes (estadistica).

## Estructura del proyecto

```
mini-catastro/
  docker-compose.yml    # db (PostGIS) + web (Django)
  Dockerfile            # imagen web con GDAL/GEOS/PROJ
  requirements.txt
  .env.example          # plantilla (el .env real no se versiona)
  manage.py
  config/               # proyecto Django (settings, urls, wsgi)
  catastro/             # app de negocio
    models.py           # Propietario, Predio, ZonaRiesgo, Copropiedad
    serializers.py      # salida GeoJSON
    views.py            # ViewSets + acciones espaciales
    filters.py          # filtros (condicion, nivel de riesgo)
    urls.py             # router DRF
    migrations/         # 0000 PostGIS+SRID 9377, 0001 modelos
  fixtures/initial_data.json    # datos de ejemplo
  scripts/build_fixture.py      # generador del fixture
```
## Seguridad

- Autenticacion **JWT** (`IsAuthenticated` por defecto en toda la API).
- Secretos **fuera del repositorio**: se leen de `.env` (via
  `django-environ`); solo se versiona `.env.example`.

## Respaldo de la base de datos

Se entrega el fixture (`fixtures/initial_data.json`). Para generar un
`.backup` con `pg_dump`, con los contenedores arriba:

```bash
docker compose exec db pg_dump -U catastro -Fc catastro > catastro.backup
```
