import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import skew, kurtosis

class SeismicService:
    """
    Service Layer para logica de negocio y calculos de ingenieria.
    Centraliza la inteligencia del sistema y el filtrado de datos de negocio.
    """
    
    @staticmethod
    def enriquecer_dataset(df):
        """Aplica las clasificaciones NEC-15 al dataframe."""
        from utils import clasificar_suelo_nec, asignar_zona_sismica
        
        df = df.copy()
        df['time_value'] = pd.to_datetime(df['time_value'])
        df['Tipo_Suelo'] = df.apply(clasificar_suelo_nec, axis=1)
        df['Zona_Sismica'] = df['latitude_value'].apply(asignar_zona_sismica)
        
        def categorizar_magnitud(m):
            if m < 4.0: return "Menor (< 4.0)"
            if m < 5.0: return "Ligera (4.0 - 4.9)"
            if m < 6.0: return "Moderada (5.0 - 5.9)"
            if m < 7.0: return "Fuerte (6.0 - 6.9)"
            return "Mayor (>= 7.0)"
        
        df['Rango_Magnitud'] = df['magnitude_value'].apply(categorizar_magnitud)
        df['magnitude_size'] = df['magnitude_value'].apply(lambda x: max(0.1, float(x)) if pd.notnull(x) else 0.1)
        return df

    @staticmethod
    def filtrar_datos(df, zones, soils, magnitudes, start_date, end_date):
        """Aplica los filtros de usuario incluyendo rango de fechas."""
        mask = (
            (df['Zona_Sismica'].isin(zones)) & 
            (df['Tipo_Suelo'].isin(soils)) &
            (df['magnitude_type'].isin(magnitudes)) &
            (df['time_value'].dt.date >= start_date) &
            (df['time_value'].dt.date <= end_date)
        )
        return df[mask]

    @staticmethod
    def obtener_estadisticas_magnitud(series):
        return {
            "Media": series.mean(),
            "Mediana": series.median(),
            "Rango": series.max() - series.min(),
            "Varianza": series.var(),
            "Desviacion Estandar": series.std(),
            "Coeficiente Asimetria": skew(series.dropna()),
            "Coeficiente Apuntamiento": kurtosis(series.dropna())
        }

    @staticmethod
    def calcular_probabilidad_mensual(df, umbral_mag=4.0):
        df_ts = df.copy()
        df_ts['mes_anio'] = df_ts['time_value'].dt.to_period('M')
        total_meses = df_ts['mes_anio'].nunique()
        meses_con_evento = df_ts[df_ts['magnitude_value'] > umbral_mag]['mes_anio'].nunique()
        probabilidad = meses_con_evento / total_meses if total_meses > 0 else 0
        conteo_mensual = df_ts[df_ts['magnitude_value'] > umbral_mag].groupby('mes_anio').size().reset_index(name='frecuencia')
        conteo_mensual['mes_anio'] = conteo_mensual['mes_anio'].astype(str)
        return probabilidad, total_meses, meses_con_evento, conteo_mensual

    @staticmethod
    def estimar_probabilidad_falla(mag, depth, soil_type):
        from utils import calcular_probabilidad_falla
        return calcular_probabilidad_falla(mag, depth, soil_type)

    @staticmethod
    def realizar_regresion_suelo(df):
        from utils import realizar_regresion_lineal
        return realizar_regresion_lineal(df)

    @staticmethod
    def obtener_espectro_diseno(soil_type):
        from utils import generar_espectro_nec
        return generar_espectro_nec(soil_type)
