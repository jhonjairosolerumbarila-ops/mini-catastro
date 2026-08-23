"""Filtros declarativos para la API de predios."""
import django_filters
from django.contrib.gis.db.models.aggregates import Union

from .models import Predio, ZonaRiesgo


class PredioFilter(django_filters.FilterSet):
    """Filtros: por condicion y por nivel de riesgo (cruce espacial)."""

    condicion = django_filters.ChoiceFilter(
        field_name="condicion_predio", choices=Predio.Condicion.choices
    )
    numero_predial = django_filters.CharFilter(
        field_name="numero_predial", lookup_expr="exact"
    )
    nivel_riesgo = django_filters.ChoiceFilter(
        choices=ZonaRiesgo.Nivel.choices,
        method="filtrar_por_nivel_riesgo",
        label="Nivel de riesgo (cruce espacial)",
    )

    class Meta:
        model = Predio
        fields = ["condicion", "numero_predial", "nivel_riesgo"]

    def filtrar_por_nivel_riesgo(self, queryset, name, value):
        combinada = ZonaRiesgo.objects.filter(nivel_riesgo=value).aggregate(
            geom=Union("poligono")
        )["geom"]
        if combinada is None:
            return queryset.none()
        return queryset.filter(poligono__intersects=combinada)
