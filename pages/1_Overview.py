import streamlit as st
import pandas as pd

from utils.load_data import (
    cargar_datos_cda,
    cargar_comparativa_internacional,
    filtrar_datos,
)

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.title("Overview del mercado de CDAs")
st.markdown("Vista general del mercado de CDAs en Paraguay y su contexto comparado.")

# =========================
# CARGA DE DATOS
# =========================
df = cargar_datos_cda()
df_int = cargar_comparativa_internacional()

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

monedas = st.sidebar.multiselect(
    "Moneda",
    options=sorted(df["currency_code"].dropna().unique()),
    default=sorted(df["currency_code"].dropna().unique())
)

tipos_entidad = st.sidebar.multiselect(
    "Tipo de entidad",
    options=sorted(df["entity_type"].dropna().unique()),
    default=sorted(df["entity_type"].dropna().unique())
)

perfiles_plazo = st.sidebar.multiselect(
    "Perfil de plazo",
    options=sorted(df["term_profile"].dropna().unique()),
    default=sorted(df["term_profile"].dropna().unique())
)

df_f = filtrar_datos(
    df,
    monedas=monedas,
    tipos_entidad=tipos_entidad,
    perfiles_plazo=perfiles_plazo
)

# =========================
# 1. COMPARATIVA INTERNACIONAL
# =========================
st.subheader("Comparativa del mercado paraguayo frente a otros mercados y regiones")

st.markdown(
    """
    Esta sección sitúa a Paraguay en contexto frente a otros mercados a partir de una
    comparación de tasa benchmark, inflación, tasa real proxy y cobertura de depósitos.
    """
)

if not df_int.empty:
    df_int = df_int.copy()

    # Tabla resumida para mostrar
    columnas_comp = [
        "country",
        "region",
        "benchmark_rate_pct",
        "inflation_yoy_pct",
        "real_rate_proxy_pct",
        "policy_rate_pct",
        "market_risk_tier",
        "deposit_protection_scheme",
        "deposit_guarantee_limit",
        "rank_by_real_rate_proxy",
    ]
    columnas_comp = [c for c in columnas_comp if c in df_int.columns]

    paraguay_row = df_int[df_int["country"].str.upper() == "PARAGUAY"].copy()

    col1, col2, col3 = st.columns(3)

    if not paraguay_row.empty:
        py = paraguay_row.iloc[0]

        col1.metric(
            "Paraguay · tasa benchmark",
            f"{py['benchmark_rate_pct']:.2f}%"
        )
        col2.metric(
            "Paraguay · inflación interanual",
            f"{py['inflation_yoy_pct']:.2f}%"
        )
        col3.metric(
            "Paraguay · tasa real proxy",
            f"{py['real_rate_proxy_pct']:.2f}%"
        )

        st.info(
            f"**Lectura rápida:** Paraguay aparece con un perfil de riesgo "
            f"**{py['market_risk_tier']}** y ocupa la posición "
            f"**{int(py['rank_by_real_rate_proxy'])}** en la comparativa por tasa real proxy."
        )

    st.dataframe(
        df_int[columnas_comp].sort_values("rank_by_real_rate_proxy", ascending=True),
        use_container_width=True
    )

    st.markdown("### Paraguay frente al promedio regional")

    resumen_region = (
        df_int.groupby("region", as_index=False)
        .agg(
            benchmark_rate_promedio=("benchmark_rate_pct", "mean"),
            inflacion_promedio=("inflation_yoy_pct", "mean"),
            tasa_real_proxy_promedio=("real_rate_proxy_pct", "mean")
        )
        .sort_values("tasa_real_proxy_promedio", ascending=False)
    )

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.dataframe(resumen_region, use_container_width=True)

    with col2:
        if not paraguay_row.empty:
            st.markdown("#### Posicionamiento de Paraguay")
            st.write(
                f"- **Región:** {py['region']}"
            )
            st.write(
                f"- **Tasa benchmark:** {py['benchmark_rate_pct']:.2f}%"
            )
            st.write(
                f"- **Tasa real proxy:** {py['real_rate_proxy_pct']:.2f}%"
            )
            st.write(
                f"- **Esquema de protección:** {py['deposit_protection_scheme']}"
            )
            st.write(
                f"- **Límite de garantía:** {py['deposit_guarantee_limit']}"
            )
            st.write(
                f"- **Comentario relativo:** {py['relative_attractiveness_note']}"
            )

st.markdown("---")

# =========================
# 2. KPIs BÁSICOS DE PARAGUAY
# =========================
st.subheader("KPIs básicos del mercado de CDAs en Paraguay")

total_registros = len(df_f)
total_entidades = df_f["entity_name"].nunique()
tasa_nominal_promedio = df_f["rate_nominal_pct"].mean()
tasa_real_promedio = df_f["real_rate_pct"].mean()
tasa_nominal_max = df_f["rate_nominal_pct"].max()
score_balanceado_promedio = df_f["final_score_balanced"].mean()

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("Registros analizados", f"{total_registros}")
col2.metric("Entidades analizadas", f"{total_entidades}")
col3.metric("Tasa nominal promedio", f"{tasa_nominal_promedio:.2f}%")

col4.metric("Tasa real promedio", f"{tasa_real_promedio:.2f}%")
col5.metric("Tasa nominal máxima", f"{tasa_nominal_max:.2f}%")
col6.metric("Score balanceado promedio", f"{score_balanceado_promedio:.2f}")

st.markdown("---")

# =========================
# 3. ANÁLISIS GENERAL DEL OVERVIEW
# =========================
st.subheader("Tabla resumen del mercado")

columnas_mostrar = [
    "entity_name",
    "entity_type",
    "currency_code",
    "instrument_name",
    "term_profile",
    "term_days_floor",
    "rate_nominal_pct",
    "real_rate_pct",
    "risk_score",
    "liquidity_score",
    "solvency_score",
    "final_score_balanced",
    "recommendation_tag",
]

columnas_mostrar = [col for col in columnas_mostrar if col in df_f.columns]

st.dataframe(
    df_f[columnas_mostrar].sort_values("final_score_balanced", ascending=False),
    use_container_width=True
)

st.markdown("---")

st.subheader("Promedios por tipo de entidad")

resumen_tipo = (
    df_f.groupby("entity_type", as_index=False)
    .agg(
        registros=("entity_name", "count"),
        entidades=("entity_name", "nunique"),
        tasa_nominal_promedio=("rate_nominal_pct", "mean"),
        tasa_real_promedio=("real_rate_pct", "mean"),
        riesgo_promedio=("risk_score", "mean"),
        score_balanceado_promedio=("final_score_balanced", "mean"),
    )
    .sort_values("score_balanceado_promedio", ascending=False)
)

st.dataframe(resumen_tipo, use_container_width=True)

st.markdown("---")

st.subheader("Top 10 oportunidades según score balanceado")

columnas_top = [
    "entity_name",
    "entity_type",
    "currency_code",
    "instrument_name",
    "term_profile",
    "rate_nominal_pct",
    "real_rate_pct",
    "risk_score",
    "final_score_balanced",
    "rank_balanced",
    "recommendation_tag",
]
columnas_top = [c for c in columnas_top if c in df_f.columns]

top10 = (
    df_f.sort_values("final_score_balanced", ascending=False)
    .loc[:, columnas_top]
    .head(10)
)

st.dataframe(top10, use_container_width=True)
