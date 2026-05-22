import pandas as pd
import os
import sys

class SeismicDAO:
    """
    Data Access Object para el dataset sismico.
    Encargado exclusivamente de la lectura de datos crudos desde el origen persistente.
    """
    def __init__(self):
        self.csv_path = self._get_resource_path('dataset_seismico_final.csv')

    def _get_resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_all(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Dataset no encontrado en: {self.csv_path}")
        return pd.read_csv(self.csv_path)
