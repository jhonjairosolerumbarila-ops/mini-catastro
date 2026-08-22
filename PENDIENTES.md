# Pendientes

- [ ] **Migración del SRID 9377**: convertir el INSERT manual de
  MAGNA-SIRGAS/CTM12 en spatial_ref_sys en una migración de datos de
  Django (RunSQL con su reverse), para que se reaplique automáticamente
  en cualquier despliegue. Pues bloquea la reproducibilidad de las consultas
  métricas de la Fase 4.
- [ ] Migración CreateExtension('postgis') (reproducibilidad de la extensión).
- [ ] Modelos, API, consultas espaciales, fixture, backup, README.
