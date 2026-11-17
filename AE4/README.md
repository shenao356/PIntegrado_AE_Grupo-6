# AE4 — Proyecto Integrador (Etapa 3): Métricas y Visualización de Datos

Esta carpeta contiene los entregables de la **Actividad Evaluativa 4 (AE4 - Etapa 3)** del Proyecto Integrador sobre el mercado gastronómico de la ciudad de Nueva York (`MongoDB/whatscooking.restaurants`, **25.159 restaurantes preparados × 27 variables sin valores nulos**).

- **🌐 Enlace directo a la aplicación publicada en Streamlit Community Cloud:** [**https://pintegradoaegrupo-6-dashboard.streamlit.app/**](https://pintegradoaegrupo-6-dashboard.streamlit.app/)

## Estructura de la Carpeta `AE4/`

- **`app.py`**: Punto de entrada de la aplicación web en Streamlit (`streamlit run AE4/app.py`).
- **`src/analisis.py`**: Clase `AnalisisRestaurantesNYC` (hereda de `AnalisisBase`) con las 9 métricas formales (`M1`–`M9`), estadísticos descriptivos, KPIs y métodos para las 5 preguntas de negocio (`PN1`–`PN5`).
- **`src/dashboard_streamlit.py`**: Clase `DashboardStreamlit` con carga desde CSV, 6 filtros interactivos en la barra lateral, 15 gráficos interactivos de Plotly y 6 pestañas temáticas limpias.
- **`notebooks/AE4_Metricas_y_Visualizacion_Streamlit.ipynb`**: Cuaderno Jupyter ejecutado con la definición de métricas, tablas de resultados, generación de las 15 figuras de Plotly y prueba automatizada con `streamlit.testing.v1.AppTest`.
- **`documento/AE4 S30 - Morales Henao Raul Santiago.docx`**: Documento final integrado (Etapas 1, 2 y 3) en Word bajo plantilla institucional IU Digital y normas APA 7.
- **`resultados/tabla_definicion_metricas_ae4.csv`**: Catálogo formal de las 9 métricas con código, nombre, fórmula matemática, unidad de medida, pregunta vinculada y propósito analítico.

## Instrucciones de Ejecución

Desde la raíz del repositorio:

```bash
pip install -r AE4/requirements.txt
streamlit run AE4/app.py
```

También puede ejecutarse desde el paquete central del proyecto:

```bash
streamlit run src/clases_po/app.py
```
