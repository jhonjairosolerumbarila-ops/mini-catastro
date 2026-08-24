# Pendientes

Todos los items resueltos:

- [x] Migracion del SRID 9377 (MAGNA-SIRGAS/CTM12): resuelta en
  0000_postgis_y_srid con RunSQL idempotente + reverse_sql. Verificada
  en arranque desde cero (docker compose down -v && up && migrate).
- [x] Migracion CreateExtension('postgis'): resuelta en 0000.
- [x] Modelos: Propietario, Predio, ZonaRiesgo, Copropiedad (M2M).
- [x] API REST: CRUD + JWT + GeoJSON + Swagger.
- [x] Consultas espaciales (Fase 4): riesgos por predio, predios por
  nivel, radio metrico (CTM12), estadistica. Validadas contra SQL.
- [x] Consulta por ubicacion (punto en poligono).
- [x] Fixture de datos de ejemplo.
- [x] README completo.
