"""Módulo de analítica descriptiva y cálculo de métricas de restaurantes en Nueva York (AE4).

La clase :class:`AnalisisRestaurantesNYC` encapsula todas las métricas, indicadores clave (KPIs),
tablas de frecuencia y cruces multivariados que responden las cinco preguntas de negocio (PN1 a PN5)
sobre el dataset preparado y enriquecido en la Etapa 2 (AE3: 25.159 restaurantes × 27 columnas).

Al centralizar los cálculos en esta clase:
1. El notebook de la AE4 y la aplicación web de Streamlit utilizan exactamente las mismas fórmulas.
2. Si el usuario aplica filtros en la barra lateral de Streamlit, todas las tablas, métricas y textos
   se recalculan dinámicamente sin valores escritos a mano.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ORDEN_BARRIOS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]

ORDEN_PRECIOS = [
    "1 - Económico ($)",
    "2 - Moderado ($$)",
    "3 - Costoso ($$$)",
    "4 - Gourmet / Exclusivo ($$$$)",
]

ORDEN_PRECIOS_DECLARADOS = [
    "1 - Económico ($)",
    "2 - Moderado ($$)",
    "3 - Costoso ($$$)",
    "4 - Gourmet / Exclusivo ($$$$)",
    "No Especificado",
]

ORDEN_SERVICIOS = [
    "1. Básico (1 servicio)",
    "2. Intermedio (2 servicios)",
    "3. Completo / Multipropósito (3-4 servicios)",
]

ORDEN_REPUTACION = [
    "1. Excelente (4.5 - 5.0 ★)",
    "2. Sobresaliente (4.0 ★)",
    "3. Aceptable (3.0 - 3.5 ★)",
    "4. Baja Valoración (< 3.0 ★)",
]

ORDEN_FAMILIAS = [
    "Norteamericana",
    "Europea y Mediterránea",
    "Asiática",
    "Cafetería, Panadería y Postres",
    "Latinoamericana y Caribeña",
    "Otras Cocinas del Mundo",
    "Sandwiches, Deli y Casual",
    "Saludable, Vegetariana y Bebidas",
]


class AnalisisRestaurantesNYC:
    """Motor de métricas y tablas de resultados para los restaurantes de Nueva York."""

    def __init__(self, df: pd.DataFrame, df_total: pd.DataFrame | None = None):
        """Inicializa el analizador con el DataFrame activo (filtrado o completo) y la base global."""
        self.R = df.copy()
        self.R_total = df_total.copy() if df_total is not None else df.copy()

    # ==================================================================
    # 1. DEFINICIÓN FORMAL DE MÉTRICAS (Rúbrica AE4 - Instrucción 1)
    # ==================================================================
    @staticmethod
    def tabla_definicion_metricas() -> pd.DataFrame:
        """Devuelve la definición formal de cada métrica utilizada, su fórmula, unidad y pregunta asociada."""
        filas = [
            (
                "M1",
                "Oferta y Participación de Restaurantes",
                "N_i = count(ID_Restaurante)  |  %_i = (N_i / N_total) * 100",
                "Establecimientos (locales) y porcentaje (%)",
                "PN1, PN2, PN3, PN4, PN5",
                "Cuantifica el tamaño absoluto y peso relativo de cada distrito, cocina, nivel de precio o servicio.",
            ),
            (
                "M2",
                "Densidad Comercial Superficial",
                "Densidad_km2 = N_distrito / Superficie_Km2",
                "Restaurantes por km² (locales/km²)",
                "PN1",
                "Mide la saturación territorial física de establecimientos por kilómetro cuadrado en cada distrito.",
            ),
            (
                "M3",
                "Densidad Comercial Demográfica",
                "Densidad_10k = (N_distrito / Poblacion_Distrito) * 10.000",
                "Restaurantes por cada 10.000 habitantes (locales/10k hab.)",
                "PN1",
                "Contextualiza la oferta gastronómica frente a la población residente oficial del Censo de NYC.",
            ),
            (
                "M4",
                "Volumen y Promedio de Reseñas (Tracción)",
                "Suma = sum(Total_Resenas)  |  Media = mean(Total_Resenas)  |  Mediana = median(Total_Resenas)",
                "Reseñas (opiniones de clientes)",
                "PN1, PN2, PN3, PN4, PN5",
                "Aproxima el flujo de interacción y visibilidad digital acumulada por establecimiento (no equivale a ventas en $).",
            ),
            (
                "M5",
                "Calificación Promedio Simple",
                "R_bar = mean(Calificacion)",
                "Estrellas (escala de 1,0 a 5,0 ★)",
                "PN1, PN2, PN3, PN4, PN5",
                "Mide la satisfacción directa declarada por los comensales en la plataforma.",
            ),
            (
                "M6",
                "Índice de Reputación Ponderada (Bayesiana)",
                "IRP = (v / (v + m)) * R + (m / (v + m)) * C   (m = 50 reseñas, C = 3,5327 ★)",
                "Estrellas ponderadas (escala de 1,0 a 5,0 ★)",
                "PN1, PN2, PN3, PN4, PN5",
                "Corrige el sesgo de muestras pequeñas estabilizando la calificación hacia la media global de NYC.",
            ),
            (
                "M7",
                "Puntaje de Popularidad (Tracción Comercial)",
                "Popularidad = Calificacion * Total_Resenas",
                "Puntos de popularidad ponderada (pts)",
                "PN1, PN2, PN3, PN4, PN5",
                "Combina satisfacción y volumen de reseñas para identificar los formatos con mayor reconocimiento acumulado.",
            ),
            (
                "M8",
                "Tasa de Alta Reputación (≥ 4,0 ★)",
                "% Alta Rep. = (count(Calificacion >= 4.0) / N_grupo) * 100",
                "Porcentaje de locales sobresalientes/excelentes (%)",
                "PN1, PN2, PN3, PN4, PN5",
                "Mide la proporción de restaurantes que alcanzan calificaciones sobresalientes (4,0 ★) o excelentes (4,5–5,0 ★).",
            ),
            (
                "M9",
                "Equipamiento de Servicios de Conveniencia",
                "Total_Servicios = Para_Llevar + Mesas_Exteriores + Hora_Feliz + Permite_Mascotas",
                "Cantidad de servicios activos (1 a 4 servicios) y % de adopción",
                "PN4",
                "Evalúa la dotación operativa del local (Básico: 1, Intermedio: 2, Completo/Multipropósito: 3 a 4 servicios).",
            ),
        ]
        return pd.DataFrame(
            filas,
            columns=[
                "Código",
                "Métrica / Indicador",
                "Fórmula de Cálculo",
                "Unidad de Medida",
                "Preguntas que Responde",
                "Propósito Analítico",
            ],
        )

    # ==================================================================
    # 2. INDICADORES CLAVE (KPIs) Y ESTADÍSTICAS DESCRIPTIVAS
    # ==================================================================
    def kpis(self) -> dict[str, float]:
        """Calcula los indicadores clave (KPIs) sobre el DataFrame activo."""
        R = self.R
        if R.empty:
            return {
                "Restaurantes": 0,
                "% del total NYC": 0.0,
                "Reseñas acumuladas": 0,
                "Promedio reseñas": 0.0,
                "Mediana reseñas": 0.0,
                "Calificación promedio": 0.0,
                "Reputación ponderada": 0.0,
                "Popularidad promedio": 0.0,
                "% Alta reputación": 0.0,
                "Densidad km2": 0.0,
                "Densidad 10k hab": 0.0,
                "Servicios promedio": 0.0,
            }

        # Superficie y población de los distritos presentes en la vista filtrada
        distritos_unicos = R[["Barrio", "Poblacion_Distrito", "Superficie_Km2"]].drop_duplicates("Barrio")
        sup_total = float(distritos_unicos["Superficie_Km2"].sum())
        pob_total = float(distritos_unicos["Poblacion_Distrito"].sum())

        n_rest = len(R)
        n_total = max(len(self.R_total), 1)
        alta_rep = float((R["Calificacion"] >= 4.0).mean())

        return {
            "Restaurantes": n_rest,
            "% del total NYC": n_rest / n_total,
            "Reseñas acumuladas": int(R["Total_Resenas"].sum()),
            "Promedio reseñas": float(R["Total_Resenas"].mean()),
            "Mediana reseñas": float(R["Total_Resenas"].median()),
            "Calificación promedio": float(R["Calificacion"].mean()),
            "Reputación ponderada": float(R["Indice_Reputacion_Ponderada"].mean()),
            "Popularidad promedio": float(R["Puntaje_Popularidad"].mean()),
            "% Alta reputación": alta_rep,
            "Densidad km2": n_rest / sup_total if sup_total > 0 else 0.0,
            "Densidad 10k hab": (n_rest / pob_total) * 10000.0 if pob_total > 0 else 0.0,
            "Servicios promedio": float(R["Total_Servicios"].mean()),
        }

    @staticmethod
    def medidas(s: pd.Series) -> pd.Series:
        """Estadísticos descriptivos completos de una serie numérica (estilo Semana 5/6)."""
        s = s.dropna().astype(float)
        if s.empty:
            return pd.Series(dtype=float)
        media = s.mean()
        return pd.Series({
            "n (datos)": s.count(),
            "Suma": s.sum(),
            "Media": media,
            "Mediana": s.median(),
            "Moda": s.mode().iloc[0] if not s.mode().empty else np.nan,
            "Mínimo": s.min(),
            "Máximo": s.max(),
            "Rango": s.max() - s.min(),
            "Desviación estándar": s.std(ddof=1),
            "Coef. de variación": s.std(ddof=1) / media if media != 0 else np.nan,
            "Q1 (25 %)": s.quantile(0.25),
            "Q3 (75 %)": s.quantile(0.75),
        })

    def medidas_variables(self) -> pd.DataFrame:
        """Tabla resumen de estadísticos descriptivos para las variables cuantitativas clave."""
        cols = [
            "Calificacion",
            "Indice_Reputacion_Ponderada",
            "Total_Resenas",
            "Puntaje_Popularidad",
            "Rango_Precio",
            "Total_Servicios",
            "Cantidad_Platos_Menu",
        ]
        cols = [c for c in cols if c in self.R.columns]
        return pd.DataFrame({c: self.medidas(self.R[c]) for c in cols}).round(3)

    # ==================================================================
    # 3. PREGUNTA DE NEGOCIO 1 (PN1): Distritos y Densidad Demográfica
    # ==================================================================
    def pn1_distribucion_distritos(self, incluir_total: bool = False) -> pd.DataFrame:
        """Calcula la tabla de resultados para PN1 por distrito (Barrio)."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        t = (
            R.groupby("Barrio", observed=True)
            .agg(
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
                Poblacion_Distrito=("Poblacion_Distrito", "first"),
                Superficie_Km2=("Superficie_Km2", "first"),
                Vocacion_Comercial=("Vocacion_Comercial", "first"),
            )
            .reset_index()
        )
        t["Barrio"] = t["Barrio"].astype(str)
        t = t.sort_values("Restaurantes", ascending=False).reset_index(drop=True)

        total_rest = max(t["Restaurantes"].sum(), 1)
        total_res = max(t["Resenas_Acumuladas"].sum(), 1)
        t.insert(2, "Participacion_Locales_Pct", (t["Restaurantes"] / total_rest) * 100.0)
        t.insert(4, "Participacion_Resenas_Pct", (t["Resenas_Acumuladas"] / total_res) * 100.0)
        t.insert(9, "Locales_por_Km2", t["Restaurantes"] / t["Superficie_Km2"])
        t.insert(10, "Locales_por_10k_Hab", (t["Restaurantes"] / t["Poblacion_Distrito"]) * 10000.0)

        if incluir_total and len(t) > 1:
            sup_tot = float(t["Superficie_Km2"].sum())
            pob_tot = int(t["Poblacion_Distrito"].sum())
            fila_tot = pd.DataFrame([{
                "Barrio": "TOTAL / GLOBAL NYC",
                "Restaurantes": int(t["Restaurantes"].sum()),
                "Participacion_Locales_Pct": 100.0,
                "Resenas_Acumuladas": int(t["Resenas_Acumuladas"].sum()),
                "Participacion_Resenas_Pct": 100.0,
                "Promedio_Resenas": float(R["Total_Resenas"].mean()),
                "Calificacion_Promedio": float(R["Calificacion"].mean()),
                "Reputacion_Ponderada": float(R["Indice_Reputacion_Ponderada"].mean()),
                "Popularidad_Promedio": float(R["Puntaje_Popularidad"].mean()),
                "Pct_Alta_Reputacion": float((R["Calificacion"] >= 4.0).mean() * 100.0),
                "Locales_por_Km2": float(len(R) / sup_tot) if sup_tot > 0 else 0.0,
                "Locales_por_10k_Hab": float((len(R) / pob_tot) * 10000.0) if pob_tot > 0 else 0.0,
                "Poblacion_Distrito": pob_tot,
                "Superficie_Km2": sup_tot,
                "Vocacion_Comercial": "Consolidado distritos seleccionados",
            }])
            t = pd.concat([t, fila_tot], ignore_index=True)

        cols_redondear = [
            "Participacion_Locales_Pct",
            "Participacion_Resenas_Pct",
            "Promedio_Resenas",
            "Calificacion_Promedio",
            "Reputacion_Ponderada",
            "Popularidad_Promedio",
            "Pct_Alta_Reputacion",
            "Locales_por_Km2",
            "Locales_por_10k_Hab",
        ]
        t[cols_redondear] = t[cols_redondear].round(2)
        return t

    # ==================================================================
    # 4. PREGUNTA DE NEGOCIO 2 (PN2): Familias y Especialidades Culinarias
    # ==================================================================
    def pn2_familias_culinarias(self) -> pd.DataFrame:
        """Calcula la tabla de resultados para PN2-A por macro-familia gastronómica (Familia_Culinaria)."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        t = (
            R.groupby("Familia_Culinaria", observed=True)
            .agg(
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Precio_Promedio=("Rango_Precio", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
            )
            .reset_index()
        )
        t["Familia_Culinaria"] = t["Familia_Culinaria"].astype(str)
        t = t.sort_values("Restaurantes", ascending=False).reset_index(drop=True)
        total_rest = max(t["Restaurantes"].sum(), 1)
        total_res = max(t["Resenas_Acumuladas"].sum(), 1)
        t["Participacion_Locales_Pct"] = (t["Restaurantes"] / total_rest) * 100.0
        t["Participacion_Resenas_Pct"] = (t["Resenas_Acumuladas"] / total_res) * 100.0
        return t.round(2)

    def pn2_especialidades_culinarias(self, top_n: int | None = 15) -> pd.DataFrame:
        """Calcula la tabla de resultados para PN2-B por especialidad individual (Tipo_Cocina)."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        total_global = max(len(R), 1)
        t = (
            R.groupby("Tipo_Cocina", observed=True)
            .agg(
                Familia_Culinaria=("Familia_Culinaria", "first"),
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Precio_Promedio=("Rango_Precio", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
            )
            .reset_index()
        )
        t["Tipo_Cocina"] = t["Tipo_Cocina"].astype(str)
        t["Familia_Culinaria"] = t["Familia_Culinaria"].astype(str)
        t["Participacion_Locales_Pct"] = (t["Restaurantes"] / total_global) * 100.0
        t = t.sort_values(["Restaurantes", "Resenas_Acumuladas"], ascending=[False, False]).reset_index(drop=True)
        if top_n is not None:
            t = t.head(top_n)
        return t.round(2)

    # ==================================================================
    # 5. PREGUNTA DE NEGOCIO 3 (PN3): Segmentos de Precio y Satisfacción
    # ==================================================================
    def pn3_segmentos_precio_declarado(self) -> pd.DataFrame:
        """Calcula la tabla PN3-A según Categoria_Precio_Declarada (incluyendo 'No Especificado')."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        t = (
            R.groupby("Categoria_Precio_Declarada", observed=True)
            .agg(
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Mediana_Resenas=("Total_Resenas", "median"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
            )
            .reset_index()
        )
        t["Categoria_Precio_Declarada"] = pd.Categorical(
            t["Categoria_Precio_Declarada"].astype(str),
            categories=[c for c in ORDEN_PRECIOS_DECLARADOS if c in set(t["Categoria_Precio_Declarada"].astype(str))],
            ordered=True,
        )
        t = t.sort_values("Categoria_Precio_Declarada").reset_index(drop=True)
        t["Categoria_Precio_Declarada"] = t["Categoria_Precio_Declarada"].astype(str)
        total_rest = max(t["Restaurantes"].sum(), 1)
        total_res = max(t["Resenas_Acumuladas"].sum(), 1)
        t["Participacion_Locales_Pct"] = (t["Restaurantes"] / total_rest) * 100.0
        t["Participacion_Resenas_Pct"] = (t["Resenas_Acumuladas"] / total_res) * 100.0
        return t.round(2)

    def pn3_segmentos_precio_imputado(self) -> pd.DataFrame:
        """Calcula la tabla PN3-B según Rango_Precio y Categoria_Precio (tras imputación condicional)."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        t = (
            R.groupby(["Rango_Precio", "Categoria_Precio"], observed=True)
            .agg(
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Mediana_Resenas=("Total_Resenas", "median"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
            )
            .reset_index()
            .sort_values("Rango_Precio")
            .reset_index(drop=True)
        )
        t["Categoria_Precio"] = t["Categoria_Precio"].astype(str)
        total_rest = max(t["Restaurantes"].sum(), 1)
        total_res = max(t["Resenas_Acumuladas"].sum(), 1)
        t["Participacion_Locales_Pct"] = (t["Restaurantes"] / total_rest) * 100.0
        t["Participacion_Resenas_Pct"] = (t["Resenas_Acumuladas"] / total_res) * 100.0
        return t.round(2)

    # ==================================================================
    # 6. PREGUNTA DE NEGOCIO 4 (PN4): Servicios de Conveniencia
    # ==================================================================
    def pn4_servicios_conveniencia(self) -> pd.DataFrame:
        """Calcula la tabla PN4 por Nivel_Servicios (Básico, Intermedio, Completo)."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        t = (
            R.groupby("Nivel_Servicios", observed=True)
            .agg(
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Mediana_Resenas=("Total_Resenas", "median"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
                Pct_Para_Llevar=("Para_Llevar", lambda x: x.mean() * 100.0),
                Pct_Mesas_Exteriores=("Mesas_Exteriores", lambda x: x.mean() * 100.0),
                Pct_Hora_Feliz=("Hora_Feliz", lambda x: x.mean() * 100.0),
                Pct_Permite_Mascotas=("Permite_Mascotas", lambda x: x.mean() * 100.0),
            )
            .reset_index()
        )
        t["Nivel_Servicios"] = pd.Categorical(
            t["Nivel_Servicios"].astype(str),
            categories=[c for c in ORDEN_SERVICIOS if c in set(t["Nivel_Servicios"].astype(str))],
            ordered=True,
        )
        t = t.sort_values("Nivel_Servicios").reset_index(drop=True)
        t["Nivel_Servicios"] = t["Nivel_Servicios"].astype(str)
        total_rest = max(t["Restaurantes"].sum(), 1)
        total_res = max(t["Resenas_Acumuladas"].sum(), 1)
        t["Participacion_Locales_Pct"] = (t["Restaurantes"] / total_rest) * 100.0
        t["Participacion_Resenas_Pct"] = (t["Resenas_Acumuladas"] / total_res) * 100.0
        return t.round(2)

    def pn4_adopcion_individual(self) -> pd.DataFrame:
        """Calcula el conteo y porcentaje de adopción de cada uno de los 4 servicios booleanos."""
        R = self.R
        if R.empty:
            return pd.DataFrame()
        n = len(R)
        servicios = [
            ("Para_Llevar", "Comida para llevar (TakeOut)"),
            ("Mesas_Exteriores", "Mesas al aire libre (OutdoorSeating)"),
            ("Hora_Feliz", "Hora feliz / promociones (HappyHour)"),
            ("Permite_Mascotas", "Admisión de mascotas (DogsAllowed)"),
        ]
        filas = []
        for col, etiqueta in servicios:
            activos = int(R[col].sum())
            inactivos = n - activos
            sub_si = R[R[col]]
            sub_no = R[~R[col]]
            filas.append({
                "Columna": col,
                "Servicio": etiqueta,
                "Restaurantes_Activos": activos,
                "Adopcion_Pct": round((activos / n) * 100.0, 2),
                "Restaurantes_No_Activos": inactivos,
                "Promedio_Resenas_Si": round(float(sub_si["Total_Resenas"].mean()), 2) if len(sub_si) else 0.0,
                "Promedio_Resenas_No": round(float(sub_no["Total_Resenas"].mean()), 2) if len(sub_no) else 0.0,
                "Popularidad_Si": round(float(sub_si["Puntaje_Popularidad"].mean()), 2) if len(sub_si) else 0.0,
                "Calificacion_Si": round(float(sub_si["Calificacion"].mean()), 2) if len(sub_si) else 0.0,
            })
        return pd.DataFrame(filas)

    # ==================================================================
    # 7. PREGUNTA DE NEGOCIO 5 (PN5): Matriz Distrito × Precio
    # ==================================================================
    def pn5_matriz_distrito_precio(self) -> pd.DataFrame:
        """Calcula la tabla multivariada PN5 (Barrio × Rango_Precio / Categoria_Precio)."""
        R = self.R
        if R.empty:
            return pd.DataFrame()

        t = (
            R.groupby(["Barrio", "Rango_Precio", "Categoria_Precio"], observed=True)
            .agg(
                Restaurantes=("ID_Restaurante", "count"),
                Resenas_Acumuladas=("Total_Resenas", "sum"),
                Promedio_Resenas=("Total_Resenas", "mean"),
                Calificacion_Promedio=("Calificacion", "mean"),
                Reputacion_Ponderada=("Indice_Reputacion_Ponderada", "mean"),
                Popularidad_Promedio=("Puntaje_Popularidad", "mean"),
                Pct_Alta_Reputacion=("Calificacion", lambda x: (x >= 4.0).mean() * 100.0),
            )
            .reset_index()
        )
        t["Barrio"] = t["Barrio"].astype(str)
        t["Categoria_Precio"] = t["Categoria_Precio"].astype(str)
        tot_distrito = t.groupby("Barrio")["Restaurantes"].transform("sum").replace(0, 1)
        tot_global = max(t["Restaurantes"].sum(), 1)
        t["Participacion_En_Distrito_Pct"] = (t["Restaurantes"] / tot_distrito) * 100.0
        t["Participacion_Global_Pct"] = (t["Restaurantes"] / tot_global) * 100.0
        t = t.sort_values(["Barrio", "Rango_Precio"]).reset_index(drop=True)
        return t.round(2)

    def pn5_pivot(self, metrica: str = "Restaurantes") -> pd.DataFrame:
        """Construye una matriz pivote (Barrio en filas × Categoria_Precio en columnas) para mapas de calor."""
        m = self.pn5_matriz_distrito_precio()
        if m.empty:
            return pd.DataFrame()
        orden_b = [b for b in ORDEN_BARRIOS if b in set(m["Barrio"])]
        orden_p = [p for p in ORDEN_PRECIOS if p in set(m["Categoria_Precio"])]
        piv = m.pivot(index="Barrio", columns="Categoria_Precio", values=metrica).reindex(
            index=orden_b, columns=orden_p
        )
        return piv.fillna(0)

    # ==================================================================
    # 8. RANKINGS Y HALLAZGOS EJECUTIVOS
    # ==================================================================
    def top_restaurantes(self, n: int = 15, criterio: str = "Puntaje_Popularidad") -> pd.DataFrame:
        """Devuelve el Top N de establecimientos según popularidad o reputación ponderada."""
        cols = [
            "ID_Restaurante",
            "Nombre",
            "Barrio",
            "Tipo_Cocina",
            "Familia_Culinaria",
            "Categoria_Precio",
            "Calificacion",
            "Indice_Reputacion_Ponderada",
            "Total_Resenas",
            "Puntaje_Popularidad",
            "Nivel_Servicios",
        ]
        cols = [c for c in cols if c in self.R.columns]
        return self.R.sort_values(criterio, ascending=False).head(n)[cols].reset_index(drop=True)

    def hallazgos(self) -> list[str]:
        """Genera viñetas de hallazgos cuantitativos calculados directamente sobre los datos activos."""
        if self.R.empty:
            return ["No hay registros disponibles con los filtros actuales."]

        k = self.kpis()
        pn1 = self.pn1_distribucion_distritos()
        pn2 = self.pn2_familias_culinarias()
        pn3 = self.pn3_segmentos_precio_imputado()
        pn4 = self.pn4_servicios_conveniencia()

        top_b = pn1.iloc[0]
        ult_b = pn1.iloc[-1]
        top_f = pn2.iloc[0]
        top_trac_f = pn2.sort_values("Popularidad_Promedio", ascending=False).iloc[0]

        res = [
            (
                f"Alcance analizado: {k['Restaurantes']:,} restaurantes en Nueva York "
                f"({k['% del total NYC']:.1%} de la base preparada), que acumulan "
                f"{k['Reseñas acumuladas']:,} reseñas (media de {k['Promedio reseñas']:.2f} reseñas/local; "
                f"calificación media de {k['Calificación promedio']:.2f} ★ y reputación bayesiana de {k['Reputación ponderada']:.2f} ★)."
            ),
            (
                f"PN1 (Distritos y Densidad): {top_b['Barrio']} concentra {int(top_b['Restaurantes']):,} locales "
                f"({top_b['Participacion_Locales_Pct']:.2f} %) con una densidad de {top_b['Locales_por_Km2']:.2f} locales/km² y "
                f"{top_b['Locales_por_10k_Hab']:.2f} locales por 10.000 hab., frente a {ult_b['Barrio']} con "
                f"{int(ult_b['Restaurantes']):,} locales ({ult_b['Locales_por_Km2']:.2f} locales/km²)."
            ),
            (
                f"PN2 (Familias Culinarias): La familia '{top_f['Familia_Culinaria']}' lidera en número de locales con "
                f"{int(top_f['Restaurantes']):,} ({top_f['Participacion_Locales_Pct']:.2f} %), mientras que "
                f"'{top_trac_f['Familia_Culinaria']}' registra la mayor tracción media por local "
                f"({top_trac_f['Promedio_Resenas']:.2f} reseñas y {top_trac_f['Popularidad_Promedio']:.2f} pts de popularidad)."
            ),
        ]
        if len(pn3) >= 2:
            p_max = pn3.sort_values("Popularidad_Promedio", ascending=False).iloc[0]
            res.append(
                f"PN3 (Precios y Satisfacción): Los segmentos Económico ($) y Moderado ($$) agrupan el "
                f"{pn3[pn3['Rango_Precio'].isin([1, 2])]['Participacion_Locales_Pct'].sum():.2f} % de la oferta, pero el segmento "
                f"'{p_max['Categoria_Precio']}' alcanza la mayor tracción promedio ({p_max['Promedio_Resenas']:.2f} reseñas y "
                f"{p_max['Popularidad_Promedio']:.2f} pts)."
            )
        if len(pn4) >= 1:
            s_top = pn4.iloc[-1]
            res.append(
                f"PN4 (Servicios): Los restaurantes con equipamiento '{s_top['Nivel_Servicios']}' "
                f"({s_top['Participacion_Locales_Pct']:.2f} % de la oferta) logran {s_top['Promedio_Resenas']:.2f} reseñas promedio, "
                f"calificación de {s_top['Calificacion_Promedio']:.2f} ★ y {s_top['Pct_Alta_Reputacion']:.2f} % de alta reputación."
            )
        return res


# Alias de compatibilidad con la nomenclatura del repositorio docente
AnalisisBase = AnalisisRestaurantesNYC
