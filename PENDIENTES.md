# Pendientes

- [X] **Migración del SRID 9377**: convertir el INSERT manual de
  MAGNA-SIRGAS/CTM12 en spatial_ref_sys en una migración de datos de
  Django (RunSQL con su reverse), para que se reaplique automáticamente
  en cualquier despliegue. Pues bloquea la reproducibilidad de las consultas
  métricas de los siguientes pasos. RESUELTO:Migración 0000_postgis_y_srid
  con RunSQL idempotente (INSERT...WHERE NOT EXISTS) y su reverse_sql.
  Verificado: ST_Transform a 9377 funciona tras migrate desde cero.
- [X] Migración CreateExtension('postgis') (reproducibilidad de la extensión).
- [ ] Modelos: RESUELTO (Propietario, Predio, ZonaRiesgo, Copropiedad).
- [ ] API REST  (serializadores, vistas, rutas).
- [ ] consultas espaciales
- [ ] fixture, backup, README.
