import streamlit as st
import pandas as pd

from utils.load_data import (
    cargar_datos_cda,
    cargar_comparativa_internacional,
    cargar_diccionario,
)
from utils.metrics import (
    calcular_kpis_generales,
    obtener_mejores_por_dimension,
    calcular_resumen_tipo,
    calcular_resumen_moneda,
)
from utils.insights import generar_insight_overview, generar_insight_macro
from utils.charts import (
    grafico_distribucion_tasas,
    grafico_score_por_tipo,
    grafico_riesgo_retorno,
    grafico_tasa_real_por_pais,
    grafico_resumen_regional,
    grafico_conteo_categoria,
)

st.set_page_config(
    page_title="NOVAresDashboard",
    page_icon="📈",
    layout="wide"
)

st.title("NOVAresDashboard")
st.markdown("### Inteligencia de Inversión en CDAs del sistema financiero paraguayo")

st.markdown(
    """
    Plataforma analítica para explorar oportunidades de inversión en CDAs desde una lectura de
    **rentabilidad, riesgo, liquidez, accesibilidad y contexto macrofinanciero**.
    """
)

# =========================
# CARGA
# =========================
df = cargar_datos_cda()
df_int = cargar_comparativa_internacional()
df_dict = cargar_diccionario()

if df.empty:
    st.warning("No se pudo cargar la base principal de CDAs.")
    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("NOVAresDashboard")
st.sidebar.markdown("**Panel ejecutivo**")
st.sidebar.markdown("---")
st.sidebar.info(
    "Usa las páginas laterales para profundizar en overview, ranking, comparador, "
    "riesgo-retorno y contexto macro."
)

# =========================
# KPIS PRINCIPALES
# =========================
kpis = calcular_kpis_generales(df)

st.subheader("KPIs principales")

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

col1.metric("Registros", f"{kpis.get('registros', 0)}")
col2.metric("Entidades", f"{kpis.get('entidades', 0)}")
col3.metric(
    "Tasa nominal promedio",
    f"{kpis.get('tasa_nominal_promedio', float('nan')):.2f}%"
    if pd.notna(kpis.get("tasa_nominal_promedio")) else "N/D"
)
col4.metric(
    "Tasa nominal máxima",
    f"{kpis.get('tasa_nominal_maxima', float('nan')):.2f}%"
    if pd.notna(kpis.get("tasa_nominal_maxima")) else "N/D"
)

col5.metric(
    "Tasa real promedio",
    f"{kpis.get('tasa_real_promedio', float('nan')):.2f}%"
    if pd.notna(kpis.get("tasa_real_promedio")) else "N/D"
)
col6.metric(
    "Score balanceado promedio",
    f"{kpis.get('score_balanceado_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("score_balanceado_promedio")) else "N/D"
)
col7.metric(
    "% con tasa real positiva",
    f"{kpis.get('pct_tasa_real_positiva', float('nan')):.1f}%"
    if pd.notna(kpis.get("pct_tasa_real_positiva")) else "N/D"
)
col8.metric(
    "% garantizados",
    f"{kpis.get('pct_garantizados', float('nan')):.1f}%"
    if pd.notna(kpis.get("pct_garantizados")) else "N/D"
)

st.markdown("---")

# =========================
# INSIGHTS EJECUTIVOS
# =========================
st.subheader("Lectura ejecutiva")

insight_local = generar_insight_overview(df)
st.info(insight_local)

if not df_int.empty:
    insight_macro = generar_insight_macro(df_int)
    st.info(insight_macro)

st.markdown("---")

# =========================
# MEJORES OPORTUNIDADES
# =========================
st.subheader("Mejores oportunidades destacadas")

tops = obtener_mejores_por_dimension(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    top = tops.get("mejor_balanceado")
    if top is not None:
        st.markdown("### Mejor equilibrio general")
        st.write(f"**Entidad:** {top.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top.get('instrument_name', 'N/D')}")
        st.write(f"**Score balanceado:** {top.get('final_score_balanced', float('nan')):.2f}")
        st.write(f"**Tasa real:** {top.get('real_rate_pct', float('nan')):.2f}%")

with col2:
    top = tops.get("mejor_conservador")
    if top is not None:
        st.markdown("### Mejor perfil conservador")
        st.write(f"**Entidad:** {top.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top.get('instrument_name', 'N/D')}")
        st.write(f"**Score conservador:** {top.get('final_score_conservative', float('nan')):.2f}")
        st.write(f"**Riesgo:** {top.get('risk_score', float('nan')):.2f}")

with col3:
    top = tops.get("mejor_agresivo")
    if top is not None:
        st.markdown("### Mejor perfil agresivo")
        st.write(f"**Entidad:** {top.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top.get('instrument_name', 'N/D')}")
        st.write(f"**Score agresivo:** {top.get('final_score_aggressive', float('nan')):.2f}")
        st.write(f"**Tasa nominal:** {top.get('rate_nominal_pct', float('nan')):.2f}%")

with col4:
    top = tops.get("menor_riesgo")
    if top is not None:
        st.markdown("### Menor riesgo")
        st.write(f"**Entidad:** {top.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top.get('instrument_name', 'N/D')}")
        st.write(f"**Riesgo:** {top.get('risk_score', float('nan')):.2f}")
        st.write(f"**Tasa real:** {top.get('real_rate_pct', float('nan')):.2f}%")

st.markdown("---")

# =========================
# VISUALES PRINCIPALES
# =========================
st.subheader("Vista rápida del mercado")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_distribucion_tasas(
        df,
        col="rate_nominal_pct",
        titulo="Distribución de tasas nominales",
        color_col="currency_code"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_score_por_tipo(
        df,
        tipo_col="entity_type",
        score_col="final_score_balanced",
        titulo="Score balanceado promedio por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

fig_rr = grafico_riesgo_retorno(
    df,
    x_col="risk_score",
    y_col="real_rate_pct",
    color_col="entity_type",
    size_col="final_score_balanced",
    hover_name="entity_name",
    titulo="Mapa riesgo vs retorno real"
)
if fig_rr is not None:
    st.plotly_chart(fig_rr, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = grafico_conteo_categoria(
        df,
        categoria_col="currency_code",
        titulo="Distribución por moneda"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = grafico_conteo_categoria(
        df,
        categoria_col="term_profile",
        titulo="Distribución por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# RESÚMENES
# =========================
st.subheader("Resúmenes del mercado")

resumen_tipo = calcular_resumen_tipo(df)
resumen_moneda = calcular_resumen_moneda(df)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Resumen por tipo de entidad")
    if not resumen_tipo.empty:
        st.dataframe(resumen_tipo, use_container_width=True)

with col2:
    st.markdown("### Resumen por moneda")
    if not resumen_moneda.empty:
        st.dataframe(resumen_moneda, use_container_width=True)

st.markdown("---")

# =========================
# CONTEXTO INTERNACIONAL
# =========================
if not df_int.empty:
    st.subheader("Contexto internacional")

    col1, col2 = st.columns(2)

    with col1:
        fig = grafico_tasa_real_por_pais(
            df_int,
            country_col="country",
            valor_col="real_rate_proxy_pct",
            top_n=15,
            titulo="Comparativa internacional por tasa real proxy"
        )
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = grafico_resumen_regional(
            df_int,
            region_col="region",
            valor_col="real_rate_proxy_pct",
            titulo="Promedio regional de tasa real proxy"
        )
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# METODOLOGÍA
# =========================
st.subheader("Soporte metodológico")

with st.expander("Ver diccionario de variables"):
    st.dataframe(df_dict, use_container_width=True)

st.caption("Desarrollado por NOVAres · 2026")
