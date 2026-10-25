# Actividad 1 y 2: Carga, Preparación e Ideación de Datos desde Hugging Face

¡Hola! Este es el repositorio de mi trabajo para las actividades del Proyecto Integrador de la materia. 

El objetivo principal es aprender a conectarnos a Hugging Face para descargar un conjunto de datos, procesarlo y explorarlo usando Python y Pandas dentro de un Jupyter Notebook, estructurar el código mediante clases orientadas a objetos, documentar la necesidad analítica y exportar los reportes en archivo `.txt`. Además, implementamos control de versiones con Git/GitHub y una automatización con GitHub Actions.

---

## Dataset Seleccionado

Para el proyecto elegí el dataset gastronómico:
- **Enlace en Hugging Face:** [`MongoDB/whatscooking.restaurants`](https://huggingface.co/datasets/MongoDB/whatscooking.restaurants)
- **División utilizada:** `train`
- **¿Por qué este dataset?:** Me pareció muy entretenido y práctico para practicar porque contiene información real de restaurantes en Nueva York: tipos de cocina (italiana, mexicana, etc.), barrios, calificaciones con estrellas, cantidad de reseñas y facilidades como servicio para llevar o mesas al aire libre.

---

## Estructura de Carpetas del Proyecto

Organizamos los archivos de la siguiente manera para mantener todo en orden:

```text
.
├── .github/
│   └── workflows/
│       └── ejecutar-semana-1.yml        # Flujo de GitHub Actions para correr todo automaticamente
├── AE2/                                 # Etapa 1 Proyecto Integrador (AE2): Ideacion, Diseno y Necesidad
│   ├── documento/
│   │   └── EA2 S30 - Morales Henao Raul Santiago.docx
│   ├── notebooks/
│   │   └── EA2_Exploracion_Dataset_HuggingFace.ipynb
│   ├── resultados/
│   │   └── resumen_dataframe.txt
│   ├── src/
│   │   ├── __init__.py
│   │   └── hf_loader.py
│   ├── README.md
│   └── requirements.txt
├── src/
│   ├── clases_po/                      # Aqui estan las clases en Python que nos pide la guia
│   │   ├── __init__.py
│   │   ├── hf_loader.py                # Clase para conectarse y descargar datos de Hugging Face
│   │   └── reportes.py                 # Clase para armar y guardar el reporte en texto (.txt)
│   └── sincronicas/
│       ├── datos/
│       │   └── whatscooking_restaurants.csv  # Archivo CSV con los datos limpios y transformados
│       ├── reportes/
│       │   └── whatscooking_restaurants.txt  # Resumen final con estadisticas de los datos
│       └── Semana_1SINC.ipynb          # Cuaderno Jupyter donde coordinamos todo el flujo
├── .gitignore                          # Archivos temporales o pesados que no subimos a Git
├── README.md                           # Esta guia de explicacion del proyecto
└── requirements.txt                    # Librerias que necesitamos instalar
```

---

## Explicación de las Clases Creadas

Para cumplir con la rúbrica y buenas prácticas de programación orientada a objetos, separamos las tareas en dos clases:

### 1. `HFDatasetLoader` (`src/clases_po/hf_loader.py` y `AE2/src/hf_loader.py`)
Es la encargada de hacer la conexión con Hugging Face.
- Recibe el nombre del dataset (`dataset_name`) y el split.
- Permite limitar el número de filas (`max_rows`) para que la prueba no tarde tanto tiempo descargando datos innecesarios.
- También soporta modo streaming y la opción de guardar a disco si se necesita.
- Al final nos devuelve un DataFrame de pandas listo para usar.

### 2. `Reportes` (`src/clases_po/reportes.py`)
Es la encargada de generar el resumen del DataFrame.
- Revisa cuántas filas y columnas tiene la tabla.
- Cuenta si hay registros duplicados.
- Muestra el listado de columnas y sus tipos de datos.
- Revisa cuántos valores nulos o faltantes hay en cada campo.
- Calcula estadísticas básicas (conteo, promedio, desviación, mínimo, percentiles y máximo) para las columnas numéricas.
- Permite ver el reporte en pantalla o guardarlo directamente en un archivo de texto `.txt`.

---

## Flujo del Notebook y las 4 Transformaciones (Actividad 1)

Todo el proceso de la Actividad 1 se coordina desde el cuaderno [`src/sincronicas/Semana_1SINC.ipynb`](src/sincronicas/Semana_1SINC.ipynb). Allí aplicamos **cuatro transformaciones** a los datos:

1. **Transformación 1 (Selección y traducción de columnas):**
   El dataset original traía columnas complejas que no íbamos a usar (como vectores numéricos de embedding). Seleccionamos 9 columnas de interés para el análisis y les cambiamos el nombre al español (`ID_Restaurante`, `Nombre`, `Barrio`, `Tipo_Cocina`, `Calificacion`, `Total_Resenas`, `Rango_Precio`, `Mesas_Exteriores`, `Para_Llevar`) para que sea más amigable y entendible.

2. **Transformación 2 (Filtrado de calidad):**
   Eliminamos restaurantes que tuvieran datos faltantes en nombre o tipo de cocina. También dejamos únicamente aquellos con calificación mayor o igual a 3.0 estrellas y que tuvieran como mínimo 5 reseñas, para evitar registros con poca información.

3. **Transformación 3 (Creación de nuevas columnas):**
   - `Puntaje_Popularidad`: Multiplicamos la calificación por la cantidad de reseñas (`Calificacion * Total_Resenas`). Así los restaurantes bien calificados y muy visitados obtienen un puntaje más alto.
   - `Categoria_Precio`: Los precios venían en números (1, 2, 3, 4). Creamos una columna de texto que los traduce a nombres claros: Económico, Moderado, Costoso o Gourmet.

4. **Transformación 4 (Limpieza y ordenamiento):**
   Estandarizamos el texto en `Tipo_Cocina` y `Barrio` quitando espacios extras y poniéndolos en formato tipo título (primera letra en mayúscula). Rellenamos los valores vacíos de opciones booleanas con `False`, ordenamos la tabla de mayor a menor popularidad y reiniciamos el índice.

Al final, guardamos los datos limpios en `datos/whatscooking_restaurants.csv` y llamamos a la clase `Reportes` para crear el archivo `reportes/whatscooking_restaurants.txt`.

Para el detalle de la **Actividad 2 (Etapa 1 del Proyecto Integrador)**, consulta [`AE2/README.md`](AE2/README.md).

---

## ¿Cómo ejecutar el proyecto en tu computadora?

Si quieres probar el código localmente, sigue estos sencillos pasos:

1. **Clonar este repositorio:**
   ```bash
   git clone https://github.com/shenao356/PIntegrado_AE_Grupo-6.git
   cd PIntegrado_AE_Grupo-6
   ```

2. **Crear y activar un entorno virtual (recomendado):**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / Mac:
   source .venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   pip install -r AE2/requirements.txt
   ```

4. **Abrir y correr los Notebooks:**
   ```bash
   jupyter notebook src/sincronicas/Semana_1SINC.ipynb
   jupyter notebook AE2/notebooks/EA2_Exploracion_Dataset_HuggingFace.ipynb
   ```

---

## Automatización con GitHub Actions

Para asegurar que todo funcione siempre de manera automática:
- El archivo `.github/workflows/ejecutar-semana-1.yml` se ejecuta cada vez que hacemos un `push` a la rama `main`.
- Este proceso prepara el entorno, borra resultados anteriores para que no queden archivos viejos, corre los notebooks de principio a fin (tanto el de la Semana 1 como el de la `AE2`), genera el CSV y los reportes `.txt` (`src/sincronicas/reportes/whatscooking_restaurants.txt` y `AE2/resultados/resumen_dataframe.txt`), y guarda los resultados automáticamente.
- Al terminar, limpia los archivos temporales para dejar el entorno ordenado.
