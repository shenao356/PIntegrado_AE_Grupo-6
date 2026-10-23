# Actividad 2: Exploración Inicial del Dataset (Etapa 1)

¡Hola profesor y compañeros! En esta carpeta se encuentra el código y los resultados correspondientes a la **segunda actividad (Etapa 1: Ideación y Diseño)** de nuestro Proyecto Integrador.

---

## Estructura de esta actividad

```text
AE2/
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
