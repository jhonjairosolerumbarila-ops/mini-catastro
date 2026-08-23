"""Vistas de la API Mini-Catastro (DRF). Incluye acciones espaciales."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Predio, Propietario, ZonaRiesgo
from .serializers import (
    PredioDetailSerializer,
    PredioListSerializer,
    PropietarioSerializer,
    RiesgoResumenSerializer,
    ZonaRiesgoSerializer,
)


class PropietarioViewSet(viewsets.ModelViewSet):
    """CRUD de propietarios. En consulta anida sus predios y copropiedades."""

    queryset = Propietario.objects.all().prefetch_related(
        "predios", "copropiedades__predio"
    )
    serializer_class = PropietarioSerializer
    search_fields = ["documento_identidad", "nombre_completo", "correo_electronico"]
    ordering_fields = ["nombre_completo", "documento_identidad"]


class PredioViewSet(viewsets.ModelViewSet):
    """CRUD de predios y consultas espaciales."""

    queryset = Predio.objects.select_related("propietario").all()
    search_fields = ["numero_predial", "nombre_direccion"]
    ordering_fields = ["numero_predial", "creado_en"]
    lookup_field = "numero_predial"
    lookup_value_regex = r"\d+"

    def get_serializer_class(self):
        if self.action == "list":
            return PredioListSerializer
        return PredioDetailSerializer

    @action(detail=True, methods=["get"], url_path="riesgos")
    def riesgos(self, request, numero_predial=None):
        predio = self.get_object()
        zonas = ZonaRiesgo.objects.filter(poligono__intersects=predio.poligono)
        return Response(RiesgoResumenSerializer(zonas, many=True).data)


class ZonaRiesgoViewSet(viewsets.ModelViewSet):
    """CRUD de zonas de riesgo."""

    queryset = ZonaRiesgo.objects.all()
    serializer_class = ZonaRiesgoSerializer
    search_fields = ["nombre"]
