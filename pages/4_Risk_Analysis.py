import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda, filtrar_datos

st.set_page_config(page_title="Análisis de Riesgo", page_icon="🛡️", layout="wide")

st.title("Análisis de riesgo y retorno")
st.markdown(
    """
    Evalúa las oportunidades de inversión en CDAs desde una perspectiva de
    **riesgo, rentabilidad, liquidez, solvencia y perfil de inversión**.
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

if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# =========================
# CLASIFICACIONES AUXILIARES
# =========================
df_f = df_f.copy()

# Clasificación simple de riesgo
if "risk_score" in df_f.columns:
    df_f["categoria_riesgo"] = pd.cut(
        df_f["risk_score"],
        bins=[-float("inf"), 33, 66, float("inf")],
        labels=["Bajo", "Medio", "Alto"]
    )
else:
    df_f["categoria_riesgo"] = "No disponible"

# Clasificación simple de atractivo balanceado
if "final_score_balanced" in df_f.columns:
    df_f["categoria_atractivo"] = pd.cut(
        df_f["final_score_balanced"],
        bins=[-float("inf"), 40, 70, float("inf")],
        labels=["Bajo", "Medio", "Alto"]
    )
else:
    df_f["categoria_atractivo"] = "No disponible"

# =========================
# KPIs PRINCIPALES
# =========================
st.subheader("KPIs principales de riesgo y retorno")

riesgo_promedio = df_f["risk_score"].mean() if "risk_score" in df_f.columns else float("nan")
tasa_real_promedio = df_f["real_rate_pct"].mean() if "real_rate_pct" in df_f.columns else float("nan")
liquidez_promedio = df_f["liquidity_score"].mean() if "liquidity_score" in df_f.columns else float("nan")
solvencia_promedio = df_f["solvency_score"].mean() if "solvency_score" in df_f.columns else float("nan")
score_balanceado_promedio = (
    df_f["final_score_balanced"].mean() if "final_score_balanced" in df_f.columns else float("nan")
)
entidades = df_f["entity_name"].nunique() if "entity_name" in df_f.columns else 0

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("Entidades analizadas", f"{entidades}")
col2.metric("Riesgo promedio", f"{riesgo_promedio:.2f}")
col3.metric("Tasa real promedio", f"{tasa_real_promedio:.2f}%")

col4.metric("Liquidez promedio", f"{liquidez_promedio:.2f}")
col5.metric("Solvencia promedio", f"{solvencia_promedio:.2f}")
col6.metric("Score balanceado promedio", f"{score_balanceado_promedio:.2f}")

st.markdown("---")

# =========================
# MEJORES OPORTUNIDADES SEGÚN ENFOQUE
# =========================
st.subheader("Mejores oportunidades según enfoque")

menor_riesgo = df_f.sort_values("risk_score", ascending=True).iloc[0]
mayor_tasa_real = df_f.sort_values("real_rate_pct", ascending=False).iloc[0]
mejor_balanceado = df_f.sort_values("final_score_balanced", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Menor riesgo")
    st.write(f"**Entidad:** {menor_riesgo['entity_name']}")
    st.write(f"**Instrumento:** {menor_riesgo.get('instrument_name', 'N/D')}")
    st.write(f"**Riesgo:** {menor_riesgo['risk_score']:.2f}")
    st.write(f"**Tasa real:** {menor_riesgo.get('real_rate_pct', float('nan')):.2f}%")

with col2:
    st.markdown("### Mayor tasa real")
    st.write(f"**Entidad:** {mayor_tasa_real['entity_name']}")
    st.write(f"**Instrumento:** {mayor_tasa_real.get('instrument_name', 'N/D')}")
    st.write(f"**Tasa real:** {mayor_tasa_real['real_rate_pct']:.2f}%")
    st.write(f"**Riesgo:** {mayor_tasa_real.get('risk_score', float('nan')):.2f}")

with col3:
    st.markdown("### Mejor equilibrio riesgo-retorno")
    st.write(f"**Entidad:** {mejor_balanceado['entity_name']}")
    st.write(f"**Instrumento:** {mejor_balanceado.get('instrument_name', 'N/D')}")
    st.write(f"**Score balanceado:** {mejor_balanceado['final_score_balanced']:.2f}")
    st.write(f"**Tasa real:** {mejor_balanceado.get('real_rate_pct', float('nan')):.2f}%")

st.markdown("---")

# =========================
# SEGMENTACIÓN DEL MERCADO
# =========================
st.subheader("Segmentación básica de oportunidades")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Distribución por categoría de riesgo")
    dist_riesgo = (
        df_f["categoria_riesgo"]
        .value_counts(dropna=False)
        .rename_axis("categoria_riesgo")
        .reset_index(name="registros")
    )
    st.dataframe(dist_riesgo, use_container_width=True)

with col2:
    st.markdown("### Distribución por atractivo balanceado")
    dist_atractivo = (
        df_f["categoria_atractivo"]
        .value_counts(dropna=False)
        .rename_axis("categoria_atractivo")
        .reset_index(name="registros")
    )
    st.dataframe(dist_atractivo, use_container_width=True)

st.markdown("---")

# =========================
# MATRIZ SIMPLE DE OPORTUNIDADES
# =========================
st.subheader("Matriz simple de riesgo vs atractivo")

matriz = (
    df_f.groupby(["categoria_riesgo", "categoria_atractivo"], dropna=False)
    .size()
    .reset_index(name="registros")
    .sort_values(["categoria_riesgo", "categoria_atractivo"])
)

st.dataframe(matriz, use_container_width=True)

st.markdown("---")

# =========================
# TABLA PRINCIPAL DE RIESGO
# =========================
st.subheader("Tabla de análisis de riesgo")

columnas_riesgo = [
    "entity_name",
    "entity_type",
    "instrument_name",
    "currency_code",
    "term_profile",
    "term_days_floor",
    "rate_nominal_pct",
    "real_rate_pct",
    "risk_score",
    "risk_proxy",
    "liquidity_score",
    "solvency_score",
    "npl_score",
    "profitability_score",
    "safety_score_100",
    "flexibility_score_100",
    "market_timing_score_100",
    "final_score_conservative",
    "final_score_balanced",
    "final_score_aggressive",
    "categoria_riesgo",
    "categoria_atractivo",
    "recommendation_tag",
]

columnas_riesgo = [c for c in columnas_riesgo if c in df_f.columns]

tabla_riesgo = df_f[columnas_riesgo].sort_values(
    ["final_score_balanced", "real_rate_pct"],
    ascending=[False, False]
)

st.dataframe(tabla_riesgo, use_container_width=True)

st.markdown("---")

# =========================
# RESUMEN POR TIPO DE ENTIDAD
# =========================
st.subheader("Resumen por tipo de entidad")

if "entity_type" in df_f.columns:
    resumen_tipo = (
        df_f.groupby("entity_type", as_index=False)
        .agg(
            registros=("entity_name", "count"),
            entidades=("entity_name", "nunique"),
            riesgo_promedio=("risk_score", "mean"),
            tasa_real_promedio=("real_rate_pct", "mean"),
            liquidez_promedio=("liquidity_score", "mean"),
            solvencia_promedio=("solvency_score", "mean"),
            score_conservador_promedio=("final_score_conservative", "mean"),
            score_balanceado_promedio=("final_score_balanced", "mean"),
            score_agresivo_promedio=("final_score_aggressive", "mean"),
        )
        .sort_values("score_balanceado_promedio", ascending=False)
    )

    st.dataframe(resumen_tipo, use_container_width=True)

st.markdown("---")

# =========================
# MEJORES OPCIONES POR PERFIL
# =========================
st.subheader("Mejores opciones por perfil de inversión")

mejor_conservador = df_f.sort_values("final_score_conservative", ascending=False).iloc[0]
mejor_balanceado = df_f.sort_values("final_score_balanced", ascending=False).iloc[0]
mejor_agresivo = df_f.sort_values("final_score_aggressive", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Perfil conservador")
    st.write(f"**Entidad:** {mejor_conservador['entity_name']}")
    st.write(f"**Instrumento:** {mejor_conservador.get('instrument_name', 'N/D')}")
    st.write(f"**Score conservador:** {mejor_conservador['final_score_conservative']:.2f}")
    st.write(f"**Riesgo:** {mejor_conservador.get('risk_score', float('nan')):.2f}")
    st.write(f"**Tasa real:** {mejor_conservador.get('real_rate_pct', float('nan')):.2f}%")

with col2:
    st.markdown("### Perfil balanceado")
    st.write(f"**Entidad:** {mejor_balanceado['entity_name']}")
    st.write(f"**Instrumento:** {mejor_balanceado.get('instrument_name', 'N/D')}")
    st.write(f"**Score balanceado:** {mejor_balanceado['final_score_balanced']:.2f}")
    st.write(f"**Riesgo:** {mejor_balanceado.get('risk_score', float('nan')):.2f}")
    st.write(f"**Tasa real:** {mejor_balanceado.get('real_rate_pct', float('nan')):.2f}%")

with col3:
    st.markdown("### Perfil agresivo")
    st.write(f"**Entidad:** {mejor_agresivo['entity_name']}")
    st.write(f"**Instrumento:** {mejor_agresivo.get('instrument_name', 'N/D')}")
    st.write(f"**Score agresivo:** {mejor_agresivo['final_score_aggressive']:.2f}")
    st.write(f"**Riesgo:** {mejor_agresivo.get('risk_score', float('nan')):.2f}")
    st.write(f"**Tasa real:** {mejor_agresivo.get('real_rate_pct', float('nan')):.2f}%")

st.markdown("---")

# =========================
# LECTURA INTERPRETATIVA
# =========================
st.subheader("Lectura interpretativa")

top_interpretacion = (
    df_f.sort_values("final_score_balanced", ascending=False)
    .head(5)
)

for _, row in top_interpretacion.iterrows():
    st.markdown(f"### {row['entity_name']}")
    st.write(f"**Instrumento:** {row.get('instrument_name', 'N/D')}")
    st.write(f"**Moneda:** {row.get('currency_code', 'N/D')}")
    st.write(f"**Plazo:** {row.get('term_profile', 'N/D')}")
    st.write(f"**Tasa nominal:** {row.get('rate_nominal_pct', float('nan')):.2f}%")
    st.write(f"**Tasa real:** {row.get('real_rate_pct', float('nan')):.2f}%")
    st.write(f"**Riesgo:** {row.get('risk_score', float('nan')):.2f} · Categoría: {row.get('categoria_riesgo', 'N/D')}")
    st.write(f"**Liquidez:** {row.get('liquidity_score', float('nan')):.2f}")
    st.write(f"**Solvencia:** {row.get('solvency_score', float('nan')):.2f}")
    st.write(f"**Score balanceado:** {row.get('final_score_balanced', float('nan')):.2f}")
    st.write(f"**Recomendación:** {row.get('recommendation_tag', 'N/D')}")
    st.markdown("---")
