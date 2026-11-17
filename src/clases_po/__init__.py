"""Módulo donde agrupamos las clases reutilizables del Proyecto Integrador (EA1 a AE4)."""
from .analisis import AnalisisBase, AnalisisRestaurantesNYC
from .dashboard_streamlit import DashboardStreamlit
from .reportes import Reportes

try:
    from .hf_loader import HFDatasetLoader
except ImportError:  # En entornos livianos (como Streamlit Cloud) donde no se instala datasets
    HFDatasetLoader = None  # type: ignore[assignment,misc]

__all__ = [
    "HFDatasetLoader",
    "Reportes",
    "AnalisisRestaurantesNYC",
    "AnalisisBase",
    "DashboardStreamlit",
]
