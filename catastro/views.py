"""
Vistas de la API Mini-Catastro (Django REST Framework).
"""
from rest_framework import viewsets

from .models import Predio, Propietario, ZonaRiesgo
from .serializers import (
    PredioListSerializer,
    PropietarioSerializer,
    ZonaRiesgoSerializer,
)


class PropietarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de propietarios.

    En consulta/detalle la respuesta incluye el listado de predios de los
    que es titular (campo `predios`) y sus copropiedades.
    """

    queryset = Propietario.objects.all().prefetch_related(
        "predios", "copropiedades__predio"
    )
    serializer_class = PropietarioSerializer
    search_fields = ["documento_identidad", "nombre_completo", "correo_electronico"]
    ordering_fields = ["nombre_completo", "documento_identidad"]


class PredioViewSet(viewsets.ModelViewSet):
    """CRUD de predios."""

    queryset = Predio.objects.select_related("propietario").all()
    serializer_class = PredioListSerializer
    search_fields = ["numero_predial", "nombre_direccion"]
    ordering_fields = ["numero_predial", "creado_en"]

    # El número predial es un identificador de negocio único: se usa como
    # lookup en la URL (más RESTful que el id interno).
    lookup_field = "numero_predial"
    lookup_value_regex = r"\d+"


class ZonaRiesgoViewSet(viewsets.ModelViewSet):
    """CRUD de zonas de riesgo."""

    queryset = ZonaRiesgo.objects.all()
    serializer_class = ZonaRiesgoSerializer
    search_fields = ["nombre"]
