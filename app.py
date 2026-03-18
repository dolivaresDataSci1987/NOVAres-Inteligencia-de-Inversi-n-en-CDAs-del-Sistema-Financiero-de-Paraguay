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
# ESTILOS
# =========================
st.markdown(
    """
    <style>
        .main-header-card {
            background: linear-gradient(135deg, #1b1235 0%, #2a174a 55%, #34195a 100%);
            padding: 1.4rem 1.6rem 1.2rem 1.6rem;
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1.2rem;
            box-shadow: 0 6px 24px rgba(0,0,0,0.18);
        }

        .beta-badge {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            background-color: rgba(255,255,255,0.10);
            color: #ffffff;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.4px;
            margin-bottom: 0.8rem;
        }

        .main-title {
            color: white;
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0 0 0.2rem 0;
            line-height: 1.1;
        }

        .main-subtitle {
            color: rgba(255,255,255,0.92);
            font-size: 1.15rem;
            margin: 0.2rem 0 0.7rem 0;
            font-weight: 500;
        }

        .main-description {
            color: rgba(255,255,255,0.86);
            font-size: 1rem;
            margin-top: 0.4rem;
            line-height: 1.6;
        }

        .ownership-note {
            color: rgba(255,255,255,0.78);
            font-size: 0.88rem;
            margin-top: 1rem;
        }

        .logo-wrap img {
            max-width: 100%;
            border-radius: 10px;
        }

        .block-container {
            padding-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER
# =========================
logo_path = Path("logo.png")
if not logo_path.exists():
    logo_path = Path("assets/logo.png")

col1, col2 = st.columns([1.1, 2.5])

with col1:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)

with col2:
    st.markdown(
        """
        <div class="main-header-card">
            <div class="beta-badge">VERSIÓN BETA · 2026</div>
            <div class="main-title">NOVAres | Inteligencia de Inversión en CDAs</div>
            <div class="main-subtitle">Sistema financiero paraguayo</div>
            <div class="main-description">
                Plataforma analítica para explorar oportunidades de inversión en CDAs desde una lectura integrada de
                <b>rentabilidad, riesgo, liquidez, accesibilidad y contexto de mercado</b>.
            </div>
            <div class="ownership-note">
                Propiedad de David Olivares by NOVAres (2026)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

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
st.sidebar.image(str(logo_path), use_container_width=True) if logo_path.exists() else None
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
