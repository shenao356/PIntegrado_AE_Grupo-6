# Actividad 2: Exploración Inicial del Dataset (Etapa 1)

¡Hola profesor y compañeros! En esta carpeta se encuentra el código y los resultados correspondientes a la **segunda actividad (Etapa 1: Ideación y Diseño)** de nuestro Proyecto Integrador.

---

## Propósito y Necesidad Analítica

- **Propósito:** Definir y documentar una necesidad de analítica descriptiva en el sector gastronómico de la ciudad de Nueva York a partir del reconocimiento técnico de un dataset de Hugging Face, ejecutando un flujo reproducible en Jupyter que genera y verifica automáticamente el resumen estructural en `.txt`.
- **Necesidad y Beneficiario:** Apoyar a emprendedores e inversionistas gastronómicos (escenario hipotético de consultoría sobre datos reales) que requieren caracterizar la oferta existente en los cinco distritos de Nueva York antes de tomar decisiones de apertura o posicionamiento.
- **Pregunta de Análisis:** *¿Cómo se distribuyen los establecimientos gastronómicos registrados en la ciudad de Nueva York según sus distritos geográficos, especialidades culinarias predominantes, rangos de precio y calificaciones de los usuarios, y qué patrones caracterizan su oferta comercial para orientar decisiones de apertura y posicionamiento?*

---

## Estructura de esta actividad

```text
AE2/
├── documento/
│   └── EA2 S30 - Morales Henao Raul Santiago.docx  # Documento inicial del proyecto (Ideacion y Diseno)
├── notebooks/
│   └── EA2_Exploracion_Dataset_HuggingFace.ipynb   # Cuaderno Jupyter con la carga y exploracion
├── resultados/
│   └── resumen_dataframe.txt                       # Archivo de texto con el resumen automatico
├── src/
│   ├── __init__.py
│   └── hf_loader.py                                # Clase para conectarse y descargar datos de Hugging Face
├── requirements.txt                                # Librerias necesarias para ejecutar el codigo
└── README.md                                       # Esta explicacion
```

---

## Dataset Seleccionado

Continuamos trabajando con el dataset de Hugging Face:
- **Identificador:** [`MongoDB/whatscooking.restaurants`](https://huggingface.co/datasets/MongoDB/whatscooking.restaurants)
- **Partición:** `train`
- **Contenido:** 25.361 registros de restaurantes en Nueva York con 18 variables (barrios, tipos de cocina, calificaciones, reseñas y servicios).

---

## Contenido del Notebook

En el cuaderno [`EA2_Exploracion_Dataset_HuggingFace.ipynb`](notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb) realizamos:
1. Conexión y descarga del dataset oficial desde Hugging Face.
2. Carga en un DataFrame de Pandas e inspección de dimensiones (25.361 filas × 18 columnas).
3. Revisión de nombres y tipos de columnas (`dtypes`).
4. Conteo y porcentajes de valores nulos o faltantes (`isna().sum()`).
5. Explicación conceptual de qué representa cada fila y cómo las variables respaldan la necesidad propuesta.
6. Generación automática del archivo [`resumen_dataframe.txt`](resultados/resumen_dataframe.txt) con codificación UTF-8.
7. Verificación del archivo generado directamente dentro del notebook.

---

## ¿Cómo ejecutar el código?

1. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Abrir y ejecutar el notebook:
   ```bash
   jupyter notebook notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb
   ```
