"""Serializadores de la API Mini-Catastro."""
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Copropiedad, Predio, Propietario, ZonaRiesgo


class ZonaRiesgoSerializer(GeoFeatureModelSerializer):
    """Salida GeoJSON de una zona de riesgo."""

    nivel_riesgo_display = serializers.CharField(
        source="get_nivel_riesgo_display", read_only=True
    )

    class Meta:
        model = ZonaRiesgo
        geo_field = "poligono"
        fields = ["id", "nombre", "nivel_riesgo", "nivel_riesgo_display", "poligono"]


class RiesgoResumenSerializer(serializers.Serializer):
    """Riesgo que afecta a un predio (sin geometria, version ligera)."""

    id = serializers.IntegerField()
    nombre = serializers.CharField()
    nivel_riesgo = serializers.CharField()
    nivel_riesgo_display = serializers.CharField(source="get_nivel_riesgo_display")


class PredioListSerializer(GeoFeatureModelSerializer):
    """Serializador de listado (ligero)."""

    condicion_predio_display = serializers.CharField(
        source="get_condicion_predio_display", read_only=True
    )
    propietario_nombre = serializers.CharField(
        source="propietario.nombre_completo", read_only=True
    )

    class Meta:
        model = Predio
        geo_field = "poligono"
        fields = [
            "id", "numero_predial", "nombre_direccion", "condicion_predio",
            "condicion_predio_display", "propietario", "propietario_nombre",
            "poligono",
        ]


class PredioDetailSerializer(GeoFeatureModelSerializer):
    """Detalle de predio: incluye las zonas de riesgo que lo intersectan."""

    condicion_predio_display = serializers.CharField(
        source="get_condicion_predio_display", read_only=True
    )
    propietario_nombre = serializers.CharField(
        source="propietario.nombre_completo", read_only=True
    )
    riesgos = serializers.SerializerMethodField()

    class Meta:
        model = Predio
        geo_field = "poligono"
        fields = [
            "id", "numero_predial", "nombre_direccion", "condicion_predio",
            "condicion_predio_display", "propietario", "propietario_nombre",
            "riesgos", "poligono",
        ]

    @extend_schema_field(RiesgoResumenSerializer(many=True))
    def get_riesgos(self, obj):
        zonas = ZonaRiesgo.objects.filter(poligono__intersects=obj.poligono)
        return RiesgoResumenSerializer(zonas, many=True).data


class PredioAnidadoSerializer(serializers.ModelSerializer):
    """Predio plano (sin geometria) para anidar en Propietario."""

    condicion_predio_display = serializers.CharField(
        source="get_condicion_predio_display", read_only=True
    )

    class Meta:
        model = Predio
        fields = [
            "id", "numero_predial", "nombre_direccion",
            "condicion_predio", "condicion_predio_display",
        ]


class CopropiedadAnidadaSerializer(serializers.ModelSerializer):
    """Participacion de copropiedad para anidar en Propietario."""

    numero_predial = serializers.CharField(
        source="predio.numero_predial", read_only=True
    )

    class Meta:
        model = Copropiedad
        fields = ["predio", "numero_predial", "porcentaje_participacion"]


class PropietarioSerializer(serializers.ModelSerializer):
    """CRUD de propietario. En consulta anida sus predios y copropiedades."""

    predios = PredioAnidadoSerializer(many=True, read_only=True)
    copropiedades = CopropiedadAnidadaSerializer(many=True, read_only=True)

    class Meta:
        model = Propietario
        fields = [
            "id", "documento_identidad", "nombre_completo",
            "correo_electronico", "telefono", "predios", "copropiedades",
        ]
