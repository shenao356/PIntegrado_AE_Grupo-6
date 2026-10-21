"""Clase para generar un reporte resumen de un DataFrame y guardarlo en un archivo .txt.
Actividad 1 - Estudiante de Ingenieria
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd


class Reportes:
    """Esta clase recibe cualquier DataFrame de pandas y arma un reporte claro en texto.
    
    Incluye:
    - Cantidad total de filas y columnas.
    - Cuantas filas duplicadas existen.
    - Lista de columnas con sus tipos de datos.
    - Conteo de datos faltantes (nulos) por columna.
    - Estadisticas descriptivas de las columnas numericas (media, min, max, etc.).
    """

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Crea el texto con todo el resumen del DataFrame."""
        self._validar_dataframe(df)
        numericas = df.select_dtypes(include="number")

        lineas = [
            "REPORTE GENERAL DEL DATAFRAME",
            "=" * 60,
            f"Total de filas: {len(df)}",
            f"Total de columnas: {len(df.columns)}",
            f"Filas duplicadas: {int(df.duplicated().sum())}",
            "",
            "Columnas y tipos de datos:",
            *[f"  - {columna}: {tipo}" for columna, tipo in df.dtypes.items()],
            "",
            "Valores nulos por columna:",
            *[f"  - {columna}: {cantidad}" for columna, cantidad in df.isna().sum().items()],
        ]

        # Si tenemos columnas numericas, agregamos el describe redondeado
        if not numericas.empty:
            lineas += [
                "",
                "Estadisticas de columnas numericas:",
                numericas.describe().round(3).to_string(),
            ]

        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Muestra el reporte directamente en la consola o en el notebook."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte generado dentro de un archivo de texto .txt."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path

    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        """Verifica que el dato recibido sea efectivamente un DataFrame de pandas."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El parametro df debe ser un pandas DataFrame valido.")
