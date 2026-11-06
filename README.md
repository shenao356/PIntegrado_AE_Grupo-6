# Proyecto Integrador de Analítica de Datos (S30) — Grupo 6

¡Hola profesor y compañeros! Este es el repositorio oficial de nuestro **Proyecto Integrador** para la asignatura **Proyecto Integrado III - Analítica de Datos (S30)** en la **Institución Universitaria Digital de Antioquia (IU Digital)**.

- **Estudiante:** Raul Santiago Morales Henao (`shenao356`)
- **Grupo:** Grupo 6
- **Docente:** Andrés Felipe Callejas Jaramillo
- **Dataset en Hugging Face:** [`MongoDB/whatscooking.restaurants`](https://huggingface.co/datasets/MongoDB/whatscooking.restaurants) (`split="train"`)

---

## Mapa General del Repositorio por Entregas (EA1, AE2 y AE3)

Conservamos de forma ordenada todas las entregas anteriores y organizamos la tercera entrega en la carpeta [`AE3/`](AE3/):

```text
.
├── .github/
│   └── workflows/
│       └── ejecutar-semana-1.yml                                      # Automatización GitHub Actions (EA1, AE2 y AE3)
├── src/                                                               # Entrega 1 (EA1): Carga y Creación de Dataset
│   ├── clases_po/
│   │   ├── __init__.py
│   │   ├── hf_loader.py                                               # Clase HFDatasetLoader (EA1)
│   │   └── reportes.py                                                # Clase Reportes (EA1)
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
│   │   ├── __init__.py
│   │   └── hf_loader.py
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
│   │   ├── tabla_control_calidad_antes_despues.csv                    # Tabla de auditoría antes y después
│   │   ├── tabla_pn1_distribucion_distritos.csv                       # Tabla resultado Pregunta de Negocio 1
│   │   ├── tabla_pn2_especialidades_culinarias.csv                    # Tabla resultado Pregunta de Negocio 2-B (Top 15 Cocinas)
│   │   ├── tabla_pn2b_familias_culinarias.csv                         # Tabla resultado Pregunta de Negocio 2-A (8 Familias)
│   │   ├── tabla_pn3_segmentos_precio.csv                             # Tabla resultado Pregunta de Negocio 3-A (Precio declarado)
│   │   ├── tabla_pn3b_segmentos_precio_imputado.csv                   # Tabla resultado Pregunta de Negocio 3-B (Precio imputado)
│   │   ├── tabla_pn4_servicios_conveniencia.csv                       # Tabla resultado Pregunta de Negocio 4 (Servicios)
│   │   └── tabla_pn5_matriz_distrito_precio.csv                       # Tabla resultado Pregunta de Negocio 5 (Distrito × Precio)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── hf_loader.py                                               # Clase para carga desde Hugging Face
│   │   └── reportes.py                                                # Clase para generar el resumen .txt del DataFrame final
│   ├── requirements.txt
│   └── README.md
├── requirements.txt                                                   # Dependencias globales del proyecto
└── README.md                                                          # Documentación general del repositorio
```

---

## Avance Actual: Entrega 3 (AE3) — Etapa 2: Transformación y Enriquecimiento de Datos

### 1. Necesidad y Preguntas de Negocio Abordadas (Continuidad con AE2)
Retomamos la necesidad formulada en la **AE2**: apoyar con evidencia cuantitativa y descriptiva a un equipo de emprendedores e inversionistas gastronómicos que evalúan abrir o posicionar un restaurante en la ciudad de Nueva York. A partir de la pregunta general de análisis y de los cinco literales de información requerida (*a–e*) planteados en AE2, estructuramos y respondemos **5 preguntas de negocio operativas**:
- **PN1 (Concentración y densidad por distrito):** ¿Cómo se distribuye la oferta de restaurantes y el volumen de reseñas entre los cinco distritos de Nueva York (*Manhattan, Brooklyn, Queens, Bronx, Staten Island*), y cuál es la densidad comercial (por $\text{km}^2$ y por 10.000 habitantes) y reputación promedio en cada zona?
- **PN2 (Especialidades y familias culinarias predominantes):** ¿Cuáles son las especialidades culinarias (`Tipo_Cocina`) y las 8 familias gastronómicas (`Familia_Culinaria`) con mayor presencia en Nueva York, y cómo se comparan en calificación, reseñas y popularidad?
- **PN3 (Estructura de precios y relación con la satisfacción):** ¿Cómo se segmenta la oferta gastronómica según las categorías de rango de precio (`Categoria_Precio_Declarada` y `Categoria_Precio`) y qué diferencias existen en sus calificaciones y volumen de interacción?
- **PN4 (Servicios de conveniencia y valor agregado):** ¿Qué proporción de restaurantes ofrece servicios de conveniencia (`Para_Llevar`, `Mesas_Exteriores`, `Hora_Feliz`, `Permite_Mascotas`) y cómo varía la popularidad según el nivel de servicios ofrecidos (`Nivel_Equipamiento_Servicios`)?
- **PN5 (Cruce estratégico Distrito × Categoría de Precio):** ¿Cómo se cruzan el distrito geográfico (`Barrio`) y el nivel de precios (`Categoria_Precio`) en densidad de oferta y reputación para detectar zonas saturadas frente a posibles nichos de oportunidad?

### 2. Transformaciones y Reglas de Calidad Aplicadas
Sobre el dataset completo de **25.361 registros y 18 columnas** (`df_original`), el cuaderno [`AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb`](AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb) ejecuta y valida:
1. **Rescate de atributos desde campos anidados y selección de columnas:** Se extrajo `Codigo_Postal` desde `address`, `Longitud` y `Latitud` desde `location`, y `Cantidad_Platos_Menu` desde `menu`. Se descartaron las columnas técnicas o vacías (`_id`, `embedding`, `sponsored` con 99,91% de nulos y diccionarios crudos) y se renombraron las variables al español.
2. **Detección y filtrado justificado de faltantes ocultos en texto:** Se identificaron **151 registros con nombre vacío (`""`)** y **51 registros con distrito `"Missing"`** (202 registros incompletos = **0,80%** del total). Se excluyeron justificadamente para garantizar que toda unidad de análisis sea un establecimiento real ubicado en un distrito válido, conservando **25.159 restaurantes válidos (99,20%)**.
3. **Unicidad de clave primaria (`ID_Restaurante`):** Se comprobó que hay `0` filas duplicadas exactas y se desambiguó la única colisión de ID (`40720599` $\rightarrow$ `40720599_2`) entre dos restaurantes reales distintos en Manhattan.
4. **Normalización de categorías y corrección UTF-8:** Se limpiaron espacios extremos y se corrigieron errores de codificación (`"CafÃ©/Coffee/Tea"` $\rightarrow$ `"Café/Coffee/Tea"`) y etiquetas extensas en **1.798 registros**, consolidando **84 especialidades culinarias limpias**.
5. **Conversión a tipos booleanos estrictos y validación geográfica en NYC:** `Mesas_Exteriores`, `Para_Llevar`, `Hora_Feliz` y `Permite_Mascotas` pasaron de `object` (con valores `None`) a `bool` (`True`/`False`). Se validaron las coordenadas dentro de los límites de NYC (`Latitud` $[40.45, 40.95]$, `Longitud` $[-74.30, -73.65]$), imputando 45 registros fuera de rango con la mediana de su distrito.
6. **Doble tratamiento trazable de `Rango_Precio` (2.394 nulos, 9,52%):** Se conservó la etiqueta `"No Especificado"` en `Categoria_Precio_Declarada` y se imputó `Rango_Precio` (`int64` de 1 a 4) con la **mediana condicional de `(Tipo_Cocina, Barrio)`**, obteniendo **0 valores nulos** en las 27 columnas finales.

### 3. Enriquecimiento de la Información
Se incorporaron **9 variables enriquecidas** documentadas en el diccionario de datos actualizado:
- `Familia_Culinaria` (8 grandes familias gastronómicas).
- `Categoria_Precio_Declarada` y `Categoria_Precio` (`1 - Económico ($)` a `4 - Lujo ($$$$)`).
- `Total_Servicios_Conveniencia` y `Nivel_Equipamiento_Servicios` (`Equipamiento Básico`, `Equipamiento Intermedio`, `Equipamiento Completo`).
- `Indice_Traccion_Comercial` ($\text{Calificacion} \times \text{Total\_Resenas}$).
- **Integración con Catálogo Demográfico y Territorial de NYC (`merge` `many_to_one`):** Unión validada por `Barrio` que incorpora `Poblacion_Distrito`, `Superficie_Km2` y `Vocacion_Comercial` sin multiplicar filas (`25.159` antes y después) ni alterar el total de reseñas (`2.415.896`).

### 4. Rutas del Dataset Preparado, Tablas de Resultados y Archivo Descriptivo `.txt`
- **Notebook ejecutado:** [`AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb`](AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb)
- **Documento Word actualizado:** [`AE3/documento/AE3 S30 - Morales Henao Raul Santiago.docx`](AE3/documento/AE3%20S30%20-%20Morales%20Henao%20Raul%20Santiago.docx)
- **Dataset preparado (`.csv`):** [`AE3/datos/whatscooking_restaurants_preparado.csv`](AE3/datos/whatscooking_restaurants_preparado.csv)
- **Archivo descriptivo del DataFrame final (`.txt`):** [`AE3/resultados/resumen_dataframe.txt`](AE3/resultados/resumen_dataframe.txt)
- **Tablas de resultados exportadas (`.csv`):**
  - [`AE3/resultados/tabla_control_calidad_antes_despues.csv`](AE3/resultados/tabla_control_calidad_antes_despues.csv)
  - [`AE3/resultados/tabla_pn1_distribucion_distritos.csv`](AE3/resultados/tabla_pn1_distribucion_distritos.csv)
  - [`AE3/resultados/tabla_pn2_especialidades_culinarias.csv`](AE3/resultados/tabla_pn2_especialidades_culinarias.csv)
  - [`AE3/resultados/tabla_pn2b_familias_culinarias.csv`](AE3/resultados/tabla_pn2b_familias_culinarias.csv)
  - [`AE3/resultados/tabla_pn3_segmentos_precio.csv`](AE3/resultados/tabla_pn3_segmentos_precio.csv)
  - [`AE3/resultados/tabla_pn3b_segmentos_precio_imputado.csv`](AE3/resultados/tabla_pn3b_segmentos_precio_imputado.csv)
  - [`AE3/resultados/tabla_pn4_servicios_conveniencia.csv`](AE3/resultados/tabla_pn4_servicios_conveniencia.csv)
  - [`AE3/resultados/tabla_pn5_matriz_distrito_precio.csv`](AE3/resultados/tabla_pn5_matriz_distrito_precio.csv)

---

## ¿Cómo Ejecutar el Proyecto Localmente?

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
   pip install -r AE3/requirements.txt
   ```

3. **Ejecutar el Notebook de la AE3:**
   ```bash
   jupyter notebook AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb
   ```

---

## Resumen Histórico de Entregas Anteriores (EA1 y AE2)

- **Entrega 1 (EA1):** Implementación de las clases `HFDatasetLoader` y `Reportes` en [`src/clases_po/`](src/clases_po/), notebook [`src/sincronicas/Semana_1SINC.ipynb`](src/sincronicas/Semana_1SINC.ipynb) sobre una muestra de 5.000 registros y flujo de integración continua en [`.github/workflows/ejecutar-semana-1.yml`](.github/workflows/ejecutar-semana-1.yml).
- **Entrega 2 (AE2 - Etapa 1):** Documentación de la necesidad, pregunta de análisis, objetivos, diccionario inicial y exploración completa de los 25.361 registros en [`AE2/notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb`](AE2/notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb) y [`AE2/resultados/resumen_dataframe.txt`](AE2/resultados/resumen_dataframe.txt).
