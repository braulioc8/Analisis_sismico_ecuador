import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_access import SeismicDAO
from service_layer import SeismicService

# Aero-Technical Aesthetics
SOIL_COLORS = {"A":"#1E3A8A", "B":"#3B82F6", "C":"#10B981", "D":"#F59E0B", "E":"#F97316", "F":"#EF4444"}
ST_STYLE = """
<style>
    .main { background-color: #F8FAFC; }
    .stMetric { background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; }
    h1, h2, h3 { color: #1E293B; font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #F1F5F9; border-radius: 4px 4px 0 0; padding: 10px 20px; }
    .formula-text { color: #64748B; font-size: 0.85em; margin-top: -10px; margin-bottom: 10px; }
    .q-indicator { color: #3B82F6; font-size: 0.9em; font-weight: bold; margin-bottom: 15px; }
</style>
"""

def main():
    st.set_page_config(page_title="Analisis Sismico Pro", layout="wide", initial_sidebar_state="expanded")
    st.markdown(ST_STYLE, unsafe_allow_html=True)

    # Sidebar: Control Panel
    st.sidebar.title("PANEL DE CONTROL")
    
    dao = SeismicDAO()
    service = SeismicService()

    @st.cache_data
    def get_data_ready():
        raw_df = dao.load_all()
        return service.enriquecer_dataset(raw_df)

    try:
        full_data = get_data_ready()
        
        # Chronological Filters
        st.sidebar.subheader("RANGO TEMPORAL")
        min_date, max_date = full_data['time_value'].min().date(), full_data['time_value'].max().date()
        start_date = st.sidebar.date_input("INICIO", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("FIN", value=max_date, min_value=min_date, max_value=max_date)
        
        st.sidebar.markdown("---")
        
        # Dimensions Filters
        st.sidebar.subheader("DIMENSIONES")
        zona_selected = st.sidebar.multiselect("ZONAS SISMICAS", options=sorted(full_data['Zona_Sismica'].unique()), default=full_data['Zona_Sismica'].unique())
        suelo_selected = st.sidebar.multiselect("TIPOS DE SUELO", options=["A", "B", "C", "D", "E", "F"], default=["A", "B", "C", "D", "E", "F"])
        m_types_selected = st.sidebar.multiselect("TIPOS DE MAGNITUD", options=sorted(full_data['magnitude_type'].unique()), default=full_data['magnitude_type'].unique())
        map_opacity = st.sidebar.slider("OPACIDAD DE CAPAS", 0.1, 1.0, 0.6)

        filtered_data = service.filtrar_datos(full_data, zona_selected, suelo_selected, m_types_selected, start_date, end_date)

        if filtered_data.empty:
            st.warning("No hay datos que coincidan con los filtros actuales.")
            st.stop()

        # Dashboard Header
        st.title("SISTEMA DE ANALISIS SISMICO | NEC-15")
        st.caption("Fuente de datos: IGEPN Ecuador. Modelado estadistico para evaluacion estructural.")

        # KPI Layer
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("TOTAL DE EVENTOS", f"{len(filtered_data):,}")
        kpi2.metric("MAGNITUD PROMEDIO", f"{filtered_data['magnitude_value'].mean():.2f} Mw")
        kpi3.metric("PROFUNDIDAD MAXIMA", f"{filtered_data['depth_value'].max():.1f} km")
        kpi4.metric("SUELO CRITICO", filtered_data['Tipo_Suelo'].mode()[0])

        st.markdown("---")

        # Modular Tabs
        tab_stat, tab_spatial, tab_eng = st.tabs(["ESTADO ESTADISTICO", "DESCUBRIMIENTO ESPACIAL", "MODELOS DE INGENIERIA"])

        with tab_stat:
            st.subheader("Distribucion de Magnitudes y Probabilidad Mensual")
            st.markdown('<p class="q-indicator">Sirve a la interpretacion de: Pregunta 1 y Pregunta 2</p>', unsafe_allow_html=True)
            
            col_s1, col_s2 = st.columns([2, 1])
            
            with col_s1:
                st.markdown('<p class="formula-text">Estadistica Descriptiva: Evaluacion de Asimetria, Curtosis y Tendencia Central (Pregunta 1)</p>', unsafe_allow_html=True)
                fig_hist = px.histogram(filtered_data, x="magnitude_value", nbins=30, marginal="box", 
                                       title="Distribucion de Intensidad (Mw)", color_discrete_sequence=["#3B82F6"])
                fig_hist.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col_s2:
                stats = service.obtener_estadisticas_magnitud(filtered_data['magnitude_value'])
                st.markdown("**Metricas Descriptivas**")
                st.json({k: f"{v:.4f}" for k, v in stats.items()})

            st.markdown("---")
            prob_q2, tot_m, mes_ev, df_m = service.calcular_probabilidad_mensual(filtered_data)
            
            st.markdown('<p class="formula-text">Probabilidad Relativa (Pregunta 2): P(A) = n(A) / N, donde n(A) son meses con eventos > 4.0 y N el total de meses.</p>', unsafe_allow_html=True)
            col_p1, col_p2 = st.columns([1, 2])
            with col_p1:
                st.metric("PROBABILIDAD MENSUAL (Mw > 4.0)", f"{prob_q2*100:.2f}%")
                st.caption(f"Basado en {mes_ev} meses activos sobre {tot_m} analizados.")
            with col_p2:
                fig_ts = px.line(df_m, x='mes_anio', y='frecuencia', title="Tendencia de Frecuencia Mensual", color_discrete_sequence=["#10B981"])
                fig_ts.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_ts, use_container_width=True)

        with tab_spatial:
            st.subheader("Descubrimiento Geoespacial y Densidad")
            st.markdown('<p class="q-indicator">Sirve a la interpretacion de: Contexto General y Ubicacion (NEC-15)</p>', unsafe_allow_html=True)
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                fig_heat = px.density_mapbox(filtered_data, lat='latitude_value', lon='longitude_value', z='magnitude_value', radius=8, 
                                            center=dict(lat=-1.5, lon=-78.5), zoom=5, mapbox_style="carto-positron", title="Mapa de Densidad de Energia")
                fig_heat.update_traces(opacity=map_opacity)
                fig_heat.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_heat, use_container_width=True)
            with m_col2:
                fig_map = px.scatter_mapbox(filtered_data, lat="latitude_value", lon="longitude_value", color="Tipo_Suelo", size="magnitude_size", 
                                           color_discrete_map=SOIL_COLORS, zoom=5, mapbox_style="carto-positron", title="Localizacion por Tipo de Suelo")
                fig_map.update_traces(marker=dict(opacity=map_opacity))
                fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_map, use_container_width=True)

        with tab_eng:
            st.subheader("Influencia Estructural y Curvas de Fragilidad (NEC-15)")
            st.markdown('<p class="q-indicator">Sirve a la interpretacion de: Pregunta 3 y Pregunta 4</p>', unsafe_allow_html=True)
            eng_col1, eng_col2 = st.columns([1, 1])
            
            with eng_col1:
                st.markdown("**Comparativa de Espectros de Diseño**")
                st.markdown('<p class="formula-text">Aceleracion (Pregunta 3): Sa = Z * I * Fa (Amplificacion segun tipo de suelo).</p>', unsafe_allow_html=True)
                s_comp = st.multiselect("Comparar suelos:", ["A", "B", "C", "D", "E", "F"], default=["A", "C", "E"])
                fig_spec = go.Figure()
                for s in s_comp:
                    t, sa = service.obtener_espectro_diseno(s)
                    fig_spec.add_trace(go.Scatter(x=t, y=sa, mode='lines', name=f'Suelo {s}', line=dict(color=SOIL_COLORS[s], width=2)))
                fig_spec.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), xaxis_title="Periodo (s)", yaxis_title="Sa (g)")
                st.plotly_chart(fig_spec, use_container_width=True)
            
            with eng_col2:
                st.markdown("**Matriz de Correlacion y Regresion Multiple**")
                st.markdown('<p class="formula-text">Modelo Lineal (Pregunta 3): Y = &beta;0 + &beta;1(S) + &beta;2(D) + &epsilon;</p>', unsafe_allow_html=True)
                soil_map_num = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}
                corr_df = filtered_data[['magnitude_value', 'depth_value']].copy()
                corr_df['Rango_Suelo'] = filtered_data['Tipo_Suelo'].map(soil_map_num)
                fig_corr = px.imshow(corr_df.corr(), text_auto=".2f", color_continuous_scale='Blues')
                fig_corr.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_corr, use_container_width=True)

            st.markdown("---")
            st.subheader("Simulador de Escenarios (Regresion Logistica)")
            st.markdown('<p class="formula-text">Probabilidad de Falla (Pregunta 4): P(falla) = 1 / (1 + e^(-z)) donde z = &beta;0 + &beta;1(M) + &beta;2(D) + &beta;3(S)</p>', unsafe_allow_html=True)
            
            sim_col1, sim_col2 = st.columns([1, 2])
            with sim_col1:
                in_mag = st.slider("Magnitud", 2.0, 9.0, 6.5)
                in_depth = st.number_input("Profundidad (km)", 0.0, 200.0, 15.0)
                in_soil = st.selectbox("Suelo del Sitio", ["A", "B", "C", "D", "E", "F"], index=4)
                prob = service.estimar_probabilidad_falla(in_mag, in_depth, in_soil)
                st.metric("RIESGO DE FALLA", f"{prob*100:.1f}%")
                st.progress(prob)
            with sim_col2:
                mags = np.linspace(2.0, 9.0, 50)
                df_c = pd.DataFrame([{ "M": m, "P": service.estimar_probabilidad_falla(m, in_depth, s), "S": s } for s in ["A", "C", "E", "F"] for m in mags])
                fig_c = px.line(df_c, x="M", y="P", color="S", color_discrete_map=SOIL_COLORS, title="Curvas de Fragilidad Comparativas")
                fig_c.add_trace(go.Scatter(x=[in_mag], y=[prob], mode="markers", marker=dict(color="#000", size=12, symbol="x"), name="Escenario"))
                fig_c.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_c, use_container_width=True)

    except Exception as e:
        st.error(f"ERROR DE SISTEMA: {e}")

if __name__ == "__main__":
    main()
