import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda, filtrar_datos

st.set_page_config(page_title="Comparador", page_icon="⚖️", layout="wide")

st.title("Comparador de CDAs")
st.markdown(
    """
    Compara distintas oportunidades de inversión en CDAs del sistema financiero paraguayo
    de forma directa y estructurada.
    """
)

# =========================
# CARGA DE DATOS
# =========================
df = cargar_datos_cda()

# =========================
# FILTROS GENERALES
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
# IDENTIFICADOR DESCRIPTIVO
# =========================
df_f = df_f.copy()

df_f["opcion_comparacion"] = (
    df_f["entity_name"].fillna("Entidad") + " | " +
    df_f["instrument_name"].fillna("Instrumento") + " | " +
    df_f["currency_code"].fillna("Moneda") + " | " +
    df_f["term_profile"].fillna("Plazo")
)

# =========================
# SELECTOR DE OPCIONES
# =========================
st.subheader("Selecciona las opciones a comparar")

opciones = st.multiselect(
    "Elige entre 2 y 4 opciones",
    options=df_f["opcion_comparacion"].tolist(),
    default=df_f["opcion_comparacion"].tolist()[:2]
)

if len(opciones) < 2:
    st.info("Selecciona al menos 2 opciones para activar el comparador.")
    st.stop()

if len(opciones) > 4:
    st.warning("Selecciona un máximo de 4 opciones.")
    st.stop()

df_comp = df_f[df_f["opcion_comparacion"].isin(opciones)].copy()

# =========================
# BLOQUE DESTACADO
# =========================
st.subheader("Resumen rápido")

mejor_balanceado = df_comp.sort_values("final_score_balanced", ascending=False).iloc[0]
mayor_tasa = df_comp.sort_values("rate_nominal_pct", ascending=False).iloc[0]
menor_riesgo = df_comp.sort_values("risk_score", ascending=True).iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("Mejor score balanceado", mejor_balanceado["entity_name"])
col2.metric("Mayor tasa nominal", mayor_tasa["entity_name"])
col3.metric("Menor riesgo", menor_riesgo["entity_name"])

st.markdown("---")

# =========================
# TABLA PRINCIPAL DE COMPARACIÓN
# =========================
st.subheader("Comparación estructurada")

columnas_comparacion = [
    "entity_name",
    "entity_type",
    "instrument_name",
    "currency_code",
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
    "npl_score",
    "profitability_score",
    "withdrawal_allowed",
    "early_withdrawal_penalty",
    "compound_interest",
    "guarantee",
    "auto_renewal",
    "final_score_conservative",
    "final_score_balanced",
    "final_score_aggressive",
    "recommendation_tag",
]

columnas_comparacion = [c for c in columnas_comparacion if c in df_comp.columns]

tabla_comp = df_comp[columnas_comparacion].set_index("entity_name").T

st.dataframe(tabla_comp, use_container_width=True)

st.markdown("---")

# =========================
# COMPARACIÓN RESUMIDA DE SCORES
# =========================
st.subheader("Comparación resumida de scores")

columnas_scores = [
    "entity_name",
    "rate_nominal_pct",
    "real_rate_pct",
    "risk_score",
    "liquidity_score",
    "solvency_score",
    "final_score_conservative",
    "final_score_balanced",
    "final_score_aggressive",
]

columnas_scores = [c for c in columnas_scores if c in df_comp.columns]

st.dataframe(
    df_comp[columnas_scores].sort_values("final_score_balanced", ascending=False),
    use_container_width=True
)

st.markdown("---")

# =========================
# MEJOR OPCIÓN SEGÚN PERFIL
# =========================
st.subheader("Mejor opción según perfil de inversión")

mejor_conservador = df_comp.sort_values("final_score_conservative", ascending=False).iloc[0]
mejor_balanceado = df_comp.sort_values("final_score_balanced", ascending=False).iloc[0]
mejor_agresivo = df_comp.sort_values("final_score_aggressive", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Conservador")
    st.write(f"**Entidad:** {mejor_conservador['entity_name']}")
    st.write(f"**Instrumento:** {mejor_conservador['instrument_name']}")
    st.write(f"**Score:** {mejor_conservador['final_score_conservative']:.2f}")
    st.write(f"**Tasa nominal:** {mejor_conservador['rate_nominal_pct']:.2f}%")

with col2:
    st.markdown("### Balanceado")
    st.write(f"**Entidad:** {mejor_balanceado['entity_name']}")
    st.write(f"**Instrumento:** {mejor_balanceado['instrument_name']}")
    st.write(f"**Score:** {mejor_balanceado['final_score_balanced']:.2f}")
    st.write(f"**Tasa nominal:** {mejor_balanceado['rate_nominal_pct']:.2f}%")

with col3:
    st.markdown("### Agresivo")
    st.write(f"**Entidad:** {mejor_agresivo['entity_name']}")
    st.write(f"**Instrumento:** {mejor_agresivo['instrument_name']}")
    st.write(f"**Score:** {mejor_agresivo['final_score_aggressive']:.2f}")
    st.write(f"**Tasa nominal:** {mejor_agresivo['rate_nominal_pct']:.2f}%")

st.markdown("---")

# =========================
# DETALLE INTERPRETABLE
# =========================
st.subheader("Lectura interpretativa")

for _, row in df_comp.sort_values("final_score_balanced", ascending=False).iterrows():
    st.markdown(f"### {row['entity_name']}")
    st.write(f"**Instrumento:** {row.get('instrument_name', 'N/D')}")
    st.write(f"**Moneda:** {row.get('currency_code', 'N/D')}")
    st.write(f"**Plazo:** {row.get('term_profile', 'N/D')}")
    st.write(f"**Tasa nominal:** {row.get('rate_nominal_pct', float('nan')):.2f}%")
    st.write(f"**Tasa real:** {row.get('real_rate_pct', float('nan')):.2f}%")
    st.write(f"**Riesgo:** {row.get('risk_score', float('nan')):.2f}")
    st.write(f"**Score balanceado:** {row.get('final_score_balanced', float('nan')):.2f}")
    st.write(f"**Recomendación:** {row.get('recommendation_tag', 'N/D')}")
    st.markdown("---")
