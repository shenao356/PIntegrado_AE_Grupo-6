"""Dashboard web interactivo de Restaurantes de Nueva York (NYC) con Streamlit + Plotly (AE4).

La clase :class:`DashboardStreamlit` toma el dataset preparado y enriquecido en la Etapa 2 (AE3:
``whatscooking_restaurants_preparado.csv``, con 25.159 restaurantes y 27 variables sin valores nulos) y:

1. Calcula los indicadores clave (KPIs) y las tablas de resultados reutilizando :class:`AnalisisRestaurantesNYC`
   (garantizando que las cifras de la app coincidan exactamente con el notebook y el informe PDF).
2. Define formalmente cada métrica utilizada, su fórmula matemática y su unidad de medida.
3. Construye cada visualización interactiva en Plotly con título, subtítulo de alcance, etiquetas de ejes,
   unidades y paleta de identidad fija por distrito.
4. Redacta dinámicamente la interpretación de los datos, la respuesta a cada pregunta de negocio (PN1 a PN5),
   la decisión estratégica que apoya y sus limitaciones metodológicas (distinguiendo nivel de precios y
   tracción de reseñas frente a ingresos reales o rentabilidad financiera, y evitando atribuir causalidad).
5. Ensambla la aplicación web completa en Streamlit (``render()``) con filtros interactivos en la barra
   lateral, lista para ejecutarse localmente o publicarse en Streamlit Community Cloud desde GitHub.

Uso en Jupyter Notebook::

    dash = DashboardStreamlit.desde_csv("AE4/datos/whatscooking_restaurants_preparado.csv")
    dash.kpis_tabla()
    dash.figura_pn1_oferta_distritos()

Uso en la aplicación web (``src/clases_po/app.py`` o ``AE4/app.py``)::

    DashboardStreamlit.desde_csv(RUTA_DATOS).render()
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

try:  # dentro del paquete clases_po o AE4.src
    from .analisis import (
        ORDEN_BARRIOS,
        ORDEN_FAMILIAS,
        ORDEN_PRECIOS,
        ORDEN_PRECIOS_DECLARADOS,
        ORDEN_REPUTACION,
        ORDEN_SERVICIOS,
        AnalisisRestaurantesNYC,
    )
except ImportError:  # cuando app.py agrega la carpeta al sys.path y lo importa directamente
    from analisis import (  # type: ignore[no-redef]
        ORDEN_BARRIOS,
        ORDEN_FAMILIAS,
        ORDEN_PRECIOS,
        ORDEN_PRECIOS_DECLARADOS,
        ORDEN_REPUTACION,
        ORDEN_SERVICIOS,
        AnalisisRestaurantesNYC,
    )


# ==============================================================================
# Funciones auxiliares de formato numérico (estilo colombiano/español) y escape
# ==============================================================================
def numero(x: float | int, decimales: int = 0) -> str:
    """Formatea números con punto de miles y coma decimal (ej. 25.159 o 172,81)."""
    return f"{x:,.{decimales}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x: float, decimales: int = 1, es_proporcion: bool = False) -> str:
    """Formatea porcentajes (si es_proporcion=True multiplica por 100)."""
    val = x * 100.0 if es_proporcion else x
    return f"{val:.{decimales}f} %".replace(".", ",")


def estrellas(x: float, decimales: int = 2) -> str:
    """Formatea calificaciones en escala de estrellas (ej. 3,53 ★)."""
    return f"{numero(x, decimales)} ★"


def _esc(texto: str) -> str:
    """Streamlit interpreta $...$ como fórmula LaTeX; se escapa el símbolo $ para mostrar ($), ($$), ($$$)."""
    return texto.replace("$", r"\$")


def _acepta_delta_arrow(st_mod) -> bool:
    import inspect

    try:
        return "delta_arrow" in inspect.signature(st_mod.metric).parameters
    except (TypeError, ValueError):
        return False


# Coordenadas oficiales de referencia de los 5 distritos de NYC para el mapa interactivo
CENTROIDES_BARRIOS = {
    "Manhattan": (40.7831, -73.9712),
    "Brooklyn": (40.6782, -73.9442),
    "Queens": (40.7282, -73.7949),
    "Bronx": (40.8448, -73.8648),
    "Staten Island": (40.5795, -74.1502),
}


class DashboardStreamlit:
    """Visualizador interactivo de métricas y gráficos para el Proyecto Integrador (AE4)."""

    # Paleta de identidad visual (un color fijo por distrito, nunca por posición en el ranking)
    PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6", "#e87ba4", "#008300", "#e34948"]
    COLOR_BARRIO = {
        "Manhattan": "#2a78d6",      # Azul corporativo
        "Brooklyn": "#eb6834",       # Naranja terracota
        "Queens": "#1baf7a",         # Verde esmeralda
        "Bronx": "#eda100",          # Ámbar dorado
        "Staten Island": "#6250d6",  # Violeta
    }
    COLOR_PRECIO = {
        "1 - Económico ($)": "#5aa9e6",
        "2 - Moderado ($$)": "#2a78d6",
        "3 - Costoso ($$$)": "#eb6834",
        "4 - Gourmet / Exclusivo ($$$$)": "#b4491f",
        "No Especificado": "#8c8b85",
    }
    COLOR = "#2a78d6"
    ACENTO = "#eb6834"
    VERDE = "#1baf7a"
    TEXTO, TEXTO_2, REJILLA = "#1f1f1e", "#5f5e5a", "#e6e5e0"
    ESCALA = "Blues"
    ESCALA_CALIDA = "YlOrRd"

    NECESIDAD_PROYECTO = (
        "Un grupo de emprendedores e inversionistas del sector gastronómico busca abrir, posicionar o expandir "
        "un restaurante en la ciudad de Nueva York (NYC). Antes de comprometer capital en arriendo, diseño de menú "
        "e infraestructura de servicios, requieren evidencia cuantitativa y descriptiva sobre la distribución geográfica "
        "de la competencia, las especialidades culinarias con mayor tracción, la estructura de precios, el impacto "
        "de los servicios de conveniencia y los nichos territoriales menos saturados."
    )

    PREGUNTA_NEGOCIO = (
        "¿Dónde ubicar un restaurante en Nueva York, con qué especialidad culinaria, en qué rango de precios "
        "y con qué nivel de servicios de conveniencia para lograr la mejor relación entre tracción de reseñas, "
        "reputación digital y saturación competitiva?"
    )

    PREGUNTAS = {
        "PN1": "¿Cómo se distribuye la oferta de restaurantes y el flujo de reseñas entre los cinco distritos de Nueva York, y cuál es su densidad comercial (por km² y por 10.000 habitantes) y reputación promedio?",
        "PN2": "¿Cuáles son las especialidades culinarias y las 8 macro-familias gastronómicas predominantes en Nueva York, y cómo se comparan en calificación, promedio de reseñas y popularidad?",
        "PN3": "¿Cómo se segmenta la oferta gastronómica según las categorías de rango de precio (declarada e imputada) y qué relación guarda el nivel de precios con la satisfacción y el volumen de reseñas?",
        "PN4": "¿Qué proporción de restaurantes ofrece servicios de conveniencia (para llevar, mesas exteriores, hora feliz, mascotas) y cómo varía la popularidad y reputación según el nivel de equipamiento?",
        "PN5": "¿Cómo se cruzan el distrito geográfico y la categoría de precio en densidad de oferta, reseñas y reputación para identificar zonas saturadas frente a nichos de oportunidad?",
    }

    COLUMNAS_REQUERIDAS = [
        "ID_Restaurante",
        "Nombre",
        "Barrio",
        "Tipo_Cocina",
        "Calificacion",
        "Total_Resenas",
        "Mesas_Exteriores",
        "Para_Llevar",
        "Hora_Feliz",
        "Permite_Mascotas",
        "Codigo_Postal",
        "Latitud",
        "Longitud",
        "Cantidad_Platos_Menu",
        "Categoria_Precio_Declarada",
        "Rango_Precio",
        "Categoria_Precio",
        "Puntaje_Popularidad",
        "Indice_Reputacion_Ponderada",
        "Segmento_Reputacion",
        "Nivel_Traccion_Resenas",
        "Total_Servicios",
        "Nivel_Servicios",
        "Familia_Culinaria",
        "Poblacion_Distrito",
        "Superficie_Km2",
        "Vocacion_Comercial",
    ]

    def __init__(
        self,
        restaurantes: pd.DataFrame,
        titulo: str = "Panorama Gastronómico de Nueva York (NYC) · Métricas y Visualización (AE4)",
    ):
        faltan = [c for c in self.COLUMNAS_REQUERIDAS if c not in restaurantes.columns]
        if faltan:
            raise ValueError(f"Al dataset le faltan columnas requeridas de la AE3: {faltan}")
        self.titulo = titulo
        self.R_total = self.tipar(restaurantes)
        self.orden_barrios = [b for b in ORDEN_BARRIOS if b in set(self.R_total["Barrio"].astype(str))]
        self.color_barrio = {
            b: self.COLOR_BARRIO.get(b, self.PALETA[i % len(self.PALETA)])
            for i, b in enumerate(self.orden_barrios)
        }
        self._preparar(self.R_total)

    # ==================================================================
    # Carga, exportación y tipado del dataset preparado
    # ==================================================================
    @classmethod
    def desde_csv(cls, ruta: str | Path, **kwargs) -> "DashboardStreamlit":
        """Carga el CSV preparado y enriquecido en la AE3 y devuelve la instancia del dashboard."""
        return cls(pd.read_csv(ruta, dtype={"ID_Restaurante": str, "Codigo_Postal": str}), **kwargs)

    @staticmethod
    def exportar_datos(origen: str | Path, destino: str | Path) -> Path:
        """Copia el dataset preparado a la carpeta de la aplicación AE4 para garantizar su disponibilidad."""
        d = pd.read_csv(origen, dtype={"ID_Restaurante": str, "Codigo_Postal": str})
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        d.to_csv(destino, index=False, encoding="utf-8")
        print(f"{len(d):,} filas × {len(d.columns)} columnas → {destino} ({destino.stat().st_size / 1e6:.2f} MB)")
        return destino

    @staticmethod
    def tipar(df: pd.DataFrame) -> pd.DataFrame:
        """Restaura los tipos de datos y órdenes categóricos al leer desde CSV."""
        d = df.copy()
        d["ID_Restaurante"] = d["ID_Restaurante"].astype(str)
        d["Codigo_Postal"] = d["Codigo_Postal"].astype(str).str.zfill(5)
        for col_bool in ["Mesas_Exteriores", "Para_Llevar", "Hora_Feliz", "Permite_Mascotas"]:
            if d[col_bool].dtype != bool:
                d[col_bool] = d[col_bool].astype(str).str.lower().isin(["true", "1", "yes", "sí"])
        for col_int in ["Total_Resenas", "Cantidad_Platos_Menu", "Rango_Precio", "Total_Servicios", "Poblacion_Distrito"]:
            d[col_int] = pd.to_numeric(d[col_int], errors="coerce").fillna(0).astype("int64")
        for col_flt in ["Calificacion", "Latitud", "Longitud", "Puntaje_Popularidad", "Indice_Reputacion_Ponderada", "Superficie_Km2"]:
            d[col_flt] = pd.to_numeric(d[col_flt], errors="coerce").astype("float64")

        d["Barrio"] = pd.Categorical(
            d["Barrio"].astype(str),
            categories=[b for b in ORDEN_BARRIOS if b in set(d["Barrio"].astype(str))],
            ordered=True,
        )
        d["Categoria_Precio"] = pd.Categorical(
            d["Categoria_Precio"].astype(str),
            categories=[p for p in ORDEN_PRECIOS if p in set(d["Categoria_Precio"].astype(str))],
            ordered=True,
        )
        d["Categoria_Precio_Declarada"] = pd.Categorical(
            d["Categoria_Precio_Declarada"].astype(str),
            categories=[p for p in ORDEN_PRECIOS_DECLARADOS if p in set(d["Categoria_Precio_Declarada"].astype(str))],
            ordered=True,
        )
        d["Nivel_Servicios"] = pd.Categorical(
            d["Nivel_Servicios"].astype(str),
            categories=[s for s in ORDEN_SERVICIOS if s in set(d["Nivel_Servicios"].astype(str))],
            ordered=True,
        )
        d["Segmento_Reputacion"] = pd.Categorical(
            d["Segmento_Reputacion"].astype(str),
            categories=[r for r in ORDEN_REPUTACION if r in set(d["Segmento_Reputacion"].astype(str))],
            ordered=True,
        )
        return d

    def _preparar(self, R: pd.DataFrame) -> None:
        """Inicializa el motor de análisis sobre el subconjunto de datos activo."""
        self.R = R
        self.A = AnalisisRestaurantesNYC(R, df_total=self.R_total) if len(R) else None

    def filtrar(
        self,
        barrios: list[str] | None = None,
        familias: list[str] | None = None,
        precios: list[str] | None = None,
        servicios: list[str] | None = None,
        calificacion_rango: tuple[float, float] | None = None,
        busqueda: str | None = None,
    ) -> "DashboardStreamlit":
        """Devuelve una nueva instancia del dashboard con los filtros aplicados conservando los colores."""
        R = self.R_total
        if barrios:
            R = R[R["Barrio"].astype(str).isin(barrios)]
        if familias:
            R = R[R["Familia_Culinaria"].astype(str).isin(familias)]
        if precios:
            R = R[R["Categoria_Precio"].astype(str).isin(precios)]
        if servicios:
            R = R[R["Nivel_Servicios"].astype(str).isin(servicios)]
        if calificacion_rango and len(calificacion_rango) == 2:
            c_min, c_max = float(calificacion_rango[0]), float(calificacion_rango[1])
            R = R[(R["Calificacion"] >= c_min) & (R["Calificacion"] <= c_max)]
        if busqueda and busqueda.strip():
            q = busqueda.strip().lower()
            mask = (
                R["Nombre"].astype(str).str.lower().str.contains(q, na=False)
                | R["Tipo_Cocina"].astype(str).str.lower().str.contains(q, na=False)
                | R["Codigo_Postal"].astype(str).str.lower().str.contains(q, na=False)
            )
            R = R[mask]

        nuevo = object.__new__(DashboardStreamlit)
        nuevo.__dict__.update({k: v for k, v in self.__dict__.items() if k not in ("R", "A")})
        nuevo.R_total = self.R_total
        nuevo._preparar(R.copy())
        return nuevo

    @property
    def vacio(self) -> bool:
        return self.A is None or self.R.empty

    def alcance_texto(self) -> str:
        """Resumen textual del corte activo de datos (unidad de análisis, distritos y cocinas)."""
        if self.vacio:
            return "Sin registros seleccionados"
        n_barrios = self.R["Barrio"].nunique()
        n_cocinas = self.R["Tipo_Cocina"].nunique()
        return (
            f"Corte transversal NYC (Censo 2024 / Hugging Face) · "
            f"{numero(len(self.R))} restaurantes ({pct(len(self.R) / len(self.R_total), 1, True)} del total) · "
            f"{n_barrios} distrito(s) · {n_cocinas} especialidades culinarias"
        )

    # ==================================================================
    # Indicadores Clave (KPIs)
    # ==================================================================
    def kpis(self) -> dict[str, float]:
        return self.A.kpis() if self.A is not None else {}

    def kpis_tabla(self) -> pd.DataFrame:
        k = self.kpis()
        if not k:
            return pd.DataFrame()
        fmt = {
            "Restaurantes analizados (locales)": numero(k["Restaurantes"]),
            "% de la base total de NYC": pct(k["% del total NYC"], 1, True),
            "Reseñas acumuladas (opiniones)": numero(k["Reseñas acumuladas"]),
            "Promedio de reseñas por local": f"{numero(k['Promedio reseñas'], 2)} reseñas",
            "Calificación promedio simple": estrellas(k["Calificación promedio"], 2),
            "Índice de reputación bayesiana": estrellas(k["Reputación ponderada"], 2),
            "Puntaje de popularidad promedio": f"{numero(k['Popularidad promedio'], 2)} pts",
            "Tasa de alta reputación (≥ 4,0 ★)": pct(k["% Alta reputación"], 2, True),
            "Densidad comercial superficial": f"{numero(k['Densidad km2'], 2)} locales/km²",
            "Densidad comercial demográfica": f"{numero(k['Densidad 10k hab'], 2)} locales/10k hab.",
        }
        return pd.DataFrame({"Indicador (KPI)": list(fmt.keys()), "Valor Calculado": list(fmt.values())})

    # ==================================================================
    # Respuestas dinámicas a las 5 Preguntas de Negocio (Rúbrica AE4)
    # ==================================================================
    def respuestas(self) -> list[dict[str, str]]:
        """Genera para cada pregunta: métrica/fórmula/unidad, gráfico, respuesta con cifras, decisión y limitación."""
        if self.vacio or self.A is None:
            return []

        A = self.A
        pn1 = A.pn1_distribucion_distritos()
        pn2_fam = A.pn2_familias_culinarias()
        pn2_esp = A.pn2_especialidades_culinarias(top_n=15)
        pn3_dec = A.pn3_segmentos_precio_declarado()
        pn3_imp = A.pn3_segmentos_precio_imputado()
        pn4_srv = A.pn4_servicios_conveniencia()
        pn5_mat = A.pn5_matriz_distrito_precio()

        # Datos dinámicos PN1
        b_top = pn1.iloc[0]
        b_ult = pn1.iloc[-1]
        b_pop = pn1.sort_values("Popularidad_Promedio", ascending=False).iloc[0]
        b_rep = pn1.sort_values("Pct_Alta_Reputacion", ascending=False).iloc[0]

        # Datos dinámicos PN2
        f_top = pn2_fam.iloc[0]
        f_trac = pn2_fam.sort_values("Popularidad_Promedio", ascending=False).iloc[0]
        c_top = pn2_esp.iloc[0]
        c_trac = pn2_esp.sort_values("Popularidad_Promedio", ascending=False).iloc[0]

        # Datos dinámicos PN3
        pct_accesible = pn3_imp[pn3_imp["Rango_Precio"].isin([1, 2])]["Participacion_Locales_Pct"].sum()
        p_eco = pn3_imp.iloc[0]
        p_max_trac = pn3_imp.sort_values("Promedio_Resenas", ascending=False).iloc[0]
        fila_no_esp = pn3_dec[pn3_dec["Categoria_Precio_Declarada"] == "No Especificado"]
        txt_no_esp = ""
        if not fila_no_esp.empty:
            ne = fila_no_esp.iloc[0]
            txt_no_esp = (
                f" El segmento sin precio declarado ({numero(ne['Restaurantes'])} locales; {pct(ne['Participacion_Locales_Pct'], 2)}) "
                f"presenta pocas reseñas ({numero(ne['Promedio_Resenas'], 2)} en promedio) y una calificación simple inflada "
                f"({estrellas(ne['Calificacion_Promedio'])}), que el suavizado bayesiano corrige a {estrellas(ne['Reputacion_Ponderada'])}."
            )

        # Datos dinámicos PN4
        s_bas = pn4_srv.iloc[0]
        s_top = pn4_srv.iloc[-1]
        factor_res = s_top["Promedio_Resenas"] / max(s_bas["Promedio_Resenas"], 1.0)

        # Datos dinámicos PN5
        sub_costoso = pn5_mat[pn5_mat["Rango_Precio"] == 3].sort_values("Promedio_Resenas", ascending=False)
        nicho_txt = ""
        if not sub_costoso.empty:
            nc = sub_costoso.iloc[0]
            nicho_txt = (
                f"En el segmento Costoso ($$$), {nc['Barrio']} lidera la tracción con {numero(nc['Promedio_Resenas'], 2)} "
                f"reseñas/local y {numero(nc['Popularidad_Promedio'], 2)} pts de popularidad en solo {numero(nc['Restaurantes'])} locales."
            )
        else:
            nc = pn5_mat.sort_values("Popularidad_Promedio", ascending=False).iloc[0]
            nicho_txt = (
                f"La combinación de mayor tracción es {nc['Barrio']} en {nc['Categoria_Precio']} con "
                f"{numero(nc['Promedio_Resenas'], 2)} reseñas/local."
            )

        return [
            {
                "id": "PN1",
                "titulo": "Concentración geográfica y densidad demográfica por distrito",
                "pregunta": self.PREGUNTAS["PN1"],
                "metrica": (
                    "Oferta (% locales = N_i / N_total × 100, en % y establecimientos), "
                    "Densidad superficial (N_i / Superficie_Km2, en locales/km²), "
                    "Densidad demográfica (N_i / Poblacion_Distrito × 10.000, en locales/10k hab.) y "
                    "Reputación ponderada bayesiana (en estrellas ★ de 1,0 a 5,0)."
                ),
                "visual": (
                    "Gráfico de barras horizontales ordenadas con color fijo de identidad por distrito y gráfico "
                    "comparativo de densidad física (locales/km²) frente a densidad demográfica (locales/10k hab.)."
                ),
                "respuesta": (
                    f"{b_top['Barrio']} concentra la mayor oferta con {numero(b_top['Restaurantes'])} restaurantes "
                    f"({pct(b_top['Participacion_Locales_Pct'], 2)}) y {numero(b_top['Resenas_Acumuladas'])} reseñas "
                    f"({pct(b_top['Participacion_Resenas_Pct'], 2)}), alcanzando una saturación de "
                    f"{numero(b_top['Locales_por_Km2'], 2)} locales/km² y {numero(b_top['Locales_por_10k_Hab'], 2)} locales/10k hab. "
                    f"(frente a {b_ult['Barrio']} con {numero(b_ult['Restaurantes'])} locales y {numero(b_ult['Locales_por_Km2'], 2)} locales/km²). "
                    f"Sin embargo, la tracción media por local es muy pareja (~95–97 reseñas), destacando {b_pop['Barrio']} en "
                    f"popularidad promedio ({numero(b_pop['Popularidad_Promedio'], 2)} pts) y {b_rep['Barrio']} en alta reputación ({pct(b_rep['Pct_Alta_Reputacion'], 2)})."
                ),
                "decision": (
                    f"Descentralizar la apertura hacia distritos con alta demanda por local pero menor saturación por km² "
                    f"(como Brooklyn y Queens, con 5 a 8 veces menos densidad superficial que {b_top['Barrio']}), donde "
                    f"el flujo de reseñas por establecimiento iguala o supera al centro financiero."
                ),
                "limitacion": (
                    "La densidad mide establecimientos registrados frente a población residente censal (U.S. Census Bureau, 2024); "
                    "no captura la población flotante diaria (turistas y oficinas en Manhattan) ni mide ventas en dólares o costo del metro cuadrado de arriendo."
                ),
            },
            {
                "id": "PN2",
                "titulo": "Especialidades y macro-familias culinarias predominantes",
                "pregunta": self.PREGUNTAS["PN2"],
                "metrica": (
                    "Participación de oferta por cocina/familia (% de locales), Promedio de reseñas por local "
                    "(mean(Total_Resenas), en opiniones/local) y Puntaje de Popularidad (Calificacion × Total_Resenas, en puntos)."
                ),
                "visual": (
                    "Barras horizontales de volumen por las 8 macro-familias, gráfico comparativo de tracción promedio "
                    "(reseñas y popularidad) y ranking Top 15 de especialidades individuales."
                ),
                "respuesta": (
                    f"En volumen de oferta lidera la familia '{f_top['Familia_Culinaria']}' con {numero(f_top['Restaurantes'])} locales "
                    f"({pct(f_top['Participacion_Locales_Pct'], 2)}), encabezada por la cocina '{c_top['Tipo_Cocina']}' "
                    f"({numero(c_top['Restaurantes'])} locales; {pct(c_top['Participacion_Locales_Pct'], 2)}). "
                    f"No obstante, en tracción promedio por establecimiento lideran '{f_trac['Familia_Culinaria']}' "
                    f"({numero(f_trac['Promedio_Resenas'], 2)} reseñas y {numero(f_trac['Popularidad_Promedio'], 2)} pts) y "
                    f"dentro del Top 15 destaca '{c_trac['Tipo_Cocina']}' ({numero(c_trac['Promedio_Resenas'], 2)} reseñas y "
                    f"{numero(c_trac['Popularidad_Promedio'], 2)} pts)."
                ),
                "decision": (
                    "Evitar competir con propuestas genéricas en la categoría más saturada ('American' tradicional) y apostar "
                    "por conceptos gastronómicos con identidad cultural diferenciada (cocina hispana/latina, mediterránea/española "
                    "o cafeterías de especialidad), que generan mayor volumen de reseñas por local con menor saturación."
                ),
                "limitacion": (
                    "Un mayor volumen de reseñas y popularidad refleja visibilidad e interacción de los usuarios en la plataforma, "
                    "pero no equivale directamente a mayores ingresos netos ni a mayor margen de rentabilidad (que dependen del costo de insumos y rotación de mesas)."
                ),
            },
            {
                "id": "PN3",
                "titulo": "Segmentos de rango de precio, satisfacción y popularidad",
                "pregunta": self.PREGUNTAS["PN3"],
                "metrica": (
                    "Distribución porcentual por nivel de precio ($ a $$$$ y No Especificado, en %), "
                    "Promedio y mediana de reseñas (opiniones/local) e Índice de Reputación Ponderada Bayesiana (en ★)."
                ),
                "visual": (
                    "Columnas agrupadas en orden ordinal natural ($ → $$$$) comparando precio declarado vs. imputado, "
                    "curva/barras de gradiente de tracción y contraste entre calificación simple y reputación bayesiana."
                ),
                "respuesta": (
                    f"Los segmentos Económico ($) y Moderado ($$) concentran el {pct(pct_accesible, 2)} de la oferta total. "
                    f"Al subir desde '{p_eco['Categoria_Precio']}' hasta '{p_max_trac['Categoria_Precio']}', el promedio de reseñas "
                    f"pasa de {numero(p_eco['Promedio_Resenas'], 2)} a {numero(p_max_trac['Promedio_Resenas'], 2)} opiniones/local "
                    f"y la popularidad sube de {numero(p_eco['Popularidad_Promedio'], 2)} a {numero(p_max_trac['Popularidad_Promedio'], 2)} pts."
                    f"{txt_no_esp}"
                ),
                "decision": (
                    "Posicionar el modelo de negocio en el segmento Moderado ($$) o Costoso de entrada ($$$), donde se concentra "
                    "la mayor tracción de reseñas y mejor reputación ponderada, evitando la guerra de precios del segmento Económico ($)."
                ),
                "limitacion": (
                    "La categoría de precio ($ a $$$$) indica el nivel tarifario percibido de la carta y NO los ingresos totales ni la "
                    "rentabilidad financiera del restaurante. Además, el 9,52 % sin precio fue imputado con la mediana de (Tipo_Cocina, Barrio) para análisis multivariado."
                ),
            },
            {
                "id": "PN4",
                "titulo": "Disponibilidad de servicios de conveniencia y valor agregado",
                "pregunta": self.PREGUNTAS["PN4"],
                "metrica": (
                    "Tasa de adopción por servicio (% de locales con True) y desempeño por Nivel de Equipamiento "
                    "(Total_Servicios de 1 a 4: promedio/mediana de reseñas, popularidad en pts y % de alta reputación)."
                ),
                "visual": (
                    "Barras horizontales de adopción de los 4 servicios individuales y gráficos de columnas por "
                    "Nivel de Equipamiento (1. Básico, 2. Intermedio, 3. Completo/Multipropósito)."
                ),
                "respuesta": (
                    f"Comida para llevar (100,0 %) y mesas exteriores ({pct(self.R['Mesas_Exteriores'].mean() * 100, 1)}) son estándares "
                    f"del mercado, mientras que hora feliz ({pct(self.R['Hora_Feliz'].mean() * 100, 1)}) y admisión de mascotas "
                    f"({pct(self.R['Permite_Mascotas'].mean() * 100, 1)}) actúan como diferenciadores. Los locales con equipamiento "
                    f"'{s_top['Nivel_Servicios']}' ({pct(s_top['Participacion_Locales_Pct'], 2)} del total) alcanzan "
                    f"{numero(s_top['Promedio_Resenas'], 2)} reseñas promedio ({numero(factor_res, 1)} veces más que el nivel Básico con "
                    f"{numero(s_bas['Promedio_Resenas'], 2)}), calificación de {estrellas(s_top['Calificacion_Promedio'])} y "
                    f"{pct(s_top['Pct_Alta_Reputacion'], 2)} de alta reputación."
                ),
                "decision": (
                    "Diseñar el establecimiento bajo un formato multipropósito (3 a 4 servicios activos: para llevar + terraza exterior "
                    "+ franja de happy hour + política pet-friendly en terraza) para maximizar ocasiones de consumo y visibilidad digital."
                ),
                "limitacion": (
                    "La fuerte diferencia en reseñas y calificación según el número de servicios es una asociación observacional y NO "
                    "demuestra causalidad automática: habilitar terraza o happy hour implica costos de licencias, personal e infraestructura que deben evaluarse financieramente."
                ),
            },
            {
                "id": "PN5",
                "titulo": "Cruce estratégico Distrito × Categoría de Precio y Mapa de NYC",
                "pregunta": self.PREGUNTAS["PN5"],
                "metrica": (
                    "Matriz bivariada Distrito × Precio: Participación intra-distrito (% locales), Promedio de reseñas "
                    "(opiniones/local), Popularidad promedio (pts) y Georreferenciación (Latitud, Longitud en NYC)."
                ),
                "visual": (
                    "Mapas de calor (Heatmaps) de oferta y tracción en las 20 celdas (5 distritos × 4 niveles de precio) "
                    "y mapa geográfico interactivo (Scattermap) de Nueva York."
                ),
                "respuesta": (
                    f"En todos los distritos la estructura interna se concentra en $ (~41–43 %) y $$ (~52–55 %), mientras que "
                    f"$$$ (~3,4–3,7 %) y $$$$ (~0,4–0,7 %) son nichos selectos. {nicho_txt} Asimismo, Queens y Staten Island "
                    f"en el segmento Moderado ($$) superan las 113–120 reseñas promedio con calificaciones de 3,61 ★ a 3,64 ★."
                ),
                "decision": (
                    "Priorizar la apertura de un concepto Moderado-Alto ($$ o $$$) en corredores gastronómicos de Brooklyn o Queens, "
                    "aprovechando su alta tracción por restaurante y menor saturación competidora frente a Manhattan."
                ),
                "limitacion": (
                    "El análisis espacial identifica vacíos de oferta y alta tracción a nivel de distrito y código postal, pero la "
                    "selección final del local requiere un estudio micro-inmobiliario de tráfico peatonal, zonificación y flujo de caja proyectado."
                ),
            },
        ]

    # ==================================================================
    # Estilo común de las figuras Plotly (Rúbrica AE4: título, ejes, unidades)
    # ==================================================================
    @staticmethod
    def _etiqueta_precio_corta(c: str) -> str:
        mapa = {
            "1 - Económico ($)": "1. Económico<br>($)",
            "2 - Moderado ($$)": "2. Moderado<br>($$)",
            "3 - Costoso ($$$)": "3. Costoso<br>($$$)",
            "4 - Gourmet / Exclusivo ($$$$)": "4. Gourmet<br>($$$$)",
            "4 - Lujo ($$$$)": "4. Gourmet<br>($$$$)",
            "No Especificado": "Sin Precio<br>Declarado",
        }
        return mapa.get(str(c), str(c))

    @staticmethod
    def _etiqueta_servicio_corta(s: str) -> str:
        mapa = {
            "1. Básico (1 servicio)": "1. Básico<br>(1 servicio)",
            "2. Intermedio (2 servicios)": "2. Intermedio<br>(2 servicios)",
            "3. Completo / Multipropósito (3-4 servicios)": "3. Completo<br>(3–4 servicios)",
        }
        return mapa.get(str(s), str(s))

    def _estilo(
        self,
        fig: go.Figure,
        titulo: str = "",
        subtitulo: str = "",
        eje_x: str | None = None,
        eje_y: str | None = None,
        alto: int = 430,
        leyenda: bool = False,
        margen_izq: int = 65,
        margen_der: int = 45,
    ) -> go.Figure:
        if subtitulo:
            texto_titulo = (
                f"<b>{titulo}</b>"
                f"<br><span style='font-size:11px;color:{self.TEXTO_2};font-weight:normal'>{subtitulo}</span>"
            )
        else:
            texto_titulo = f"<b>{titulo}</b>"

        # Margen superior amplio: título/subtítulo arriba (y=0.96) y leyenda en su propia banda (y=1.02 del área de trazado)
        if subtitulo and leyenda:
            top_m = 126
        elif subtitulo:
            top_m = 82
        elif leyenda:
            top_m = 90
        else:
            top_m = 56

        bot_m = 68 if eje_x else 38

        fig.update_layout(
            title={
                "text": texto_titulo,
                "x": 0.0,
                "xanchor": "left",
                "y": 0.96,
                "yanchor": "top",
                "font": {"size": 13, "color": self.TEXTO},
            },
            height=alto,
            margin={
                "l": margen_izq,
                "r": margen_der,
                "t": top_m,
                "b": bot_m,
            },
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Segoe UI, sans-serif", "size": 11.5, "color": self.TEXTO_2},
            separators=",.",
            showlegend=leyenda,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "left",
                "x": 0.0,
                "title": None,
                "font": {"size": 11.5, "color": self.TEXTO},
                "bgcolor": "rgba(255,255,255,0.85)",
            },
            hoverlabel={"bgcolor": "white", "font_size": 12},
        )
        fig.update_xaxes(
            showgrid=False,
            linecolor=self.REJILLA,
            ticks="",
            title_text=eje_x,
            title_font={"size": 11.5, "color": self.TEXTO_2},
            title_standoff=12,
            automargin=True,
        )
        fig.update_yaxes(
            gridcolor=self.REJILLA,
            zeroline=False,
            linecolor=self.REJILLA,
            title_text=eje_y,
            title_font={"size": 11.5, "color": self.TEXTO_2},
            title_standoff=12,
            automargin=True,
        )
        return fig

    # ==================================================================
    # Figuras de Pregunta de Negocio 1 (PN1): Distritos y Densidad
    # ==================================================================
    def figura_pn1_oferta_distritos(self) -> go.Figure:
        """PN1-A: Barras horizontales ordenadas de oferta de restaurantes y % por distrito."""
        d = self.A.pn1_distribucion_distritos().sort_values("Restaurantes", ascending=True)
        d["etiqueta"] = [
            f"{numero(r)} locales ({pct(p, 1)})"
            for r, p in zip(d["Restaurantes"], d["Participacion_Locales_Pct"])
        ]
        colores = [self.color_barrio.get(b, self.COLOR) for b in d["Barrio"]]
        fig = go.Figure(
            go.Bar(
                x=d["Restaurantes"],
                y=d["Barrio"],
                orientation="h",
                text=d["etiqueta"],
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                width=0.62,
                marker={"color": colores, "cornerradius": 5},
                customdata=np.stack(
                    [
                        d["Participacion_Locales_Pct"],
                        d["Resenas_Acumuladas"],
                        d["Promedio_Resenas"],
                        d["Calificacion_Promedio"],
                        d["Reputacion_Ponderada"],
                        d["Vocacion_Comercial"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Restaurantes: %{x:,.0f} locales (%{customdata[0]:.2f} %)<br>"
                    "Reseñas acumuladas: %{customdata[1]:,.0f} opiniones<br>"
                    "Promedio reseñas/local: %{customdata[2]:.2f}<br>"
                    "Calificación media: %{customdata[3]:.2f} ★ (Bayesiana: %{customdata[4]:.2f} ★)<br>"
                    "Vocación: %{customdata[5]}<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(range=[0, d["Restaurantes"].max() * 1.35], showgrid=True, gridcolor=self.REJILLA)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo="PN1 · Oferta de restaurantes y participación (%) por distrito",
            subtitulo="Unidad: establecimientos activos y % sobre el total · Color fijo por distrito",
            eje_x="Número de restaurantes (establecimientos)",
            eje_y=None,
            alto=68 * len(d) + 135,
            margen_izq=115,
            margen_der=55,
        )

    def figura_pn1_densidad_territorial(self) -> go.Figure:
        """PN1-B: Comparación de densidad física (locales/km²) y demográfica (locales/10.000 hab.)."""
        d = self.A.pn1_distribucion_distritos().sort_values("Locales_por_Km2", ascending=True)
        fig = go.Figure([
            go.Bar(
                name="Densidad física (locales / km²)",
                x=d["Locales_por_Km2"],
                y=d["Barrio"],
                orientation="h",
                marker={"color": self.COLOR, "cornerradius": 4},
                text=[f"{numero(v, 1)} /km²" for v in d["Locales_por_Km2"]],
                textposition="outside",
                textfont={"size": 11},
                cliponaxis=False,
                customdata=np.stack([d["Superficie_Km2"], d["Restaurantes"]], axis=-1),
                hovertemplate=(
                    "<b>%{y}</b><br>Densidad superficial: %{x:.2f} locales/km²<br>"
                    "Superficie: %{customdata[0]:.1f} km² · Locales: %{customdata[1]:,.0f}<extra></extra>"
                ),
            ),
            go.Bar(
                name="Densidad demográfica (locales / 10k hab.)",
                x=d["Locales_por_10k_Hab"],
                y=d["Barrio"],
                orientation="h",
                marker={"color": self.ACENTO, "cornerradius": 4},
                text=[f"{numero(v, 1)} /10k hab." for v in d["Locales_por_10k_Hab"]],
                textposition="outside",
                textfont={"size": 11},
                cliponaxis=False,
                customdata=np.stack([d["Poblacion_Distrito"], d["Restaurantes"]], axis=-1),
                hovertemplate=(
                    "<b>%{y}</b><br>Densidad demográfica: %{x:.2f} locales/10k hab.<br>"
                    "Población Censo NYC: %{customdata[0]:,.0f} hab. · Locales: %{customdata[1]:,.0f}<extra></extra>"
                ),
            ),
        ])
        fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.14)
        max_x = max(d["Locales_por_Km2"].max(), d["Locales_por_10k_Hab"].max())
        fig.update_xaxes(range=[0, max_x * 1.35], showgrid=True, gridcolor=self.REJILLA)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo="PN1 · Densidad física (locales/km²) vs. demográfica (locales/10k hab.)",
            subtitulo="Unidad: restaurantes por km² y por cada 10.000 habitantes (Censo NYC 2024)",
            eje_x="Tasa de densidad comercial",
            eje_y=None,
            alto=74 * len(d) + 150,
            leyenda=True,
            margen_izq=115,
            margen_der=55,
        )

    def figura_pn1_traccion_distritos(self) -> go.Figure:
        """PN1-C: Popularidad promedio y % de alta reputación por distrito."""
        d = self.A.pn1_distribucion_distritos()
        colores = [self.color_barrio.get(b, self.COLOR) for b in d["Barrio"]]
        fig = go.Figure(
            go.Bar(
                x=d["Barrio"],
                y=d["Popularidad_Promedio"],
                width=0.50,
                marker={"color": colores, "cornerradius": 5},
                text=[
                    f"<b>{numero(pop, 1)} pts</b><br>({pct(ar, 1)} ≥4★)"
                    for pop, ar in zip(d["Popularidad_Promedio"], d["Pct_Alta_Reputacion"])
                ],
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                customdata=np.stack(
                    [d["Promedio_Resenas"], d["Calificacion_Promedio"], d["Reputacion_Ponderada"], d["Pct_Alta_Reputacion"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Popularidad promedio: %{y:.2f} pts<br>"
                    "Promedio de reseñas: %{customdata[0]:.2f} opiniones/local<br>"
                    "Calificación media: %{customdata[1]:.2f} ★ (Bayesiana: %{customdata[2]:.2f} ★)<br>"
                    "Locales con alta reputación (≥4,0 ★): %{customdata[3]:.2f} %<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(range=[0, d["Popularidad_Promedio"].max() * 1.34])
        return self._estilo(
            fig,
            titulo="PN1 · Popularidad promedio y % de alta reputación por distrito",
            subtitulo="Unidad: puntos de popularidad (pts) · Entre paréntesis: % de locales con calificación ≥ 4,0 ★",
            eje_x="Distrito de Nueva York (Borough)",
            eje_y="Popularidad promedio (pts)",
            alto=420,
        )

    # ==================================================================
    # Figuras de Pregunta de Negocio 2 (PN2): Familias y Especialidades
    # ==================================================================
    def figura_pn2_familias_oferta(self) -> go.Figure:
        """PN2-A: Oferta de restaurantes por las 8 macro-familias culinarias."""
        d = self.A.pn2_familias_culinarias().sort_values("Restaurantes", ascending=True)
        d["etiqueta"] = [
            f"{numero(r)} locales ({pct(p, 1)})"
            for r, p in zip(d["Restaurantes"], d["Participacion_Locales_Pct"])
        ]
        fig = go.Figure(
            go.Bar(
                x=d["Restaurantes"],
                y=d["Familia_Culinaria"],
                orientation="h",
                text=d["etiqueta"],
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                width=0.64,
                marker={"color": self.COLOR, "cornerradius": 4},
                customdata=np.stack(
                    [
                        d["Participacion_Locales_Pct"],
                        d["Promedio_Resenas"],
                        d["Popularidad_Promedio"],
                        d["Calificacion_Promedio"],
                        d["Reputacion_Ponderada"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Restaurantes: %{x:,.0f} locales (%{customdata[0]:.2f} %)<br>"
                    "Promedio reseñas: %{customdata[1]:.2f} opiniones/local<br>"
                    "Popularidad promedio: %{customdata[2]:.2f} pts<br>"
                    "Calificación: %{customdata[3]:.2f} ★ (Bayesiana: %{customdata[4]:.2f} ★)<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(range=[0, d["Restaurantes"].max() * 1.35], showgrid=True, gridcolor=self.REJILLA, tickangle=0)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo="PN2 · Oferta de restaurantes por macro-familia gastronómica (8 familias)",
            subtitulo="Unidad: cantidad de establecimientos y participación (%) sobre el total",
            eje_x="Número de restaurantes (establecimientos)",
            eje_y=None,
            alto=460,
            margen_izq=225,
            margen_der=60,
        )

    def figura_pn2_familias_traccion(self) -> go.Figure:
        """PN2-B: Tracción promedio (reseñas y popularidad) por macro-familia culinaria."""
        d = self.A.pn2_familias_culinarias().sort_values("Popularidad_Promedio", ascending=True)
        top2 = set(d.tail(2)["Familia_Culinaria"])
        colores = [self.ACENTO if f in top2 else "#7eaee8" for f in d["Familia_Culinaria"]]
        fig = go.Figure(
            go.Bar(
                x=d["Popularidad_Promedio"],
                y=d["Familia_Culinaria"],
                orientation="h",
                text=[
                    f"{numero(pop, 1)} pts ({numero(res, 1)} res./local)"
                    for pop, res in zip(d["Popularidad_Promedio"], d["Promedio_Resenas"])
                ],
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                width=0.64,
                marker={"color": colores, "cornerradius": 4},
                customdata=np.stack(
                    [d["Promedio_Resenas"], d["Calificacion_Promedio"], d["Pct_Alta_Reputacion"], d["Restaurantes"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Popularidad promedio: %{x:.2f} pts<br>"
                    "Promedio de reseñas: %{customdata[0]:.2f} opiniones/local<br>"
                    "Calificación promedio: %{customdata[1]:.2f} ★ (%{customdata[2]:.1f} % ≥4★)<br>"
                    "Total locales en familia: %{customdata[3]:,.0f}<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(range=[0, d["Popularidad_Promedio"].max() * 1.38], showgrid=True, gridcolor=self.REJILLA, tickangle=0)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo="PN2 · Tracción promedio por macro-familia (naranja = líderes en demanda)",
            subtitulo="Unidad: puntos de popularidad (Calificación × Reseñas) y promedio de reseñas/local",
            eje_x="Popularidad promedio por restaurante (pts)",
            eje_y=None,
            alto=460,
            margen_izq=225,
            margen_der=65,
        )

    def figura_pn2_top_cocinas(self, n: int = 15, metrica: str = "Restaurantes") -> go.Figure:
        """PN2-C: Ranking de las Top N especialidades culinarias según la métrica seleccionada."""
        base = self.A.pn2_especialidades_culinarias(top_n=n)
        cfg_metrica = {
            "Restaurantes": (
                "Número de restaurantes (establecimientos)",
                lambda r: f"{numero(r['Restaurantes'])} ({pct(r['Participacion_Locales_Pct'], 1)})",
                self.COLOR,
            ),
            "Popularidad_Promedio": (
                "Popularidad promedio por local (pts)",
                lambda r: f"{numero(r['Popularidad_Promedio'], 1)} pts ({numero(r['Promedio_Resenas'], 1)} res.)",
                self.ACENTO,
            ),
            "Promedio_Resenas": (
                "Promedio de reseñas por local (opiniones)",
                lambda r: f"{numero(r['Promedio_Resenas'], 1)} res. ({estrellas(r['Calificacion_Promedio'])})",
                self.VERDE,
            ),
        }
        etiqueta_eje, fn_txt, color_barra = cfg_metrica.get(metrica, cfg_metrica["Restaurantes"])
        d = base.sort_values(metrica, ascending=True)
        textos = [fn_txt(fila) for _, fila in d.iterrows()]

        fig = go.Figure(
            go.Bar(
                x=d[metrica],
                y=d["Tipo_Cocina"],
                orientation="h",
                text=textos,
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                width=0.66,
                marker={"color": color_barra, "cornerradius": 4},
                customdata=np.stack(
                    [
                        d["Familia_Culinaria"],
                        d["Restaurantes"],
                        d["Participacion_Locales_Pct"],
                        d["Promedio_Resenas"],
                        d["Popularidad_Promedio"],
                        d["Calificacion_Promedio"],
                        d["Reputacion_Ponderada"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{y}</b> (%{customdata[0]})<br>"
                    "Restaurantes: %{customdata[1]:,.0f} (%{customdata[2]:.2f} %)<br>"
                    "Promedio reseñas: %{customdata[3]:.2f} opiniones/local<br>"
                    "Popularidad promedio: %{customdata[4]:.2f} pts<br>"
                    "Calificación: %{customdata[5]:.2f} ★ (Bayesiana: %{customdata[6]:.2f} ★)<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(range=[0, d[metrica].max() * 1.35], showgrid=True, gridcolor=self.REJILLA, tickangle=0)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo=f"PN2 · Top {len(d)} especialidades culinarias ordenadas por {metrica.replace('_', ' ')}",
            subtitulo=f"Unidad: {etiqueta_eje} · Base homologada: 84 especialidades en NYC",
            eje_x=etiqueta_eje,
            eje_y=None,
            alto=36 * len(d) + 135,
            margen_izq=185,
            margen_der=60,
        )

    # ==================================================================
    # Figuras de Pregunta de Negocio 3 (PN3): Precios y Satisfacción
    # ==================================================================
    def figura_pn3_declarado_vs_imputado(self) -> go.Figure:
        """PN3-A: Comparación de la distribución declarada vs. imputada de rango de precios."""
        dec = self.A.pn3_segmentos_precio_declarado().set_index("Categoria_Precio_Declarada")
        imp = self.A.pn3_segmentos_precio_imputado().set_index("Categoria_Precio")
        categorias = [c for c in ORDEN_PRECIOS_DECLARADOS if c in dec.index or c in imp.index]
        etiquetas_x = [self._etiqueta_precio_corta(c) for c in categorias]

        y_dec = [float(dec.loc[c, "Participacion_Locales_Pct"]) if c in dec.index else 0.0 for c in categorias]
        n_dec = [int(dec.loc[c, "Restaurantes"]) if c in dec.index else 0 for c in categorias]
        y_imp = [float(imp.loc[c, "Participacion_Locales_Pct"]) if c in imp.index else 0.0 for c in categorias]
        n_imp = [int(imp.loc[c, "Restaurantes"]) if c in imp.index else 0 for c in categorias]

        fig = go.Figure([
            go.Bar(
                name="Declarado en origen",
                x=etiquetas_x,
                y=y_dec,
                marker={"color": "#8ebcf0", "cornerradius": 4},
                text=[f"{pct(v, 1)}" if n > 0 else "—" for v, n in zip(y_dec, n_dec)],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                customdata=n_dec,
                hovertemplate="<b>%{x}</b> (Declarado)<br>Participación: %{y:.2f} %<br>Locales: %{customdata:,.0f}<extra></extra>",
            ),
            go.Bar(
                name="Imputado final (Cocina × Distrito)",
                x=etiquetas_x,
                y=y_imp,
                marker={"color": self.COLOR, "cornerradius": 4},
                text=[f"{pct(v, 1)}" if n > 0 else "0,0 %" for v, n in zip(y_imp, n_imp)],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                customdata=n_imp,
                hovertemplate="<b>%{x}</b> (Imputado)<br>Participación: %{y:.2f} %<br>Locales: %{customdata:,.0f}<extra></extra>",
            ),
        ])
        fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.14)
        max_y = max(max(y_dec, default=1), max(y_imp, default=1))
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(range=[0, max_y * 1.38], ticksuffix=" %")
        return self._estilo(
            fig,
            titulo="PN3 · Oferta por categoría de precio: declarada vs. imputada",
            subtitulo="Unidad: % de restaurantes sobre el total y conteo de establecimientos",
            eje_x="Categoría de rango de precio (escala ordinal)",
            eje_y="% de restaurantes",
            alto=440,
            leyenda=True,
        )

    def figura_pn3_gradiente_traccion(self) -> go.Figure:
        """PN3-B: Gradiente de promedio y mediana de reseñas según nivel de precio."""
        d = self.A.pn3_segmentos_precio_imputado()
        etiquetas_x = [self._etiqueta_precio_corta(c) for c in d["Categoria_Precio"]]
        colores = [self.COLOR_PRECIO.get(c, self.COLOR) for c in d["Categoria_Precio"]]
        fig = go.Figure([
            go.Bar(
                name="Media de reseñas",
                x=etiquetas_x,
                y=d["Promedio_Resenas"],
                marker={"color": colores, "cornerradius": 5},
                text=[f"{numero(v, 1)} res." for v in d["Promedio_Resenas"]],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                customdata=np.stack(
                    [d["Mediana_Resenas"], d["Popularidad_Promedio"], d["Calificacion_Promedio"], d["Reputacion_Ponderada"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Promedio de reseñas: %{y:.2f} opiniones/local<br>"
                    "Mediana de reseñas: %{customdata[0]:.1f} opiniones/local<br>"
                    "Popularidad promedio: %{customdata[1]:.2f} pts<br>"
                    "Calificación: %{customdata[2]:.2f} ★ (Bayesiana: %{customdata[3]:.2f} ★)<extra></extra>"
                ),
            ),
            go.Bar(
                name="Mediana de reseñas (robusta)",
                x=etiquetas_x,
                y=d["Mediana_Resenas"],
                marker={"color": "#1baf7a", "cornerradius": 5},
                text=[f"{numero(m, 0)} res." for m in d["Mediana_Resenas"]],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                hovertemplate="<b>%{x}</b><br>Mediana de reseñas: %{y:.1f} opiniones/local<extra></extra>",
            ),
        ])
        fig.update_layout(barmode="group", bargap=0.30, bargroupgap=0.14)
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(range=[0, d["Promedio_Resenas"].max() * 1.38])
        return self._estilo(
            fig,
            titulo="PN3 · Tracción comercial (media y mediana de reseñas) por nivel de precio",
            subtitulo="Unidad: opiniones por restaurante · Pasa el cursor para ver popularidad (pts) y estrellas (★)",
            eje_x="Categoría de rango de precio imputado ($ a $$$$)",
            eje_y="Reseñas por establecimiento",
            alto=440,
            leyenda=True,
        )

    def figura_pn3_calificacion_vs_bayesiana(self) -> go.Figure:
        """PN3-C: Contraste entre calificación simple y reputación ponderada bayesiana por precio declarado."""
        d = self.A.pn3_segmentos_precio_declarado()
        etiquetas_x = [self._etiqueta_precio_corta(c) for c in d["Categoria_Precio_Declarada"]]
        fig = go.Figure([
            go.Bar(
                name="Calificación simple (media directa)",
                x=etiquetas_x,
                y=d["Calificacion_Promedio"],
                marker={"color": "#9ec5f0", "cornerradius": 4},
                text=[f"{numero(v, 2)} ★" for v in d["Calificacion_Promedio"]],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                customdata=np.stack([d["Promedio_Resenas"], d["Pct_Alta_Reputacion"]], axis=-1),
                hovertemplate=(
                    "<b>%{x}</b><br>Calificación simple: %{y:.2f} ★<br>"
                    "Promedio reseñas: %{customdata[0]:.2f} · Alta rep.: %{customdata[1]:.1f} %<extra></extra>"
                ),
            ),
            go.Bar(
                name="Reputación ponderada bayesiana (m=50)",
                x=etiquetas_x,
                y=d["Reputacion_Ponderada"],
                marker={"color": self.ACENTO, "cornerradius": 4},
                text=[f"{numero(v, 2)} ★" for v in d["Reputacion_Ponderada"]],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                customdata=np.stack([d["Promedio_Resenas"], d["Pct_Alta_Reputacion"]], axis=-1),
                hovertemplate=(
                    "<b>%{x}</b><br>Reputación bayesiana: %{y:.2f} ★<br>"
                    "Corrige el sesgo de pocas reseñas (%{customdata[0]:.1f} res. promedio)<extra></extra>"
                ),
            ),
        ])
        fig.update_layout(barmode="group", bargap=0.32, bargroupgap=0.14)
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(range=[2.8, 4.48])
        return self._estilo(
            fig,
            titulo="PN3 · Calificación simple vs. reputación bayesiana (corrección en 'Sin Precio Declarado')",
            subtitulo="Unidad: estrellas (escala 1,0 a 5,0 ★) · El suavizado bayesiano (m=50) corrige segmentos con pocas reseñas",
            eje_x="Categoría de precio declarada en origen",
            eje_y="Calificación (estrellas ★)",
            alto=440,
            leyenda=True,
        )

    # ==================================================================
    # Figuras de Pregunta de Negocio 4 (PN4): Servicios de Conveniencia
    # ==================================================================
    def figura_pn4_adopcion_individual(self) -> go.Figure:
        """PN4-A: Tasa de adopción (%) de cada uno de los 4 servicios de conveniencia."""
        d = self.A.pn4_adopcion_individual().sort_values("Adopcion_Pct", ascending=True)
        colores = [self.ACENTO if p < 50 else self.COLOR for p in d["Adopcion_Pct"]]
        fig = go.Figure(
            go.Bar(
                x=d["Adopcion_Pct"],
                y=d["Servicio"],
                orientation="h",
                width=0.58,
                marker={"color": colores, "cornerradius": 5},
                text=[
                    f"{pct(p, 1)} ({numero(n)} locales)"
                    for p, n in zip(d["Adopcion_Pct"], d["Restaurantes_Activos"])
                ],
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                customdata=np.stack(
                    [d["Restaurantes_Activos"], d["Promedio_Resenas_Si"], d["Promedio_Resenas_No"], d["Popularidad_Si"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Adopción: %{x:.2f} % (%{customdata[0]:,.0f} locales)<br>"
                    "Reseñas promedio cuando lo ofrece (Sí): %{customdata[1]:.2f}<br>"
                    "Reseñas promedio cuando NO lo ofrece: %{customdata[2]:.2f}<br>"
                    "Popularidad media (Sí): %{customdata[3]:.2f} pts<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(range=[0, 145], ticksuffix=" %", showgrid=True, gridcolor=self.REJILLA)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo="PN4 · Tasa de adopción de los 4 servicios de conveniencia",
            subtitulo="Unidad: % de restaurantes activos y conteo de locales (azul = estándar, naranja = diferenciador)",
            eje_x="Porcentaje de adopción en los restaurantes (%)",
            eje_y=None,
            alto=370,
            margen_izq=210,
            margen_der=65,
        )

    def figura_pn4_impacto_equipamiento(self) -> go.Figure:
        """PN4-B: Promedio y mediana de reseñas según el Nivel de Equipamiento de Servicios."""
        d = self.A.pn4_servicios_conveniencia()
        etiquetas_x = [self._etiqueta_servicio_corta(s) for s in d["Nivel_Servicios"]]
        colores = ["#9ec5f0", self.COLOR, self.ACENTO][: len(d)]
        fig = go.Figure([
            go.Bar(
                name="Media de reseñas por local",
                x=etiquetas_x,
                y=d["Promedio_Resenas"],
                marker={"color": colores, "cornerradius": 5},
                text=[f"{numero(v, 1)} res." for v in d["Promedio_Resenas"]],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                customdata=np.stack(
                    [d["Restaurantes"], d["Participacion_Locales_Pct"], d["Mediana_Resenas"], d["Popularidad_Promedio"], d["Calificacion_Promedio"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Restaurantes: %{customdata[0]:,.0f} (%{customdata[1]:.2f} % de oferta)<br>"
                    "Promedio de reseñas: %{y:.2f} opiniones/local<br>"
                    "Mediana de reseñas: %{customdata[2]:.1f} opiniones/local<br>"
                    "Popularidad media: %{customdata[3]:.2f} pts · Calif.: %{customdata[4]:.2f} ★<extra></extra>"
                ),
            ),
            go.Bar(
                name="Mediana de reseñas (robusta)",
                x=etiquetas_x,
                y=d["Mediana_Resenas"],
                marker={"color": "#1baf7a", "cornerradius": 5},
                text=[f"{numero(m, 0)} res." for m in d["Mediana_Resenas"]],
                textposition="outside",
                textfont={"size": 11.5},
                constraintext="none",
                cliponaxis=False,
                hovertemplate="<b>%{x}</b><br>Mediana de reseñas: %{y:.1f} opiniones/local<extra></extra>",
            ),
        ])
        fig.update_layout(barmode="group", bargap=0.30, bargroupgap=0.14)
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(range=[0, d["Promedio_Resenas"].max() * 1.38])
        return self._estilo(
            fig,
            titulo="PN4 · Volumen de reseñas (media y mediana) por Nivel de Equipamiento",
            subtitulo="Unidad: reseñas por restaurante · El nivel Completo (3–4 servicios) multiplica por 6,7x al Básico",
            eje_x="Nivel de equipamiento operativo (Total_Servicios)",
            eje_y="Reseñas por establecimiento",
            alto=440,
            leyenda=True,
        )

    def figura_pn4_reputacion_equipamiento(self) -> go.Figure:
        """PN4-C: Popularidad promedio y porcentaje de alta reputación según Nivel de Servicios."""
        d = self.A.pn4_servicios_conveniencia()
        etiquetas_x = [self._etiqueta_servicio_corta(s) for s in d["Nivel_Servicios"]]
        colores = ["#9ec5f0", self.COLOR, self.ACENTO][: len(d)]
        fig = go.Figure(
            go.Bar(
                x=etiquetas_x,
                y=d["Popularidad_Promedio"],
                width=0.48,
                marker={"color": colores, "cornerradius": 5},
                text=[
                    f"<b>{numero(pop, 1)} pts</b> · {estrellas(cal)} ({pct(ar, 1)} ≥4★)"
                    for pop, cal, ar in zip(
                        d["Popularidad_Promedio"], d["Calificacion_Promedio"], d["Pct_Alta_Reputacion"]
                    )
                ],
                textposition="outside",
                textfont={"size": 11.5},
                cliponaxis=False,
                customdata=np.stack(
                    [d["Calificacion_Promedio"], d["Reputacion_Ponderada"], d["Pct_Alta_Reputacion"], d["Pct_Hora_Feliz"], d["Pct_Permite_Mascotas"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Popularidad promedio: %{y:.2f} pts<br>"
                    "Calificación media: %{customdata[0]:.2f} ★ (Bayesiana: %{customdata[1]:.2f} ★)<br>"
                    "Alta reputación (≥4,0 ★): %{customdata[2]:.2f} %<br>"
                    "Con Hora Feliz: %{customdata[3]:.1f} % · Con Mascotas: %{customdata[4]:.1f} %<extra></extra>"
                ),
            )
        )
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(range=[0, d["Popularidad_Promedio"].max() * 1.36])
        return self._estilo(
            fig,
            titulo="PN4 · Popularidad promedio, calificación y % de alta reputación por Nivel de Servicios",
            subtitulo="Unidad: puntos de popularidad (pts) · Etiqueta: calificación media (★) y % de locales ≥ 4,0 ★",
            eje_x="Nivel de equipamiento operativo (Total_Servicios)",
            eje_y="Popularidad promedio (pts)",
            alto=430,
        )

    # ==================================================================
    # Figuras de Pregunta de Negocio 5 (PN5): Matriz Distrito × Precio y Mapa
    # ==================================================================
    def figura_pn5_heatmap_oferta(self) -> go.Figure:
        """PN5-A: Mapa de calor Distrito × Categoría de Precio (% dentro del distrito y cantidad de locales)."""
        piv_pct = self.A.pn5_pivot("Participacion_En_Distrito_Pct")
        piv_cnt = self.A.pn5_pivot("Restaurantes")
        if piv_pct.empty:
            return go.Figure()

        etiquetas_x = [self._etiqueta_precio_corta(c) for c in piv_pct.columns]
        texto = [
            [f"{pct(piv_pct.iloc[i, j], 1)}<br>({numero(piv_cnt.iloc[i, j])} locales)" for j in range(piv_pct.shape[1])]
            for i in range(piv_pct.shape[0])
        ]
        fig = go.Figure(
            go.Heatmap(
                z=piv_pct.values,
                x=etiquetas_x,
                y=list(piv_pct.index),
                colorscale=self.ESCALA,
                xgap=4,
                ygap=4,
                text=texto,
                texttemplate="%{text}",
                textfont={"size": 11.5},
                customdata=piv_cnt.values,
                hovertemplate=(
                    "<b>%{y}</b> · %{x}<br>"
                    "Participación dentro del distrito: %{z:.2f} %<br>"
                    "Cantidad de restaurantes: %{customdata:,.0f} locales<extra></extra>"
                ),
                colorbar={"title": {"text": "% dist."}, "ticksuffix": "%", "thickness": 14, "len": 0.85},
            )
        )
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo="PN5 · Mapa de calor de oferta: concentración por Distrito y Nivel de Precio",
            subtitulo="Unidad: % de participación dentro de cada distrito y número de establecimientos entre paréntesis",
            eje_x="Categoría de rango de precio ($ a $$$$)",
            eje_y=None,
            alto=76 * len(piv_pct.index) + 150,
            margen_izq=115,
            margen_der=45,
        )

    def figura_pn5_heatmap_traccion(self, metrica: str = "Promedio_Resenas") -> go.Figure:
        """PN5-B: Mapa de calor Distrito × Categoría de Precio según tracción o reputación."""
        piv_val = self.A.pn5_pivot(metrica)
        piv_cnt = self.A.pn5_pivot("Restaurantes")
        piv_cal = self.A.pn5_pivot("Calificacion_Promedio")
        if piv_val.empty:
            return go.Figure()

        cfg = {
            "Promedio_Resenas": (
                "PN5 · Mapa de calor de tracción: promedio de reseñas por local (Distrito × Precio)",
                "Unidad: opiniones promedio por restaurante y calificación media (★) entre paréntesis",
                "Reseñas",
                lambda v, c: f"{numero(v, 1)} res.<br>({estrellas(c)})",
            ),
            "Popularidad_Promedio": (
                "PN5 · Mapa de calor de popularidad promedio (Calificación × Reseñas)",
                "Unidad: puntos de popularidad promedio (pts) y calificación media (★)",
                "Pts",
                lambda v, c: f"{numero(v, 0)} pts<br>({estrellas(c)})",
            ),
            "Reputacion_Ponderada": (
                "PN5 · Mapa de calor de Reputación Ponderada Bayesiana (★)",
                "Unidad: estrellas ponderadas (1,0 a 5,0 ★) y media simple",
                "★ Bayes",
                lambda v, c: f"{estrellas(v)}<br>(Simple: {numero(c, 2)})",
            ),
        }
        titulo, subtitulo, cbar_tit, fn_celda = cfg.get(metrica, cfg["Promedio_Resenas"])
        etiquetas_x = [self._etiqueta_precio_corta(c) for c in piv_val.columns]

        texto = [
            [fn_celda(piv_val.iloc[i, j], piv_cal.iloc[i, j]) for j in range(piv_val.shape[1])]
            for i in range(piv_val.shape[0])
        ]
        fig = go.Figure(
            go.Heatmap(
                z=piv_val.values,
                x=etiquetas_x,
                y=list(piv_val.index),
                colorscale=self.ESCALA_CALIDA,
                xgap=4,
                ygap=4,
                text=texto,
                texttemplate="%{text}",
                textfont={"size": 11.5},
                customdata=np.stack([piv_cnt.values, piv_cal.values], axis=-1),
                hovertemplate=(
                    "<b>%{y}</b> · %{x}<br>"
                    f"{metrica.replace('_', ' ')}: %{{z:.2f}}<br>"
                    "Restaurantes en el nicho: %{customdata[0]:,.0f} locales<br>"
                    "Calificación promedio: %{customdata[1]:.2f} ★<extra></extra>"
                ),
                colorbar={"title": {"text": cbar_tit}, "thickness": 14, "len": 0.85},
            )
        )
        fig.update_xaxes(tickangle=0)
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)", ticksuffix="  ")
        return self._estilo(
            fig,
            titulo=titulo,
            subtitulo=subtitulo,
            eje_x="Categoría de rango de precio ($ a $$$$)",
            eje_y=None,
            alto=76 * len(piv_val.index) + 150,
            margen_izq=115,
            margen_der=45,
        )

    def figura_pn5_mapa_nyc(self, barrio: str = "Todos", max_puntos: int = 2500) -> go.Figure:
        """PN5-C: Mapa geográfico interactivo de los restaurantes en Nueva York (Scattermap)."""
        R = self.R
        if barrio and barrio != "Todos":
            R = R[R["Barrio"].astype(str) == barrio]
        if R.empty:
            return go.Figure()

        # Se muestran los restaurantes de mayor popularidad (hasta max_puntos) para fluidez visual
        muestra = R.sort_values("Puntaje_Popularidad", ascending=False).head(max_puntos)
        fig = go.Figure()

        for p_cat in ORDEN_PRECIOS:
            sub = muestra[muestra["Categoria_Precio"].astype(str) == p_cat]
            if sub.empty:
                continue
            tamanos = np.clip(5.0 + np.log1p(sub["Total_Resenas"]) * 2.1, 6.0, 22.0)
            fig.add_trace(
                go.Scattermap(
                    lat=sub["Latitud"],
                    lon=sub["Longitud"],
                    mode="markers",
                    name=p_cat,
                    marker={
                        "size": tamanos,
                        "color": self.COLOR_PRECIO.get(p_cat, self.COLOR),
                        "opacity": 0.78,
                    },
                    customdata=np.stack(
                        [
                            sub["Nombre"],
                            sub["Barrio"].astype(str),
                            sub["Tipo_Cocina"],
                            sub["Categoria_Precio"].astype(str),
                            sub["Calificacion"],
                            sub["Total_Resenas"],
                            sub["Puntaje_Popularidad"],
                            sub["Nivel_Servicios"].astype(str),
                        ],
                        axis=-1,
                    ),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Distrito: %{customdata[1]} · Cocina: %{customdata[2]}<br>"
                        "Precio: %{customdata[3]}<br>"
                        "Calificación: %{customdata[4]:.1f} ★ · Reseñas: %{customdata[5]:,.0f}<br>"
                        "Popularidad: %{customdata[6]:,.1f} pts<br>"
                        "Servicios: %{customdata[7]}<extra></extra>"
                    ),
                )
            )

        if barrio and barrio != "Todos" and barrio in CENTROIDES_BARRIOS:
            lat0, lon0 = CENTROIDES_BARRIOS[barrio]
            zoom = 11.4
        else:
            lat0, lon0 = float(muestra["Latitud"].mean()), float(muestra["Longitud"].mean())
            zoom = 9.8

        fig.update_layout(
            map={"style": "carto-positron", "center": {"lat": lat0, "lon": lon0}, "zoom": zoom},
        )
        fig = self._estilo(
            fig,
            titulo=f"PN5 · Mapa geográfico de restaurantes en NYC ({barrio}) — color = precio, tamaño = reseñas",
            subtitulo=f"Mostrando los {numero(len(muestra))} restaurantes de mayor tracción sobre {numero(len(R))} en la selección",
            alto=560,
            leyenda=True,
        )
        fig.update_layout(margin={"l": 0, "r": 0, "t": 122, "b": 10})
        return fig

    # ==================================================================
    # Aplicación Web Completa en Streamlit (render) — Interfaz Limpia y Ejecutiva
    # ==================================================================
    @staticmethod
    def _tarjeta_pregunta(st, r: dict[str, str]) -> None:
        """Muestra un resumen limpio y compacto de la pregunta de negocio, su respuesta y su ficha metodológica."""
        with st.container(border=True):
            st.markdown(f"**{r['id']} · {_esc(r['pregunta'])}**")
            st.markdown(_esc(r["respuesta"]))
            with st.expander("📐 Ver métrica, decisión estratégica y limitación metodológica"):
                st.markdown(f"- **Métrica, cálculo y unidad:** {_esc(r['metrica'])}")
                st.markdown(f"- **Justificación del gráfico:** {_esc(r['visual'])}")
                st.markdown(f"- **Decisión estratégica que apoya:** {_esc(r['decision'])}")
                st.markdown(f"- **Limitación metodológica:** {_esc(r['limitacion'])}")

    def render(self) -> None:
        """Construye y despliega la interfaz interactiva limpia en Streamlit."""
        import streamlit as st

        st.set_page_config(
            page_title="NYC Restaurantes · Visualizador AE4",
            page_icon="🗽",
            layout="wide",
        )
        st.markdown(_CSS, unsafe_allow_html=True)

        # ---------------- Barra lateral limpia (vacío = todos incluidos) ----------------
        base = self.R_total
        with st.sidebar:
            st.subheader("🔍 Filtros de Exploración")
            st.caption("Deja un filtro vacío para incluir todas las categorías.")

            sel_barrios = st.multiselect(
                "Distrito (Borough)",
                self.orden_barrios,
                default=[],
                placeholder="Todos los distritos (5)",
            )

            fams_disp = [f for f in ORDEN_FAMILIAS if f in set(base["Familia_Culinaria"].astype(str))]
            sel_familias = st.multiselect(
                "Macro-familia culinaria",
                fams_disp,
                default=[],
                placeholder="Todas las familias (8)",
            )

            precios_disp = [p for p in ORDEN_PRECIOS if p in set(base["Categoria_Precio"].astype(str))]
            sel_precios = st.multiselect(
                "Categoría de precio",
                precios_disp,
                default=[],
                placeholder="Todos los rangos ($ a $$$$)",
            )

            srv_disp = [s for s in ORDEN_SERVICIOS if s in set(base["Nivel_Servicios"].astype(str))]
            sel_servicios = st.multiselect(
                "Nivel de servicios",
                srv_disp,
                default=[],
                placeholder="Todos los niveles (1 a 4 serv.)",
            )

            c_min, c_max = float(base["Calificacion"].min()), float(base["Calificacion"].max())
            sel_calif = st.slider(
                "Rango de calificación (★)",
                min_value=c_min,
                max_value=c_max,
                value=(c_min, c_max),
                step=0.5,
            )

            busqueda_txt = st.text_input(
                "Buscar restaurante, cocina o ZIP",
                value="",
                placeholder="Ej. Pizza, Mexican, 10009...",
            )

            st.divider()
            st.caption(
                "**Proyecto Integrador S30 · Grupo 6**\n\n"
                "Raul Santiago Morales Henao\n\n"
                "Fuente: `MongoDB/whatscooking.restaurants` + Censo NYC (25.159 locales · 0 nulos)"
            )

        d = self.filtrar(
            barrios=sel_barrios or None,
            familias=sel_familias or None,
            precios=sel_precios or None,
            servicios=sel_servicios or None,
            calificacion_rango=sel_calif,
            busqueda=busqueda_txt,
        )

        # ---------------- Encabezado compacto ----------------
        st.markdown("## 🗽 Panorama Gastronómico de Nueva York (NYC)")
        st.caption(f"**Pregunta general:** {_esc(self.PREGUNTA_NEGOCIO)}  \n📊 **Muestra activa:** {d.alcance_texto()}")

        if d.vacio:
            st.warning("No se encontraron restaurantes con esa combinación de filtros. Limpia o amplía los filtros en la barra lateral.")
            return

        # ---------------- Fila única de 4 KPIs principales ----------------
        k = d.kpis()
        cols_kpi = st.columns(4)
        extra_metric = {"delta_arrow": "off"} if _acepta_delta_arrow(st) else {}
        cols_kpi[0].metric(
            "Restaurantes Activos",
            numero(k["Restaurantes"]),
            f"{pct(k['% del total NYC'], 1, True)} de NYC · {numero(k['Densidad km2'], 1)} loc/km²",
            delta_color="off",
            **extra_metric,
        )
        cols_kpi[1].metric(
            "Reseñas Acumuladas",
            numero(k["Reseñas acumuladas"]),
            f"Media: {numero(k['Promedio reseñas'], 1)} · Mediana: {numero(k['Mediana reseñas'], 0)}",
            delta_color="off",
            **extra_metric,
        )
        cols_kpi[2].metric(
            "Calificación Promedio",
            estrellas(k["Calificación promedio"]),
            f"Bayesiana (m=50): {estrellas(k['Reputación ponderada'])}",
            delta_color="off",
            **extra_metric,
        )
        cols_kpi[3].metric(
            "Popularidad Promedio",
            f"{numero(k['Popularidad promedio'], 1)} pts",
            f"Alta reputación (≥4★): {pct(k['% Alta reputación'], 1, True)}",
            delta_color="off",
            **extra_metric,
        )

        # ---------------- Navegación limpia en 6 pestañas ----------------
        tabs = st.tabs([
            "🏙️ 1. Distritos (PN1)",
            "🍽️ 2. Cocinas (PN2)",
            "💲 3. Precios (PN3)",
            "🛎️ 4. Servicios (PN4)",
            "🗺️ 5. Matriz y Mapa (PN5)",
            "📌 6. Conclusiones y Datos",
        ])
        cfg_plotly = {"displayModeBar": False}
        res_list = d.respuestas()

        # ==================================================================
        # PESTAÑA 0: PN1 · Distritos y Densidad Demográfica
        # ==================================================================
        with tabs[0]:
            self._tarjeta_pregunta(st, res_list[0])
            st.plotly_chart(d.figura_pn1_oferta_distritos(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn1_densidad_territorial(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn1_traccion_distritos(), width="stretch", config=cfg_plotly)

            with st.expander("📋 Ver tabla de datos PN1 (`tabla_pn1_distribucion_distritos.csv`)"):
                st.dataframe(d.A.pn1_distribucion_distritos(incluir_total=True), hide_index=True, width="stretch")

        # ==================================================================
        # PESTAÑA 1: PN2 · Especialidades y Macro-Familias Culinarias
        # ==================================================================
        with tabs[1]:
            self._tarjeta_pregunta(st, res_list[1])
            st.plotly_chart(d.figura_pn2_familias_oferta(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn2_familias_traccion(), width="stretch", config=cfg_plotly)

            col_ctrl1, col_ctrl2 = st.columns([2.2, 1])
            metrica_top = col_ctrl1.radio(
                "Ordenar Top de especialidades individuales por:",
                options=["Restaurantes", "Popularidad_Promedio", "Promedio_Resenas"],
                format_func=lambda x: {
                    "Restaurantes": "Oferta (Restaurantes)",
                    "Popularidad_Promedio": "Popularidad (pts)",
                    "Promedio_Resenas": "Promedio de reseñas",
                }[x],
                horizontal=True,
            )
            top_n_cocinas = col_ctrl2.slider("Top N especialidades", 8, 25, 15)
            st.plotly_chart(
                d.figura_pn2_top_cocinas(n=top_n_cocinas, metrica=metrica_top),
                width="stretch",
                config=cfg_plotly,
            )

            with st.expander("📋 Ver tablas de datos PN2 (Macro-familias y Top Especialidades)"):
                st.markdown("**Las 8 Macro-Familias Culinarias (`tabla_pn2b_familias_culinarias.csv`)**")
                st.dataframe(d.A.pn2_familias_culinarias(), hide_index=True, width="stretch")
                st.markdown(f"**Top {top_n_cocinas} Especialidades (`tabla_pn2_especialidades_culinarias.csv`)**")
                st.dataframe(d.A.pn2_especialidades_culinarias(top_n=top_n_cocinas), hide_index=True, width="stretch")

        # ==================================================================
        # PESTAÑA 2: PN3 · Segmentos de Rango de Precio y Satisfacción
        # ==================================================================
        with tabs[2]:
            self._tarjeta_pregunta(st, res_list[2])
            st.plotly_chart(d.figura_pn3_declarado_vs_imputado(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn3_gradiente_traccion(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn3_calificacion_vs_bayesiana(), width="stretch", config=cfg_plotly)

            with st.expander("📋 Ver tablas de datos PN3 (Precio declarado vs. Precio imputado)"):
                st.markdown("**Precio Declarado en Origen (`tabla_pn3_segmentos_precio.csv`)**")
                st.dataframe(d.A.pn3_segmentos_precio_declarado(), hide_index=True, width="stretch")
                st.markdown("**Precio Final Imputado (`tabla_pn3b_segmentos_precio_imputado.csv`)**")
                st.dataframe(d.A.pn3_segmentos_precio_imputado(), hide_index=True, width="stretch")

        # ==================================================================
        # PESTAÑA 3: PN4 · Servicios de Conveniencia y Equipamiento
        # ==================================================================
        with tabs[3]:
            self._tarjeta_pregunta(st, res_list[3])
            st.plotly_chart(d.figura_pn4_adopcion_individual(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn4_impacto_equipamiento(), width="stretch", config=cfg_plotly)
            st.plotly_chart(d.figura_pn4_reputacion_equipamiento(), width="stretch", config=cfg_plotly)

            with st.expander("📋 Ver tabla de datos PN4 (`tabla_pn4_servicios_conveniencia.csv`)"):
                st.dataframe(d.A.pn4_servicios_conveniencia(), hide_index=True, width="stretch")

        # ==================================================================
        # PESTAÑA 4: PN5 · Matriz Distrito × Precio y Mapa Geográfico NYC
        # ==================================================================
        with tabs[4]:
            self._tarjeta_pregunta(st, res_list[4])
            st.plotly_chart(d.figura_pn5_heatmap_oferta(), width="stretch", config=cfg_plotly)

            metrica_hm = st.radio(
                "Métrica para el mapa de calor de desempeño:",
                options=["Promedio_Resenas", "Popularidad_Promedio", "Reputacion_Ponderada"],
                format_func=lambda x: {
                    "Promedio_Resenas": "Promedio de reseñas por local",
                    "Popularidad_Promedio": "Popularidad promedio (pts)",
                    "Reputacion_Ponderada": "Reputación bayesiana (★)",
                }[x],
                horizontal=True,
            )
            st.plotly_chart(d.figura_pn5_heatmap_traccion(metrica=metrica_hm), width="stretch", config=cfg_plotly)

            opciones_mapa = ["Todos"] + [b for b in self.orden_barrios if b in set(d.R["Barrio"].astype(str))]
            barrio_mapa = st.selectbox("Enfocar mapa interactivo de NYC en el distrito:", opciones_mapa)
            st.plotly_chart(d.figura_pn5_mapa_nyc(barrio=barrio_mapa), width="stretch", config=cfg_plotly)

            with st.expander("📋 Ver matriz de datos PN5 (`tabla_pn5_matriz_distrito_precio.csv`)"):
                st.dataframe(d.A.pn5_matriz_distrito_precio(), hide_index=True, width="stretch")

        # ==================================================================
        # PESTAÑA 5: Conclusiones, Recomendaciones, Limitaciones y Datos
        # ==================================================================
        with tabs[5]:
            c_rec, c_lim = st.columns(2)
            with c_rec:
                with st.container(border=True):
                    st.markdown("#### ✅ Recomendaciones Estratégicas")
                    st.markdown(
                        "1. **Ubicación descentralizada (Brooklyn y Queens):** "
                        "Presentan de 5 a 9 veces menos saturación por km² que Manhattan (172,8 loc/km²), "
                        "manteniendo el mismo flujo promedio de reseñas (~95–97 por local) y calificación (~3,54 ★).\n"
                        "2. **Rango de precio Moderado (\\$\\$) o Costoso selectivo (\\$\\$\\$):** "
                        "Superan ampliamente en tracción al segmento Económico (\\$: 62,1 reseñas y 3,43 ★), "
                        "destacando el nicho Costoso (\\$\\$\\$) en Brooklyn con 208,7 reseñas/local.\n"
                        "3. **Diferenciación culinaria:** "
                        "Apostar por cocina latinoamericana/hispana, mediterránea/española o cafeterías de especialidad, "
                        "que superan en tracción por local a la saturada categoría tradicional *American*.\n"
                        "4. **Formato multipropósito (3 a 4 servicios):** "
                        "Sumar hora feliz y admisión de mascotas al estándar de comida para llevar y terraza "
                        "se asocia con 189,8 reseñas promedio y 3,76 ★."
                    )

            with c_lim:
                with st.container(border=True):
                    st.markdown("#### ⚠️ Limitaciones Metodológicas")
                    st.markdown(
                        "1. **Precios y reseñas vs. ingresos y rentabilidad:** "
                        "`Categoria_Precio` (\\$ a \\$\\$\\$\\$) y `Total_Resenas` miden nivel tarifario de carta y visibilidad digital, "
                        "**no ingresos en dólares ni utilidad neta** (que dependen de arriendo, nómina e insumos).\n"
                        "2. **Asociación observacional, no causalidad:** "
                        "La mayor tracción en locales con 3–4 servicios es una correlación descriptiva y **no prueba causalidad directa**.\n"
                        "3. **Corte transversal sin serie de tiempo:** "
                        "Los datos reflejan el acumulado histórico sin fechas por reseña, por lo que no miden estacionalidad ni supervivencia.\n"
                        "4. **Imputación trazable de precios (9,52 %):** "
                        "Los 2.394 locales sin precio declarado se analizaron por separado y se imputaron con la mediana de `(Tipo_Cocina, Barrio)`."
                    )

            with st.expander("📐 Ver catálogo formal de las 9 métricas del proyecto (fórmula, unidad y propósito)", expanded=True):
                st.dataframe(d.A.tabla_definicion_metricas(), hide_index=True, width="stretch")

            with st.expander("🏆 Ver Top 15 restaurantes y descargar dataset filtrado (CSV)"):
                st.markdown("**Top 15 Restaurantes por Popularidad en la Selección Actual**")
                st.dataframe(d.A.top_restaurantes(15), hide_index=True, width="stretch")
                c_dl1, c_dl2 = st.columns(2)
                c_dl1.download_button(
                    "⬇️ Descargar Dataset Filtrado (CSV)",
                    data=d.R.to_csv(index=False).encode("utf-8"),
                    file_name="whatscooking_restaurants_filtrado_ae4.csv",
                    mime="text/csv",
                )
                c_dl2.download_button(
                    "⬇️ Descargar Tabla Resumen Distritos PN1 (CSV)",
                    data=d.A.pn1_distribucion_distritos(incluir_total=True).to_csv(index=False).encode("utf-8"),
                    file_name="tabla_pn1_distritos_ae4.csv",
                    mime="text/csv",
                )


_CSS = """
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1280px;}
[data-testid="stMetricValue"] {font-size: 1.35rem; font-weight: 700;}
[data-testid="stMetricLabel"] {font-size: 0.85rem; font-weight: 600;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.18); border-radius: 8px; padding: .5rem .8rem; background: #ffffff;}
</style>
"""
