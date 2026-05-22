# Sistema de Analisis Sismico - Normativa NEC-15

Plataforma avanzada de ingenieria estructural diseñada para la evaluacion del impacto de eventos sismicos en el territorio ecuatoriano, bajo los lineamientos de la Norma Ecuatoriana de la Construccion (NEC-15).

## Descripcion General

Este sistema integra datos oficiales del Instituto Geofisico de la Escuela Politecnica Nacional (IGEPN) para realizar modelado estadistico, analisis geoespacial y estimacion de riesgos estructurales. La arquitectura esta diseñada bajo un patron de separacion de capas (DAO/Service) para garantizar robustez y escalabilidad.

## Caracteristicas Tecnicas

| Modulo | Metodologia Aplicada | Objetivo |
| :--- | :--- | :--- |
| **Estadistica Descriptiva** | Medidas de tendencia central y forma | Caracterizacion de la variable Magnitud (Mw). |
| **Analisis Probabilistico** | Probabilidad por frecuencia relativa | Estimacion de recurrencia mensual de sismos > 4.0. |
| **Analisis Geotecnico** | Clasificacion NEC-SE-DS (Perfiles A-F) | Determinacion de la rigidez del sitio y amplificacion. |
| **Modelado Predictivo** | Regresion Lineal y Logistica | Evaluacion de respuesta estructural y probabilidad de falla. |

## Requisitos del Sistema

- Python 3.10 o superior
- Navegador web moderno (Chrome, Edge, Firefox)
- Token de Mapbox (opcional para estilos de mapa avanzados)

## Guia de Instalacion y Ejecucion

### 1. Preparacion del Entorno

Se recomienda el uso de un entorno virtual para aislar las dependencias:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Linux/macOS)
source venv/bin/activate

# Activar entorno (Windows)
venv\Scripts\activate
```

### 2. Instalacion de Dependencias

```bash
pip install -r requirements.txt
```

### 3. Lanzamiento de la Aplicacion

```bash
streamlit run app.py
```

## Estructura del Proyecto

```text
.
├── app.py                # Interfaz de usuario (Streamlit)
├── service_layer.py      # Logica de negocio y calculos de ingenieria
├── data_access.py        # Capa DAO para persistencia de datos
├── utils.py              # Funciones auxiliares y algoritmos NEC-15
├── dataset_seismico_final.csv # Base de datos sismica (IGEPN)
├── LICENSE               # Licencia propietaria y terminos de uso
└── requirements.txt      # Dependencias del sistema
```

## Aviso de Propiedad Intelectual

**Propiedad del Software:** Este sistema y su arquitectura original son propiedad intelectual exclusiva de **Braulio Cajas**.

**Propiedad de los Datos:** Los registros sismicos son propiedad del **Instituto Geofisico de la Escuela Politecnica Nacional (IGEPN)** de Ecuador.

**Restricciones:** Queda prohibida la redistribucion no autorizada o la atribucion de autoria por parte de terceros. Los compañeros de clase tienen permiso de uso y modificacion para fines estrictamente academicos.

---
*Documentacion generada para el repositorio oficial en GitHub.*






























