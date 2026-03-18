import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda
from utils.metrics import calcular_kpis_ranking, calcular_resumen_tipo, calcular_resumen_moneda
from utils.insights import generar_insight_ranking
from utils.charts import (
    grafico_top_ranking,
    grafico_barras_por_categoria,
    grafico_boxplot_por_categoria,
)

st.set_page_config(page_title="Ranking", page_icon="🏆", layout="wide")

st.title("Ranking de oportunidades")
st.markdown(
    """
    Explora las mejores oportunidades de inversión en CDAs según distintos perfiles
    y compara cómo cambian los líderes por moneda, plazo y tipo de entidad.
    """
)

# =========================
# CARGA
# =========================
df = cargar_datos_cda()

if df.empty:
    st.warning("No se pudo cargar la base de CDAs.")
    st.stop()

# =========================
# FILTROS
# =========================
filtros = render_filtros_cda(df, key_prefix="ranking")
df_f = aplicar_filtros_cda(df, filtros)

if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# =========================
# PERFIL
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

if score_col not in df_f.columns:
    st.warning(f"No existe la columna {score_col} en la base.")
    st.stop()

df_rank = df_f.sort_values(score_col, ascending=False).reset_index(drop=True)

# =========================
# KPIs
# =========================
kpis = calcular_kpis_ranking(df_rank, score_col=score_col)

st.subheader("KPIs del ranking filtrado")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{kpis.get('registros', 0)}")
col2.metric("Entidades", f"{kpis.get('entidades', 0)}")
col3.metric(
    "Score promedio",
    f"{kpis.get('score_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("score_promedio")) else "N/D"
)
col4.metric(
    "Mejor score",
    f"{kpis.get('score_maximo', float('nan')):.2f}"
    if pd.notna(kpis.get("score_maximo")) else "N/D"
)

st.markdown("---")

# =========================
# TOP 1
# =========================
top = df_rank.iloc[0]

st.subheader(f"Mejor oportunidad · Perfil {perfil.lower()}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Entidad", top.get("entity_name", "N/D"))
col2.metric("Tasa nominal", f"{top.get('rate_nominal_pct', float('nan')):.2f}%")
col3.metric("Tasa real", f"{top.get('real_rate_pct', float('nan')):.2f}%")
col4.metric(titulo_score, f"{top.get(score_col, float('nan')):.2f}")

st.markdown(
    f"""
    **Instrumento:** {top.get('instrument_name', 'N/D')}  
    **Moneda:** {top.get('currency_code', 'N/D')}  
    **Perfil de plazo:** {top.get('term_profile', 'N/D')}  
    **Bucket de plazo:** {top.get('term_bucket', 'N/D')}  
    **Tipo de entidad:** {top.get('entity_type', 'N/D')}  
    **Riesgo:** {top.get('risk_score', float('nan')):.2f}  
    **Liquidez:** {top.get('liquidity_score', float('nan')):.2f}  
    **Solvencia:** {top.get('solvency_score', float('nan')):.2f}  
    **Recomendación:** {top.get('recommendation_tag', 'N/D')}
    """
)

st.info(generar_insight_ranking(df_rank, perfil=perfil, score_col=score_col))

st.markdown("---")

# =========================
# TOP 10 VISUAL
# =========================
st.subheader(f"Top 10 oportunidades · Perfil {perfil.lower()}")

fig = grafico_top_ranking(
    df_rank,
    score_col=score_col,
    nombre_col="entity_name",
    top_n=10,
    titulo=f"Top 10 por {titulo_score.lower()}",
    color_col="entity_type"
)
if fig is not None:
    st.plotly_chart(fig, use_container_width=True)

columnas_top = [
    rank_col,
    "entity_name",
    "entity_type",
    "currency_code",
    "instrument_name",
    "term_profile",
    "term_bucket",
    "term_days_floor",
    "min_amount",
    "rate_nominal_pct",
    "real_rate_pct",
    "risk_score",
    "liquidity_score",
    "solvency_score",
    score_col,
    "recommendation_tag",
]
columnas_top = [c for c in columnas_top if c in df_rank.columns]

st.dataframe(df_rank[columnas_top].head(10), use_container_width=True)

st.markdown("---")

# =========================
# DESCOMPOSICIÓN DEL LÍDER
# =========================
st.subheader("Descomposición de la mejor oportunidad")

componentes = [
    "nominal_return_score_100",
    "real_return_score_100",
    "safety_score_100",
    "flexibility_score_100",
    "accessibility_score_100",
    "market_timing_score_100",
]

componentes = [c for c in componentes if c in df_rank.columns]

if componentes:
    df_componentes = pd.DataFrame({
        "componente": componentes,
        "score": [top.get(c, float("nan")) for c in componentes]
    }).sort_values("score", ascending=False)

    st.dataframe(df_componentes, use_container_width=True)

st.markdown("---")

# =========================
# RANKING POR SEGMENTOS
# =========================
st.subheader("Liderazgo por segmentos")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_barras_por_categoria(
        df_rank,
        categoria_col="currency_code",
        valor_col=score_col,
        titulo=f"{titulo_score} promedio por moneda"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_barras_por_categoria(
        df_rank,
        categoria_col="term_profile",
        valor_col=score_col,
        titulo=f"{titulo_score} promedio por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = grafico_barras_por_categoria(
        df_rank,
        categoria_col="entity_type",
        valor_col=score_col,
        titulo=f"{titulo_score} promedio por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = grafico_boxplot_por_categoria(
        df_rank,
        categoria_col="entity_type",
        valor_col=score_col,
        titulo=f"Distribución de {titulo_score.lower()} por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# MEJORES POR MONEDA
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
        "risk_score",
        score_col,
        "recommendation_tag",
    ]
    columnas_moneda = [c for c in columnas_moneda if c in mejores_por_moneda.columns]

    st.dataframe(mejores_por_moneda[columnas_moneda], use_container_width=True)

st.markdown("---")

# =========================
# RESÚMENES
# =========================
st.subheader("Resúmenes del ranking")

resumen_tipo = calcular_resumen_tipo(df_rank)
resumen_moneda = calcular_resumen_moneda(df_rank)

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
# TABLA COMPLETA
# =========================
st.subheader("Tabla completa del ranking")

columnas_tabla = [
    rank_col,
    "entity_name",
    "entity_type",
    "currency_code",
    "instrument_name",
    "term_profile",
    "term_bucket",
    "term_days_floor",
    "size_bucket",
    "interest_payment_frequency",
    "min_amount",
    "rate_nominal_pct",
    "rate_effective_pct",
    "real_rate_pct",
    "risk_score",
    "risk_proxy",
    "liquidity_score",
    "solvency_score",
    "profitability_score",
    "accessibility_score_100",
    "nominal_return_score_100",
    "real_return_score_100",
    "safety_score_100",
    "flexibility_score_100",
    "market_timing_score_100",
    score_col,
    "recommendation_tag",
]

columnas_tabla = [c for c in columnas_tabla if c in df_rank.columns]

st.dataframe(df_rank[columnas_tabla], use_container_width=True)
