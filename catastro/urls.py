"""Enrutamiento de la API de negocio (router de DRF)."""
from rest_framework.routers import DefaultRouter

from .views import PredioViewSet, PropietarioViewSet, ZonaRiesgoViewSet

router = DefaultRouter()
router.register(r"propietarios", PropietarioViewSet, basename="propietario")
router.register(r"predios", PredioViewSet, basename="predio")
router.register(r"zonas-riesgo", ZonaRiesgoViewSet, basename="zonariesgo")

urlpatterns = router.urls
