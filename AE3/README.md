# Actividad 3 (AE3): Proyecto Integrador - Etapa 2: Transformación y Enriquecimiento de Datos

¡Hola profesor y compañeros! En esta carpeta (`AE3/`) se encuentra el desarrollo íntegro de la **Segunda Etapa (AE3: Transformación y Enriquecimiento de Datos)** de nuestro Proyecto Integrador para la asignatura **Proyecto Integrado III - Analítica de Datos (S30)** en la **Institución Universitaria Digital de Antioquia (IU Digital)**.

- **Grupo:** Grupo 6
- **Estudiante:** Raul Santiago Morales Henao (`shenao356`)
- **Docente:** Andrés Felipe Callejas Jaramillo
- **Dataset en Hugging Face:** [`MongoDB/whatscooking.restaurants`](https://huggingface.co/datasets/MongoDB/whatscooking.restaurants) (`split="train"`)

---

## 1. Estructura de Carpetas y Rutas de Resultados (`AE3/`)

```text
AE3/
├── datos/
│   └── whatscooking_restaurants_preparado.csv          # Dataset final transformado y enriquecido (25.159 filas × 27 columnas, 0 nulos)
├── documento/
│   ├── AE3 S30 - Morales Henao Raul Santiago.docx      # Informe Word actualizado (Etapas 1 y 2) en formato APA 7
│   └── media/                                          # Ilustraciones metodológicas en alta definición (300 DPI)
│       ├── ilustracion1_necesidad_datos_decisiones.png
│       ├── ilustracion2_etapas_proyecto.png
│       └── ilustracion3_flujo_transformacion_enriquecimiento.png
├── notebooks/
│   └── AE3_Transformacion_y_Enriquecimiento.ipynb      # Notebook ejecutado de principio a fin con resultados visibles
├── resultados/
│   ├── resumen_dataframe.txt                           # Archivo descriptivo .txt del DataFrame final (generado por clase Reportes)
│   ├── tabla_control_calidad_antes_despues.csv         # Auditoría comparativa antes y después de la preparación
│   ├── tabla_pn1_distribucion_distritos.csv            # Tabla resultado Pregunta de Negocio 1 (Distritos y densidad)
│   ├── tabla_pn2_especialidades_culinarias.csv         # Tabla resultado Pregunta de Negocio 2-B (Top 15 Especialidades)
│   ├── tabla_pn2b_familias_culinarias.csv              # Tabla resultado Pregunta de Negocio 2-A (8 Familias Culinarias)
│   ├── tabla_pn3_segmentos_precio.csv                  # Tabla resultado Pregunta de Negocio 3-A (Precio declarado con 'No Especificado')
│   ├── tabla_pn3b_segmentos_precio_imputado.csv        # Tabla resultado Pregunta de Negocio 3-B (Precio imputado niveles 1 a 4)
│   ├── tabla_pn4_servicios_conveniencia.csv            # Tabla resultado Pregunta de Negocio 4 (Niveles de equipamiento de servicios)
│   └── tabla_pn5_matriz_distrito_precio.csv            # Tabla resultado Pregunta de Negocio 5 (Matriz Distrito × Categoría de Precio)
├── src/
│   ├── __init__.py
│   ├── hf_loader.py                                    # Clase HFDatasetLoader para conexión y descarga desde Hugging Face
│   └── reportes.py                                     # Clase Reportes para generar y exportar el resumen descriptivo .txt (Triple A)
├── requirements.txt                                    # Dependencias de Python para ejecutar la entrega
└── README.md                                           # Esta guía detallada de la entrega AE3
```

---

## 2. Continuidad y Preguntas de Negocio Abordadas (Retoma de AE2)

En la **AE2 (Etapa 1)** definimos la necesidad de negocio para un equipo de emprendedores e inversionistas gastronómicos que evalúan abrir o posicionar un restaurante en Nueva York, formulando la pregunta rectora:
> *¿Cómo se distribuyen los establecimientos gastronómicos registrados en la ciudad de Nueva York según sus distritos geográficos, especialidades culinarias predominantes, rangos de precio y calificaciones de los usuarios, y qué patrones caracterizan su oferta comercial para orientar decisiones de apertura y posicionamiento?*

En esta **AE3**, los cinco literales de información requerida (*a–e*) planteados en la AE2 se responden mediante **5 preguntas de negocio operativas (PN1 a PN5)**:
1. **PN1 (Concentración y densidad por distrito):** ¿Cómo se distribuye la oferta de restaurantes y el volumen de reseñas entre los cinco distritos de Nueva York, y cuál es la densidad comercial (por $\text{km}^2$ y por 10.000 habitantes) y reputación promedio en cada zona?
2. **PN2 (Especialidades y familias culinarias):** ¿Cuáles son las especialidades culinarias (`Tipo_Cocina`) y las 8 familias gastronómicas (`Familia_Culinaria`) predominantes en Nueva York, y cómo se comparan en calificación promedio, reseñas y popularidad?
3. **PN3 (Estructura de precios y reputación):** ¿Cómo se segmenta la oferta gastronómica según las categorías de rango de precio (`Categoria_Precio_Declarada` y `Categoria_Precio`) y qué diferencias existen en sus calificaciones y volumen de interacción?
4. **PN4 (Servicios de conveniencia):** ¿Qué proporción de restaurantes ofrece servicios de conveniencia (`Para_Llevar`, `Mesas_Exteriores`, `Hora_Feliz`, `Permite_Mascotas`) y cómo varía la popularidad según el nivel de servicios ofrecidos (`Nivel_Equipamiento_Servicios`)?
5. **PN5 (Cruce estratégico Distrito × Precio):** ¿Cómo se cruzan el distrito geográfico (`Barrio`) y el nivel de precios (`Categoria_Precio`) en densidad de oferta y reputación para detectar saturación o nichos de mercado?

---

## 3. Transformaciones y Controles de Calidad Realizados

Partiendo del dataset original de **25.361 filas y 18 columnas** (`df_original`), aplicamos las siguientes operaciones justificadas:
1. **Rescate de atributos anidados y selección de columnas:** Se extrajo el código postal (`Codigo_Postal`) desde `address`, la `Longitud` y `Latitud` desde `location`, y el conteo de platos (`Cantidad_Platos_Menu`) desde la lista `menu`. Se descartaron columnas técnicas/vacías (`_id`, `embedding`, `sponsored` con 99,91% de nulos, y los contenedores crudos).
2. **Filtrado justificado de faltantes ocultos en texto:** La inspección semántica detectó **151 registros con nombre comercial vacío (`""`)** y **51 registros con distrito `"Missing"`** (202 registros disjuntos = **0,80%** del total). Se excluyeron justificadamente por carecer de identificación o distrito válido, conservando **25.159 establecimientos válidos (99,20%)**.
3. **Unicidad de clave primaria (`ID_Restaurante`):** Se verificó que existen `0` filas duplicadas completas y se desambiguó el único identificador repetido (`40720599` $\rightarrow$ `40720599_2`), correspondiente a dos restaurantes reales distintos en Manhattan.
4. **Normalización textual y corrección UTF-8:** Se limpiaron espacios extremos y se corrigió el error de codificación `"CafÃ©/Coffee/Tea"` $\rightarrow$ `"Café/Coffee/Tea"` (2 registros), además de estandarizar 5 nombres extensos de cocina (**1.798 registros normalizados**, consolidando **84 especialidades limpias**).
5. **Tipado booleano y validación geográfica en NYC:** Se convirtieron `Mesas_Exteriores`, `Para_Llevar`, `Hora_Feliz` y `Permite_Mascotas` de `object` a `bool` estricto (`True`/`False`). Se validaron las coordenadas dentro de la caja geográfica de NYC (`Latitud` $[40.45, 40.95]$, `Longitud` $[-74.30, -73.65]$), corrigiendo 45 registros con la mediana de su distrito.
6. **Doble tratamiento trazable para `Rango_Precio` (2.394 nulos, 9,52%):** Se creó `Categoria_Precio_Declarada` conservando la etiqueta `"No Especificado"` para análisis de transparencia, y se imputó `Rango_Precio` (`int64` de 1 a 4) usando la **mediana condicional por `(Tipo_Cocina, Barrio)`**, logrando **0 valores nulos** en todo el DataFrame final.

---

## 4. Enriquecimiento de Datos e Integración Relacional

Se incorporaron **9 variables enriquecidas** para sustentar el análisis:
- **`Familia_Culinaria`:** Clasificación taxonómica de las 84 cocinas en **8 grandes familias gastronómicas**.
- **`Categoria_Precio_Declarada` y `Categoria_Precio`:** Etiquetas ordinales comerciales (`1 - Económico ($)` a `4 - Lujo ($$$$)`).
- **`Total_Servicios_Conveniencia` y `Nivel_Equipamiento_Servicios`:** Conteo y clasificación del equipamiento de conveniencia (`Equipamiento Básico`, `Equipamiento Intermedio`, `Equipamiento Completo`).
- **`Indice_Traccion_Comercial`:** $\text{Calificacion} \times \text{Total\_Resenas}$ (continuidad con EA1).
- **Integración con Catálogo Demográfico de NYC (`merge` `many_to_one`):** Unión validada por `Barrio` con datos oficiales del Censo de NYC (`Poblacion_Distrito`, `Superficie_Km2`, `Vocacion_Comercial`), verificando que las filas (`25.159`) y las reseñas acumuladas (`2.415.896`) no se multipliquen ni alteren.

---

## 5. Pasos de Ejecución

1. **Instalar dependencias (en entorno virtual):**
   ```bash
   pip install -r AE3/requirements.txt
   ```

2. **Abrir o ejecutar el Notebook de AE3:**
   ```bash
   jupyter notebook AE3/notebooks/AE3_Transformacion_y_Enriquecimiento.ipynb
   ```
   Al ejecutarse, el notebook regenera automáticamente el dataset preparado en `AE3/datos/whatscooking_restaurants_preparado.csv`, las 8 tablas `.csv` en `AE3/resultados/` y el reporte descriptivo `AE3/resultados/resumen_dataframe.txt`.
