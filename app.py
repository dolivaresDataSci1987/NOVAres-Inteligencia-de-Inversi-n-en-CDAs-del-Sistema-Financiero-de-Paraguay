import streamlit as st

from utils.load_data import (
    cargar_datos_cda,
    cargar_comparativa_internacional,
    cargar_diccionario,
)

st.set_page_config(
    page_title="NOVAresDashboard",
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
st.sidebar.title("NOVAresDashboard")
st.sidebar.markdown("**Inteligencia de Inversión en CDAs**")
st.sidebar.markdown("---")
st.sidebar.info(
    "Plataforma analítica para explorar oportunidades de inversión "
    "en Certificados de Depósito de Ahorro (CDAs) del sistema financiero paraguayo."
)

# =========================
# CABECERA
# =========================
st.title("NOVAresDashboard")
st.markdown("### Inteligencia de Inversión en CDAs del sistema financiero paraguayo")

st.markdown(
    """
    Este dashboard permite analizar la oferta de CDAs en Paraguay desde una perspectiva de
    **rentabilidad, riesgo, accesibilidad y contexto macrofinanciero**.

    A través de distintas secciones, la plataforma facilita una lectura comparativa del mercado,
    el posicionamiento de las entidades financieras y la evaluación de oportunidades según
    distintos perfiles de inversión.
    """
)

st.markdown("---")

# =========================
# KPIs PRINCIPALES
# =========================
total_entidades = df["entity_name"].nunique() if "entity_name" in df.columns else 0
tasa_promedio = df["rate_nominal_pct"].mean() if "rate_nominal_pct" in df.columns else 0
tasa_maxima = df["rate_nominal_pct"].max() if "rate_nominal_pct" in df.columns else 0
score_promedio = (
    df["final_score_balanced"].mean()
    if "final_score_balanced" in df.columns else 0
)

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

if not df.empty:
    top_balanced = df.sort_values("final_score_balanced", ascending=False).iloc[0]
    top_conservative = df.sort_values("final_score_conservative", ascending=False).iloc[0]
    top_aggressive = df.sort_values("final_score_aggressive", ascending=False).iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Mejor opción balanceada")
        st.write(f"**Entidad:** {top_balanced.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top_balanced.get('instrument_name', 'N/D')}")
        st.write(f"**Tasa nominal:** {top_balanced.get('rate_nominal_pct', 0):.2f}%")
        st.write(f"**Score balanceado:** {top_balanced.get('final_score_balanced', 0):.2f}")

    with col2:
        st.markdown("### Mejor opción conservadora")
        st.write(f"**Entidad:** {top_conservative.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top_conservative.get('instrument_name', 'N/D')}")
        st.write(f"**Tasa nominal:** {top_conservative.get('rate_nominal_pct', 0):.2f}%")
        st.write(f"**Score conservador:** {top_conservative.get('final_score_conservative', 0):.2f}")

    with col3:
        st.markdown("### Mejor opción agresiva")
        st.write(f"**Entidad:** {top_aggressive.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {top_aggressive.get('instrument_name', 'N/D')}")
        st.write(f"**Tasa nominal:** {top_aggressive.get('rate_nominal_pct', 0):.2f}%")
        st.write(f"**Score agresivo:** {top_aggressive.get('final_score_aggressive', 0):.2f}")

st.markdown("---")

# =========================
# COBERTURA DEL DASHBOARD
# =========================
st.subheader("Cobertura del dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Base local")
    st.write(
        "La base principal integra información sobre tasas, perfiles de plazo, "
        "riesgo, liquidez, solvencia, accesibilidad y scores finales para CDAs "
        "del mercado paraguayo."
    )

with col2:
    st.markdown("### Comparativa internacional")
    st.write(
        "La base comparativa internacional permite situar a Paraguay frente a otros países "
        "y regiones en términos de benchmark, inflación, tasa real proxy y esquemas de protección de depósitos."
    )

st.markdown("---")

# =========================
# DICCIONARIO DE VARIABLES
# =========================
st.subheader("Soporte metodológico")

with st.expander("Ver diccionario básico de variables"):
    st.dataframe(df_dict, use_container_width=True)

# =========================
# PIE
# =========================
st.caption("Desarrollado por NOVAres · 2026")
