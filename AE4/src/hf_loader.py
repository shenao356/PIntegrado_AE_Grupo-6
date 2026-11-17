"""Clase creada para descargar datos de Hugging Face y pasarlos a pandas DataFrame.
Actividad 1 - Estudiante de Ingenieria
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal
from datasets import load_dataset
import pandas as pd

TipoArchivo = Literal["csv", "json", "parquet", "xlsx"]


class HFDatasetLoader:
    """Esta clase nos ayuda a conectarnos con Hugging Face.
    
    Nos permite elegir el dataset que queremos, el split (por ejemplo train),
    limitar la cantidad de filas si no queremos descargar todo, y devolver
    un DataFrame de pandas listo para trabajar.
    """

    _TIPOS_SOPORTADOS = {"csv", "json", "parquet", "xlsx"}

    def __init__(
        self,
        dataset_name: str,
        config: str | None = None,
        split: str = "train",
        token: str | None = None,
        cache_dir: str | None = None,
        max_rows: int | None = None,
        filename: str | Path | None = None,
        file_type: str | None = None,
        streaming: bool = False,
    ) -> None:
        # Guardamos los parametros que nos pasan al crear el objeto
        self.dataset_name = dataset_name
        self.config = config
        self.split = split
        self.token = token
        self.cache_dir = cache_dir
        self.max_rows = max_rows
        self.filename = Path(filename) if filename is not None else None
        self.file_type = self._normalizar_tipo_archivo(file_type)
        self.streaming = streaming
        self.df: pd.DataFrame | None = None

        # Pequeñas validaciones para evitar errores comunes
        if self.max_rows is not None and self.max_rows < 0:
            raise ValueError("max_rows debe ser un número mayor o igual a cero.")
        if self.file_type is not None and self.filename is None:
            raise ValueError("Si indicas file_type tambien debes poner un filename.")

    def load(self) -> pd.DataFrame:
        """Descarga los datos de Hugging Face y los convierte a un DataFrame de pandas."""
        if self.streaming:
            # Modo streaming: util si el dataset es muy grande y solo queremos ver unas filas
            dataset = load_dataset(
                self.dataset_name,
                self.config,
                split=self.split,
                token=self.token,
                streaming=True,
            )
            limite = self.max_rows if self.max_rows is not None else 1000
            filas = list(dataset.take(limite))
            self.df = pd.DataFrame(filas)
        else:
            # Modo normal: descargamos el split indicado
            dataset = load_dataset(
                self.dataset_name,
                self.config,
                split=self.split,
                token=self.token,
                cache_dir=self.cache_dir,
            )
            # Si pedimos un limite de filas, recortamos el dataset
            if self.max_rows is not None:
                dataset = dataset.select(range(min(self.max_rows, len(dataset))))
            self.df = dataset.to_pandas()

        # Si el usuario pidio guardar una copia directa en archivo, la guardamos
        if self.filename is not None:
            self._guardar(self.df)

        return self.df

    def info(self) -> dict[str, str | int | None]:
        """Nos devuelve un resumen rapido de lo que cargamos."""
        if self.df is None:
            raise RuntimeError("Primero debes ejecutar el metodo load() para cargar los datos.")
        return {
            "dataset": self.dataset_name,
            "config": self.config,
            "split": self.split,
            "filas": len(self.df),
            "columnas": len(self.df.columns),
        }

    @classmethod
    def _normalizar_tipo_archivo(cls, file_type: str | None) -> str | None:
        """Funcion de apoyo para verificar el formato de guardado."""
        if file_type is None:
            return None
        normalizado = file_type.lower().lstrip(".")
        if normalizado == "excel":
            normalizado = "xlsx"
        if normalizado not in cls._TIPOS_SOPORTADOS:
            formatos = ", ".join(sorted(cls._TIPOS_SOPORTADOS))
            raise ValueError(f"Formato no soportado: {file_type}. Formatos validos: {formatos}.")
        return normalizado

    def _guardar(self, df: pd.DataFrame) -> None:
        """Guarda el DataFrame en disco segun el tipo indicado."""
        assert self.filename is not None
        tipo = self.file_type or self._normalizar_tipo_archivo(self.filename.suffix)
        if tipo is None:
            raise ValueError("No se pudo detectar el tipo de archivo. Agrega la extension al nombre.")

        self.filename.parent.mkdir(parents=True, exist_ok=True)
        if tipo == "csv":
            df.to_csv(self.filename, index=False)
        elif tipo == "json":
            df.to_json(self.filename, orient="records", force_ascii=False)
        elif tipo == "parquet":
            df.to_parquet(self.filename, index=False)
        elif tipo == "xlsx":
            df.to_excel(self.filename, index=False)
