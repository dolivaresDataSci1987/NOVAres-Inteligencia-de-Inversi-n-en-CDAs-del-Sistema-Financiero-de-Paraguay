import streamlit as st
import pandas as pd
from pathlib import Path

from utils.load_data import (
    cargar_datos_cda,
    cargar_comparativa_internacional,
    cargar_diccionario,
)
from utils.metrics import (
    calcular_kpis_generales,
    obtener_mejores_por_dimension,
)
from utils.insights import generar_insight_overview, generar_insight_macro

st.set_page_config(
    page_title="NOVAres | CDAs Paraguay",
    page_icon="📈",
    layout="wide"
)

# =========================
# RUTA LOGO
# =========================
logo_path = Path("logo.png")
if not logo_path.exists():
    logo_path = Path("assets/logo.png")

# =========================
# ESTILOS GENERALES
# =========================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 1.5rem;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.07);
            padding: 0.9rem 1rem;
            border-radius: 14px;
        }

        div[data-testid="stExpander"] {
            border-radius: 14px;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER PRINCIPAL
# =========================
with st.container(border=True):
    st.caption("VERSIÓN BETA · 2026")
    st.title("NOVAres | Inteligencia de Inversión en CDAs")
    st.subheader("Sistema financiero paraguayo")
    st.markdown(
        "Plataforma analítica para explorar oportunidades de inversión en CDAs "
        "desde una lectura integrada de **rentabilidad, riesgo, liquidez, "
        "accesibilidad y contexto de mercado**."
    )
    st.caption("Propiedad de David Olivares by NOVAres (2026)")
    st.warning(
    """
    **AVISO:** Este dashboard tiene fines exclusivamente **informativos, analíticos y educativos**. **No constituye asesoramiento financiero, recomendación de inversión ni sustituye la evaluación profesional personalizada.**
Los datos mostrados se basan en información recopilada y procesada bajo una metodología propia de análisis. Algunas variables —como la **tasa nominal, tasa efectiva, plazo, monto mínimo u otras condiciones comerciales**—
    pueden **variar ligeramente** respecto a la oferta final vigente de cada entidad financiera en el momento de la contratación.
 Esto se debe a que las condiciones de los CDAs pueden ser **dinámicas**, estar sujetas a **actualizaciones comerciales**,
    cambios de mercado y, en algunos casos, a **negociación según el perfil del cliente, el monto invertido o el plazo pactado**.
 Antes de tomar una decisión de inversión, conviene **confirmar directamente con la entidad** las condiciones finales aplicables.
    """
)

st.markdown("")

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
if logo_path.exists():
    st.sidebar.image(str(logo_path), use_container_width=True)

st.sidebar.title("NOVAres | CDAs Paraguay")
st.sidebar.caption("Versión beta")
st.sidebar.markdown("**Panel ejecutivo**")
st.sidebar.markdown("---")
st.sidebar.info(
    "Usa las páginas laterales para profundizar en visión general, análisis regional, "
    "ranking, comparador de CDAs y análisis de riesgo."
)
st.sidebar.markdown("---")
st.sidebar.caption("Propiedad de David Olivares by NOVAres (2026)")

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

st.info(generar_insight_overview(df))

if not df_int.empty:
    st.info(generar_insight_macro(df_int))

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
# METODOLOGÍA
# =========================
st.subheader("Soporte metodológico")

with st.expander("Ver diccionario de variables"):
    st.dataframe(df_dict, use_container_width=True)

st.caption("Versión beta · Propiedad de David Olivares by NOVAres (2026)")
