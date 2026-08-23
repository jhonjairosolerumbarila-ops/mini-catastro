"""Vistas de la API Mini-Catastro (DRF). Incluye acciones espaciales."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.aggregates import Union
from django.db.models import Count

from .models import Predio, Propietario, ZonaRiesgo
from .filters import PredioFilter
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
    filterset_class = PredioFilter
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

    @action(detail=False, methods=["get"], url_path="cercanos")
    def cercanos(self, request):
        """Predios dentro de un radio (metros) de un punto. Usa CTM12 (9377)."""
        try:
            lon = float(request.query_params["lon"])
            lat = float(request.query_params["lat"])
            radio = float(request.query_params["radio"])
        except (KeyError, ValueError):
            return Response(
                {"detail": "Parametros requeridos: lon, lat, radio (numericos)."},
                status=400,
            )
        punto = Point(lon, lat, srid=settings.SRID_ALMACENAMIENTO)
        punto_m = punto.transform(settings.SRID_METRICO, clone=True)
        predios = (
            self.get_queryset()
            .annotate(geom_ctm=Transform("poligono", settings.SRID_METRICO))
            .filter(geom_ctm__dwithin=(punto_m, D(m=radio)))
        )
        serializer = PredioListSerializer(predios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por-ubicacion")
    def por_ubicacion(self, request):
        """Predio(s) que contienen una coordenada (punto en poligono)."""
        try:
            lon = float(request.query_params["lon"])
            lat = float(request.query_params["lat"])
        except (KeyError, ValueError):
            return Response(
                {"detail": "Parametros requeridos: lon, lat (numericos)."},
                status=400,
            )
        punto = Point(lon, lat, srid=settings.SRID_ALMACENAMIENTO)
        predios = self.get_queryset().filter(poligono__contains=punto)
        serializer = PredioListSerializer(predios, many=True)
        return Response(serializer.data)


class ZonaRiesgoViewSet(viewsets.ModelViewSet):
    """CRUD de zonas de riesgo."""

    queryset = ZonaRiesgo.objects.all()

    @action(detail=False, methods=["get"], url_path="estadisticas")
    def estadisticas(self, request):
        """Cantidad de predios afectados por cada nivel de riesgo."""
        resultado = []
        for nivel, etiqueta in ZonaRiesgo.Nivel.choices:
            combinada = ZonaRiesgo.objects.filter(nivel_riesgo=nivel).aggregate(
                geom=Union("poligono")
            )["geom"]
            if combinada is None:
                afectados = 0
            else:
                afectados = Predio.objects.filter(
                    poligono__intersects=combinada
                ).count()
            resultado.append({
                "nivel_riesgo": nivel,
                "nivel_riesgo_display": etiqueta,
                "zonas": ZonaRiesgo.objects.filter(nivel_riesgo=nivel).count(),
                "predios_afectados": afectados,
            })
        return Response({
            "resumen_por_nivel": resultado,
            "total_zonas": ZonaRiesgo.objects.count(),
            "total_predios": Predio.objects.count(),
        })
    serializer_class = ZonaRiesgoSerializer
    search_fields = ["nombre"]
