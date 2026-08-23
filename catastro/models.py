"""
Modelos del Mini-Catastro.

Relación con LADM-COL:
    - Predio       ≈ LA_BAUnit (unidad predial)
    - Propietario  ≈ Interesado (LA_Party)
    - Copropiedad  ≈ Derecho (RRR) con cuota de participación
    - ZonaRiesgo   ≈ gestión del riesgo (Ley 1523 de 2012)

SRID de almacenamiento: 4326 (WGS84). Los cálculos métricos se hacen
reproyectando a 9377 (MAGNA-SIRGAS/CTM12) en la capa de consultas.
"""
from decimal import Decimal

from django.contrib.gis.db import models as gis_models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

SRID = 4326


class Propietario(models.Model):
    """Interesado / titular de derechos sobre uno o varios predios."""

    documento_identidad = models.CharField(
        "Documento de identidad",
        max_length=20,
        unique=True,
        db_index=True,
    )
    nombre_completo = models.CharField("Nombre completo", max_length=255)
    correo_electronico = models.EmailField("Correo electrónico")
    telefono = models.CharField("Teléfono", max_length=20, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Propietario"
        verbose_name_plural = "Propietarios"
        ordering = ["nombre_completo"]

    def __str__(self):
        return f"{self.nombre_completo} ({self.documento_identidad})"


class Predio(models.Model):
    """Unidad predial georreferenciada."""

    class Condicion(models.TextChoices):
        PH = "PH", "Propiedad Horizontal"
        NPH = "NPH", "No Propiedad Horizontal"
        CONDOMINIO = "CONDOMINIO", "Condominio"
        INFORMAL = "INFORMAL", "Informal"

    numero_predial = models.CharField(
        "Número predial nacional",
        max_length=30,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                r"^\d{30}$",
                "El número predial nacional debe tener 30 dígitos.",
            )
        ],
    )
    nombre_direccion = models.CharField("Nombre o dirección", max_length=255)

    # FK obligatoria: propietario principal (requisito del enunciado).
    propietario = models.ForeignKey(
        Propietario,
        on_delete=models.PROTECT,
        related_name="predios",
        verbose_name="Propietario principal",
    )

    # M2M opcional: copropiedad con porcentaje (a través de tabla intermedia).
    copropietarios = models.ManyToManyField(
        Propietario,
        through="Copropiedad",
        related_name="predios_en_copropiedad",
        blank=True,
    )

    condicion_predio = models.CharField(
        "Condición del predio",
        max_length=20,
        choices=Condicion.choices,
        db_index=True,
    )

    poligono = gis_models.MultiPolygonField(
        "Linderos del predio",
        srid=SRID,
        spatial_index=True,
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Predio"
        verbose_name_plural = "Predios"
        ordering = ["numero_predial"]

    def __str__(self):
        return f"{self.numero_predial} - {self.nombre_direccion}"


class Copropiedad(models.Model):
    """Tabla intermedia: derecho de un propietario sobre un predio."""

    predio = models.ForeignKey(
        Predio, on_delete=models.CASCADE, related_name="copropiedades"
    )
    propietario = models.ForeignKey(
        Propietario, on_delete=models.PROTECT, related_name="copropiedades"
    )
    porcentaje_participacion = models.DecimalField(
        "Porcentaje de participación",
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
    )

    class Meta:
        verbose_name = "Copropiedad"
        verbose_name_plural = "Copropiedades"
        constraints = [
            models.UniqueConstraint(
                fields=["predio", "propietario"],
                name="uq_copropiedad_predio_propietario",
            )
        ]

    def __str__(self):
        return (
            f"{self.propietario} → {self.predio.numero_predial} "
            f"({self.porcentaje_participacion}%)"
        )


class ZonaRiesgo(models.Model):
    """Zona de amenaza / riesgo (inundación, falla geológica, etc.)."""

    class Nivel(models.TextChoices):
        ALTO = "ALTO", "Alto"
        MEDIO = "MEDIO", "Medio"
        BAJO = "BAJO", "Bajo"

    nombre = models.CharField("Nombre", max_length=150)
    nivel_riesgo = models.CharField(
        "Nivel de riesgo",
        max_length=10,
        choices=Nivel.choices,
        db_index=True,
    )
    poligono = gis_models.MultiPolygonField(
        "Área de la zona de riesgo",
        srid=SRID,
        spatial_index=True,
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Zona de riesgo"
        verbose_name_plural = "Zonas de riesgo"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_riesgo_display()})"
