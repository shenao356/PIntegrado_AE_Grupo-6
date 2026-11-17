# Proyecto Integrador de Analítica de Datos (S30) — Grupo 6

¡Hola profesor y compañeros! Este es el repositorio oficial de nuestro **Proyecto Integrador** para la asignatura **Proyecto Integrado III - Analítica de Datos (S30)** en la **Institución Universitaria Digital de Antioquia (IU Digital)**.

- **Estudiante:** Raul Santiago Morales Henao (`shenao356`)
- **Grupo:** Grupo 6
- **Docente:** Andrés Felipe Callejas Jaramillo
- **Dataset en Hugging Face:** [`MongoDB/whatscooking.restaurants`](https://huggingface.co/datasets/MongoDB/whatscooking.restaurants) (`split="train"`)
- **🌐 Aplicación Web Interactiva en Vivo (Streamlit Community Cloud):** [**https://pintegradoaegrupo-6-dashboard.streamlit.app/**](https://pintegradoaegrupo-6-dashboard.streamlit.app/)
- **Comando para ejecución local:** `streamlit run src/clases_po/app.py` (o `streamlit run AE4/app.py`)

---

## Mapa General del Repositorio por Entregas (EA1, AE2, AE3 y AE4)

Conservamos de forma ordenada todas las entregas anteriores y organizamos la entrega final de métricas y visualización en [`src/clases_po/`](src/clases_po/) y [`AE4/`](AE4/):

```text
.
├── .github/
│   └── workflows/
│       └── ejecutar-semana-1.yml                                      # Automatización GitHub Actions (EA1)
├── .streamlit/
│   └── config.toml                                                    # Tema visual claro del dashboard Streamlit (AE4)
├── src/                                                               # Paquete de clases orientadas a objetos (EA1 a AE4)
│   ├── clases_po/
│   │   ├── __init__.py
│   │   ├── hf_loader.py                                               # Clase HFDatasetLoader (EA1/AE2/AE3)
│   │   ├── reportes.py                                                # Clase Reportes (EA1/AE3)
│   │   ├── analisis.py                                                # Clase AnalisisRestaurantesNYC: motor de métricas (AE4)
│   │   ├── dashboard_streamlit.py                                     # Clase DashboardStreamlit: UI y figuras Plotly (AE4)
│   │   ├── app.py                                                     # Punto de entrada de la app Streamlit (AE4)
│   │   └── requirements.txt                                           # Dependencias livianas de la app web (AE4)
│   └── sincronicas/
│       ├── datos/whatscooking_restaurants.csv                         # Muestra inicial transformada (EA1)
│       ├── reportes/whatscooking_restaurants.txt                      # Reporte .txt de muestra (EA1)
│       └── Semana_1SINC.ipynb                                         # Notebook de la Semana 1 (EA1)
├── AE2/                                                               # Entrega 2 (AE2 - Etapa 1): Ideación y Diseño
│   ├── documento/
│   │   └── EA2 S30 - Morales Henao Raul Santiago.docx                 # Documento Word Etapa 1 (AE2)
│   ├── notebooks/
│   │   └── EA2_Exploracion_Dataset_HuggingFace.ipynb                  # Notebook de exploración inicial (25.361 filas)
│   ├── resultados/
│   │   └── resumen_dataframe.txt                                      # Resumen automático .txt de exploración (AE2)
│   ├── src/
│   ├── requirements.txt
│   └── README.md
├── AE3/                                                               # Entrega 3 (AE3 - Etapa 2): Transformación y Enriquecimiento
│   ├── datos/
│   │   └── whatscooking_restaurants_preparado.csv                     # Dataset preparado y enriquecido (25.159 filas × 27 cols)
│   ├── documento/
│   │   ├── AE3 S30 - Morales Henao Raul Santiago.docx                 # Informe Word actualizado (Etapas 1 y 2)
│   │   └── media/                                                     # Ilustraciones 1, 2 y 3 en alta resolución (300 DPI)
│   ├── notebooks/
│   │   └── AE3_Transformacion_y_Enriquecimiento.ipynb                 # Notebook ejecutado con flujo completo de AE3
│   ├── resultados/
│   │   ├── resumen_dataframe.txt                                      # Archivo descriptivo .txt del DataFrame final (Triple A)
│   │   └── tabla_*.csv                                                # Tablas de auditoría y de respuestas PN1 a PN5
│   ├── src/
│   ├── requirements.txt
│   └── README.md
├── AE4/                                                               # Entrega 4 (AE4 - Etapa 3): Métricas y Visualización en Streamlit
│   ├── app.py                                                         # Punto de entrada directo para ejecutar `streamlit run AE4/app.py`
│   ├── datos/
│   │   └── whatscooking_restaurants_preparado.csv                     # Dataset preparado y enriquecido (25.159 filas × 27 cols)
│   ├── documento/
│   │   ├── AE4 S30 - Morales Henao Raul Santiago.docx                 # Informe completo final (Etapas 1, 2 y 3) en Word
│   │   └── media/                                                     # Ilustraciones 1 a 6 del proyecto (300 DPI)
│   ├── notebooks/
│   │   └── AE4_Metricas_y_Visualizacion_Streamlit.ipynb               # Notebook ejecutado de métricas, figuras Plotly y validación AppTest
│   ├── resultados/
│   │   ├── resumen_dataframe.txt                                      # Resumen descriptivo del DataFrame preparado
│   │   ├── tabla_definicion_metricas_ae4.csv                          # Catálogo formal de las 9 métricas (M1-M9) con fórmula y unidad
│   │   └── tabla_*.csv                                                # Tablas de resultados de las preguntas de negocio PN1 a PN5
│   ├── src/
│   │   ├── __init__.py
│   │   ├── analisis.py                                                # Espejo del motor analítico AnalisisRestaurantesNYC
│   │   └── dashboard_streamlit.py                                     # Espejo de la clase visualizadora DashboardStreamlit
│   ├── requirements.txt                                               # Dependencias de la AE4 (streamlit, plotly, pandas, numpy)
│   └── README.md                                                      # Documentación específica de la AE4
├── requirements.txt                                                   # Dependencias globales del proyecto
└── README.md                                                          # Documentación general del repositorio
```

---

## Entrega Actual: AE4 — Etapa 3: Métricas y Visualización de Datos (Streamlit + Plotly)

### 1. Arquitectura Modular de la Solución (`src/clases_po/` y `AE4/`)
Siguiendo el diseño orientado a objetos de la **Semana 6**, separamos la lógica matemática de la interfaz gráfica para garantizar que el **Notebook (`AE4_Metricas_y_Visualizacion_Streamlit.ipynb`)**, el **Informe Técnico (`AE4 S30 - Morales Henao Raul Santiago.docx`)** y la **Aplicación Web (`app.py`)** consuman exactamente los mismos métodos y reporten cifras 100% idénticas:

1. **`src/clases_po/analisis.py` (`AnalisisRestaurantesNYC`):**
   - Formaliza **9 métricas analíticas (`M1` a `M9`)** con nombre claro, fórmula matemática explícita y unidad de medida (`locales`, `%`, `locales/km²`, `locales / 10k hab.`, `★ (1.0 a 5.0)`, `reseñas/local`, `puntos`).
   - Implementa el **Índice de Reputación Ponderada Bayesiana ($\text{IRP}$)** con umbral $m = 50$ reseñas y media global $C = 3,5327\text{ ★}$:
     $$\text{IRP}_i = \frac{v_i}{v_i + m} R_i + \frac{m}{v_i + m} C$$
   - Calcula las tablas de tendencias y comparaciones para las cinco preguntas de negocio (`PN1` a `PN5`) y el cuadro de medidas descriptivas (`media`, `mediana`, `desviación estándar`, `mínimo`, `máximo` e `IQR`).
2. **`src/clases_po/dashboard_streamlit.py` (`DashboardStreamlit`):**
   - Carga automáticamente el dataset preparado [`AE3/datos/whatscooking_restaurants_preparado.csv`](AE3/datos/whatscooking_restaurants_preparado.csv) (**25.159 restaurantes y 27 columnas sin nulos**).
   - Incorpora una **barra lateral con 6 filtros interactivos** (Distrito, Familia Culinaria, Categoría de Precio, Servicios de Conveniencia, Rango de Calificación y Buscador por texto o código postal) más un botón de descarga CSV en vivo.
   - Construye **15 gráficos interactivos en Plotly** con títulos descriptivos, ejes con unidades de medida, etiquetas de datos y paleta cromática fija por distrito (`Manhattan: #2b5c8f`, `Brooklyn: #d95f02`, `Queens: #2ca02c`, `Bronx: #7570b3`, `Staten Island: #e7298a`).
   - Organiza la aplicación en **4 tarjetas KPI principales** y **6 pestañas temáticas limpias**:
     1. `🏙️ 1. Distritos (PN1)`
     2. `🍽️ 2. Cocinas (PN2)`
     3. `💲 3. Precios (PN3)`
     4. `🛎️ 4. Servicios (PN4)`
     5. `🗺️ 5. Matriz y Mapa (PN5)`
     6. `📌 6. Conclusiones y Datos`
3. **`src/clases_po/app.py` (y `AE4/app.py`):**
   - Punto de entrada liviano con `@st.cache_data` para almacenar en caché el DataFrame preparado y actualizar los filtros en milisegundos.
   - **Enlace directo a la aplicación publicada:** [https://pintegradoaegrupo-6-dashboard.streamlit.app/](https://pintegradoaegrupo-6-dashboard.streamlit.app/)

### 2. ¿Cómo Acceder o Ejecutar el Visualizador de Streamlit y el Notebook de la AE4?

- **Opción A — Acceso directo en la nube (sin instalar nada):**
  Ingresa directamente a la aplicación publicada en Streamlit Community Cloud:
  👉 [**https://pintegradoaegrupo-6-dashboard.streamlit.app/**](https://pintegradoaegrupo-6-dashboard.streamlit.app/)

- **Opción B — Ejecución local:**
1. **Clonar el repositorio y activar el entorno virtual:**
   ```bash
   git clone https://github.com/shenao356/PIntegrado_AE_Grupo-6.git
   cd PIntegrado_AE_Grupo-6
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / Mac:
   source .venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación interactiva de Streamlit (cualquiera de los dos comandos equivalentes):**
   ```bash
   streamlit run src/clases_po/app.py
   ```
   o bien:
   ```bash
   streamlit run AE4/app.py
   ```
   La aplicación se abrirá automáticamente en el navegador en `http://localhost:8501`.

4. **Ejecutar el Notebook de la AE4:**
   ```bash
   jupyter notebook AE4/notebooks/AE4_Metricas_y_Visualizacion_Streamlit.ipynb
   ```

### 3. Documentos Entregables y Enlaces de la AE4
- **🌐 Aplicación Web Interactiva publicada en Streamlit:** [**https://pintegradoaegrupo-6-dashboard.streamlit.app/**](https://pintegradoaegrupo-6-dashboard.streamlit.app/)
- **Informe completo del proyecto en Word (Etapas 1, 2 y 3):** [`AE4/documento/AE4 S30 - Morales Henao Raul Santiago.docx`](AE4/documento/AE4%20S30%20-%20Morales%20Henao%20Raul%20Santiago.docx)
- **Notebook ejecutado de la AE4:** [`AE4/notebooks/AE4_Metricas_y_Visualizacion_Streamlit.ipynb`](AE4/notebooks/AE4_Metricas_y_Visualizacion_Streamlit.ipynb)
- **Catálogo de métricas exportado (`.csv`):** [`AE4/resultados/tabla_definicion_metricas_ae4.csv`](AE4/resultados/tabla_definicion_metricas_ae4.csv)

---

## Resumen Histórico de Entregas Anteriores (EA1, AE2 y AE3)

- **Entrega 1 (EA1):** Implementación de las clases `HFDatasetLoader` y `Reportes` en [`src/clases_po/`](src/clases_po/), notebook [`src/sincronicas/Semana_1SINC.ipynb`](src/sincronicas/Semana_1SINC.ipynb) sobre una muestra de 5.000 registros y flujo de integración continua en [`.github/workflows/ejecutar-semana-1.yml`](.github/workflows/ejecutar-semana-1.yml).
- **Entrega 2 (AE2 - Etapa 1):** Documentación de la necesidad, pregunta de análisis, objetivos, diccionario inicial y exploración completa de los 25.361 registros en [`AE2/notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb`](AE2/notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb) y [`AE2/resultados/resumen_dataframe.txt`](AE2/resultados/resumen_dataframe.txt).
- **Entrega 3 (AE3 - Etapa 2):** Limpieza, validación y enriquecimiento del dataset hasta obtener **25.159 restaurantes × 27 columnas con 0 nulos** en [`AE3/datos/whatscooking_restaurants_preparado.csv`](AE3/datos/whatscooking_restaurants_preparado.csv), documentado en [`AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb`](AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb) y [`AE3/documento/AE3 S30 - Morales Henao Raul Santiago.docx`](AE3/documento/AE3%20S30%20-%20Morales%20Henao%20Raul%20Santiago.docx).
