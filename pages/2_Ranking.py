import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda, filtrar_datos

st.set_page_config(page_title="Ranking", page_icon="🏆", layout="wide")

st.title("Ranking de oportunidades")
st.markdown(
    """
    Explora las mejores oportunidades de inversión en CDAs del sistema financiero paraguayo
    según distintos perfiles de inversión.
    """
)

# =========================
# CARGA DE DATOS
# =========================
df = cargar_datos_cda()

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
# SELECTOR DE PERFIL
# =========================
perfil = st.radio(
    "Selecciona el perfil de inversión",
    options=["Conservador", "Balanceado", "Agresivo"],
    horizontal=True
)

if perfil == "Conservador":
    score_col = "final_score_conservative"
    rank_col = "rank_conservative"
    titulo_score = "Score conservador"
elif perfil == "Balanceado":
    score_col = "final_score_balanced"
    rank_col = "rank_balanced"
    titulo_score = "Score balanceado"
else:
    score_col = "final_score_aggressive"
    rank_col = "rank_aggressive"
    titulo_score = "Score agresivo"

# Evitar errores si no hay datos tras filtros
if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

df_rank = df_f.sort_values(score_col, ascending=False).reset_index(drop=True)

# =========================
# BLOQUE DESTACADO
# =========================
st.subheader(f"Mejor oportunidad para perfil {perfil.lower()}")

top = df_rank.iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Entidad", top["entity_name"])
col2.metric("Tasa nominal", f"{top['rate_nominal_pct']:.2f}%")
col3.metric("Tasa real", f"{top['real_rate_pct']:.2f}%")
col4.metric(titulo_score, f"{top[score_col]:.2f}")

st.markdown(
    f"""
    **Instrumento:** {top.get('instrument_name', 'N/D')}  
    **Moneda:** {top.get('currency_code', 'N/D')}  
    **Perfil de plazo:** {top.get('term_profile', 'N/D')}  
    **Recomendación:** {top.get('recommendation_tag', 'N/D')}
    """
)

st.markdown("---")

# =========================
# KPIs DEL RANKING
# =========================
st.subheader("KPIs del ranking filtrado")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros", len(df_rank))
col2.metric("Entidades", df_rank["entity_name"].nunique())
col3.metric("Mejor score", f"{df_rank[score_col].max():.2f}")
col4.metric("Score promedio", f"{df_rank[score_col].mean():.2f}")

st.markdown("---")

# =========================
# TOP 10
# =========================
st.subheader(f"Top 10 oportunidades · Perfil {perfil.lower()}")

columnas_top = [
    rank_col,
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
    score_col,
    "recommendation_tag",
]

columnas_top = [c for c in columnas_top if c in df_rank.columns]

top10 = df_rank.loc[:, columnas_top].head(10)

st.dataframe(top10, use_container_width=True)

st.markdown("---")

# =========================
# TABLA COMPLETA DEL RANKING
# =========================
st.subheader("Tabla completa del ranking")

columnas_tabla = [
    rank_col,
    "entity_name",
    "entity_type",
    "currency_code",
    "instrument_name",
    "term_profile",
    "term_days_floor",
    "min_amount",
    "rate_nominal_pct",
    "rate_effective_pct",
    "real_rate_pct",
    "risk_score",
    "risk_proxy",
    "liquidity_score",
    "solvency_score",
    "profitability_score",
    score_col,
    "recommendation_tag",
]

columnas_tabla = [c for c in columnas_tabla if c in df_rank.columns]

st.dataframe(
    df_rank.loc[:, columnas_tabla],
    use_container_width=True
)

st.markdown("---")

# =========================
# AGRUPACIÓN POR TIPO DE ENTIDAD
# =========================
st.subheader("Promedios por tipo de entidad")

resumen_tipo = (
    df_rank.groupby("entity_type", as_index=False)
    .agg(
        registros=("entity_name", "count"),
        entidades=("entity_name", "nunique"),
        tasa_nominal_promedio=("rate_nominal_pct", "mean"),
        tasa_real_promedio=("real_rate_pct", "mean"),
        score_promedio=(score_col, "mean"),
        riesgo_promedio=("risk_score", "mean")
    )
    .sort_values("score_promedio", ascending=False)
)

st.dataframe(resumen_tipo, use_container_width=True)

st.markdown("---")

# =========================
# MEJORES OPORTUNIDADES POR MONEDA
# =========================
st.subheader("Mejores oportunidades por moneda")

if "currency_code" in df_rank.columns:
    mejores_por_moneda = (
        df_rank.sort_values(score_col, ascending=False)
        .groupby("currency_code", as_index=False)
        .first()
    )

    columnas_moneda = [
        "currency_code",
        "entity_name",
        "entity_type",
        "instrument_name",
        "term_profile",
        "rate_nominal_pct",
        "real_rate_pct",
        score_col,
        "recommendation_tag",
    ]
    columnas_moneda = [c for c in columnas_moneda if c in mejores_por_moneda.columns]

    st.dataframe(
        mejores_por_moneda[columnas_moneda],
        use_container_width=True
    )
