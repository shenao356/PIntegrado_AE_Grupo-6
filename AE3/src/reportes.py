"""Clase para generar y exportar automáticamente el archivo descriptivo .txt del DataFrame final.
Proyecto Integrador - Etapa 2 (AE3): Transformación y Enriquecimiento de Datos.
Siguiendo la metodología trabajada en clase Triple A y en EA1 / AE2.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd


class Reportes:
    """Genera un resumen descriptivo estructurado de un DataFrame de pandas y lo exporta a .txt.

    Incluye:
    - Metadatos del dataset (identificador, split y etapa del proyecto).
    - Cantidad total de filas, columnas y verificación de registros duplicados.
    - Listado completo de nombres de columnas y sus tipos de datos (dtypes).
    - Conteo y porcentaje de valores nulos por columna.
    - Estadísticas descriptivas detalladas de las variables numéricas.
    - Resumen de frecuencias principales de las variables categóricas y booleanas clave.
    """

    def __init__(
        self,
        dataset_id: str = "MongoDB/whatscooking.restaurants",
        split: str = "train",
        etapa: str = "AE3 - Transformación y Enriquecimiento de Datos (Etapa 2)",
    ) -> None:
        self.dataset_id = dataset_id
        self.split = split
        self.etapa = etapa

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Construye el texto completo del reporte descriptivo del DataFrame."""
        self._validar_dataframe(df)
        numericas = df.select_dtypes(include="number")
        booleanas = df.select_dtypes(include="bool")

        lineas = [
            "=" * 78,
            "REPORTE DESCRIPTIVO DEL DATAFRAME TRANSFORMADO Y ENRIQUECIDO (AE3)",
            "=" * 78,
            f"Etapa del Proyecto:              {self.etapa}",
            f"Dataset en Hugging Face:         {self.dataset_id}",
            f"Split / Partición utilizada:     {self.split}",
            f"Total de Filas (Registros):      {len(df):,}",
            f"Total de Columnas (Variables):   {len(df.columns)}",
            f"Filas Duplicadas Exactas:        {int(df.duplicated().sum())}",
            "-" * 78,
            "1. LISTADO DE COLUMNAS Y TIPOS DE DATOS (DTYPES):",
            "-" * 78,
        ]

        for idx, (columna, tipo) in enumerate(df.dtypes.items(), start=1):
            lineas.append(f"  {idx:>2}. {columna:<30} | Tipo: {str(tipo):<12}")

        lineas += [
            "-" * 78,
            "2. CONTEO Y PORCENTAJE DE VALORES NULOS POR COLUMNA:",
            "-" * 78,
        ]
        total_filas = max(len(df), 1)
        for columna, cantidad in df.isna().sum().items():
            pct = (int(cantidad) / total_filas) * 100
            lineas.append(f"  - {columna:<32} | Nulos: {int(cantidad):>5} ({pct:>6.2f} %)")

        if not numericas.empty:
            lineas += [
                "-" * 78,
                "3. ESTADÍSTICAS DESCRIPTIVAS DE VARIABLES NUMÉRICAS:",
                "-" * 78,
                numericas.describe().round(3).to_string(),
            ]

        if not booleanas.empty:
            lineas += [
                "-" * 78,
                "4. DISTRIBUCIÓN DE VARIABLES LÓGICAS / BOOLEANAS (SERVICIOS):",
                "-" * 78,
            ]
            for col in booleanas.columns:
                positivos = int(df[col].sum())
                pct_pos = (positivos / total_filas) * 100
                lineas.append(
                    f"  - {col:<32} | Sí (True): {positivos:>6,} ({pct_pos:>6.2f} %) | No (False): {total_filas - positivos:>6,}"
                )

        cols_cat_clave = [
            c
            for c in [
                "Barrio",
                "Familia_Culinaria",
                "Categoria_Precio",
                "Categoria_Precio_Declarada",
                "Segmento_Reputacion",
                "Nivel_Servicios",
            ]
            if c in df.columns
        ]
        if cols_cat_clave:
            lineas += [
                "-" * 78,
                "5. DISTRIBUCIÓN DE VARIABLES CATEGÓRICAS E INDICADORES DERIVADOS CLAVE:",
                "-" * 78,
            ]
            for col in cols_cat_clave:
                lineas.append(f"Variable: {col}")
                conteos = df[col].value_counts(dropna=False)
                for cat, cant in conteos.items():
                    pct_cat = (int(cant) / total_filas) * 100
                    lineas.append(f"    * {str(cat):<42}: {int(cant):>6,} ({pct_cat:>6.2f} %)")
                lineas.append("")

        lineas += [
            "=" * 78,
            "Fin del reporte automático generado a partir del DataFrame final preparado.",
            "=" * 78,
        ]

        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Muestra el reporte directamente en pantalla."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte generado en un archivo .txt con codificación UTF-8."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path

    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El parámetro df debe ser un pandas DataFrame válido.")
