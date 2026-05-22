import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.stats import skew, kurtosis

def clasificar_suelo_nec(row):
    if row['depth_value'] > 50: return 'A'
    elif row['depth_value'] > 30: return 'B'
    elif row['depth_value'] > 15: return 'C'
    elif row['depth_value'] > 5: return 'D'
    elif row['magnitude_value'] > 6.0 and row['depth_value'] < 10: return 'F'
    else: return 'E'

def asignar_zona_sismica(lat):
    if lat > 0: return 'Zona VI (Z=0.50)'
    if lat > -1: return 'Zona IV (Z=0.35)'
    return 'Zona II (Z=0.25)'

def calcular_probabilidad_falla(mag, depth, soil_type):
    beta0, beta1, beta2 = -4.5, 0.85, -0.04
    soil_impact = {'A': 0.0, 'B': 0.2, 'C': 0.5, 'D': 0.8, 'E': 1.2, 'F': 1.8}
    z = beta0 + (beta1 * mag) + (beta2 * depth) + soil_impact.get(soil_type, 1.0)
    return 1 / (1 + np.exp(-z))

def realizar_regresion_lineal(df):
    soil_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}
    df_reg = df.copy()
    df_reg['S_num'] = df_reg['Tipo_Suelo'].map(soil_map)
    X = df_reg[['S_num', 'depth_value']]
    y = (df_reg['magnitude_value'] * 0.5) + (df_reg['S_num'] * 0.3) - (df_reg['depth_value'] * 0.02)
    model = LinearRegression()
    model.fit(X, y)
    return model.coef_, model.score(X, y)

def generar_espectro_nec(soil_type, z_factor=0.4):
    fa_map = {'A': 1.0, 'B': 1.1, 'C': 1.3, 'D': 1.5, 'E': 1.8, 'F': 2.2}
    fa = fa_map.get(soil_type, 1.5)
    periodos = np.linspace(0.01, 3.0, 100)
    aceleraciones = []
    tc = 0.5 * fa
    for t in periodos:
        if t <= tc:
            sa = z_factor * fa * 2.5
        else:
            sa = z_factor * fa * 2.5 * (tc / t)
        aceleraciones.append(sa)
    return periodos, aceleraciones

def calcular_medidas_descriptivas(series):
    """Calcula medidas de tendencia central, dispersion y forma."""
    stats = {
        "Media": series.mean(),
        "Mediana": series.median(),
        "Rango": series.max() - series.min(),
        "Varianza": series.var(),
        "Desviacion Estandar": series.std(),
        "Coeficiente Asimetria": skew(series.dropna()),
        "Coeficiente Apuntamiento": kurtosis(series.dropna())
    }
    return stats
