"""App web interactiva de Restaurantes de Nueva York (AE4 - Semana 6/7).

Ejecutar en local (desde la raíz del repositorio):
    streamlit run src/clases_po/app.py

En Streamlit Community Cloud: Main file path = src/clases_po/app.py (o AE4/app.py)
"""
import importlib
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

AQUI = Path(__file__).resolve().parent                 # src/clases_po
RAIZ = AQUI.parent.parent                              # raíz del repositorio
sys.path.insert(0, str(AQUI))                          # importa el módulo sin cargar todo el paquete

import analisis                                        # noqa: E402
import dashboard_streamlit                             # noqa: E402

importlib.reload(analisis)
importlib.reload(dashboard_streamlit)
from dashboard_streamlit import DashboardStreamlit     # noqa: E402

RUTA_AE4 = RAIZ / "AE4" / "datos" / "whatscooking_restaurants_preparado.csv"
RUTA_AE3 = RAIZ / "AE3" / "datos" / "whatscooking_restaurants_preparado.csv"
RUTA_DATOS = RUTA_AE4 if RUTA_AE4.exists() else RUTA_AE3


@st.cache_data(show_spinner="Cargando base preparada de restaurantes de Nueva York (25.159 locales)…")
def cargar_datos(ruta_csv: str, version: str = "ae4_v2") -> pd.DataFrame:
    return DashboardStreamlit.tipar(pd.read_csv(ruta_csv))


DashboardStreamlit(cargar_datos(str(RUTA_DATOS))).render()
