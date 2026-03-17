import streamlit as st
import pandas as pd

from utils.load_data import (
    cargar_datos_cda,
    cargar_comparativa_internacional,
    cargar_diccionario,
)

st.set_page_config(
    page_title="NOVAres · Inteligencia de Inversión en CDAs",
    page_icon="📈",
    layout="wide"
)

# =========================
# CARGA DE DATOS
# =========================
df = cargar_datos_cda()
df_int = cargar_comparativa_internacional()
df_dict = cargar_diccionario()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("NOVAres")
st.sidebar.markdown("**Inteligencia de Inversión en CDAs**")
st.sidebar.markdown("---")
st.sidebar.info(
    "Dashboard analítico para explorar oportunidades de inversión "
    "en Certificados de Depósito de Ahorro (CDAs) del sistema financiero paraguayo."
)

# =========================
# CABECERA
# =========================
st.title("NOVAres · Inteligencia de Inversión en CDAs del sistema financiero paraguayo")
st.markdown(
    """
    Este dashboard permite analizar la oferta de CDAs en Paraguay desde una perspectiva
    de **rentabilidad, riesgo, accesibilidad y contexto macrofinanciero**.
    """
)

# =========================
# KPIs PRINCIPALES
# =========================
total_entidades = df["entity_name"].nunique()
tasa_promedio = df["rate_nominal_pct"].mean()
tasa_maxima = df["rate_nominal_pct"].max()
score_promedio = df["final_score_balanced"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Entidades analizadas", f"{total_entidades}")
col2.metric("Tasa nominal promedio", f"{tasa_promedio:.2f}%")
col3.metric("Tasa nominal máxima", f"{tasa_maxima:.2f}%")
col4.metric("Score balanceado promedio", f"{score_promedio:.2f}")

st.markdown("---")

# =========================
# RESUMEN EJECUTIVO
# =========================
st.subheader("Resumen ejecutivo")

top_balanced = df.sort_values("final_score_balanced", ascending=False).iloc[0]
top_conservative = df.sort_values("final_score_conservative", ascending=False).iloc[0]
top_aggressive = df.sort_values("final_score_aggressive", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Mejor opción balanceada")
    st.write(f"**Entidad:** {top_balanced['entity_name']}")
    st.write(f"**Instrumento:** {top_balanced['instrument_name']}")
    st.write(f"**Tasa nominal:** {top_balanced['rate_nominal_pct']:.2f}%")
    st.write(f"**Score balanceado:** {top_balanced['final_score_balanced']:.2f}")

with col2:
    st.markdown("### Mejor opción conservadora")
    st.write(f"**Entidad:** {top_conservative['entity_name']}")
    st.write(f"**Instrumento:** {top_conservative['instrument_name']}")
    st.write(f"**Tasa nominal:** {top_conservative['rate_nominal_pct']:.2f}%")
    st.write(f"**Score conservador:** {top_conservative['final_score_conservative']:.2f}")

with col3:
    st.markdown("### Mejor opción agresiva")
    st.write(f"**Entidad:** {top_aggressive['entity_name']}")
    st.write(f"**Instrumento:** {top_aggressive['instrument_name']}")
    st.write(f"**Tasa nominal:** {top_aggressive['rate_nominal_pct']:.2f}%")
    st.write(f"**Score agresivo:** {top_aggressive['final_score_aggressive']:.2f}")

st.markdown("---")

# =========================
# CONTEXTO GENERAL
# =========================
st.subheader("Cobertura del dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Base local")
    st.write(
        "La base principal incluye información de tasas, perfiles de plazo, "
        "riesgo, liquidez, solvencia, accesibilidad y scores finales para CDAs "
        "del mercado paraguayo."
    )

with col2:
    st.markdown("### Comparativa internacional")
    st.write(
        "La base internacional permite situar a Paraguay frente a otros países "
        "en términos de tasa benchmark, inflación, tasa real proxy y protección de depósitos."
    )

st.markdown("---")

# =========================
# DICCIONARIO DE VARIABLES
# =========================
with st.expander("Ver diccionario básico de variables"):
    st.dataframe(df_dict, use_container_width=True)

st.caption("Desarrollado por NOVAres · 2026")
