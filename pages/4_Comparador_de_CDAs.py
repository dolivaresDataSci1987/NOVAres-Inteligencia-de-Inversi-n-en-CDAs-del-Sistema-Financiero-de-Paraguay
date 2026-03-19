import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda
from utils.insights import generar_insight_comparator
from utils.charts import (
    grafico_radar_comparador,
    grafico_barras_scores_comparador,
)

st.set_page_config(page_title="Comparador", layout="wide")

st.title("⚖️ Comparador de CDAs")
st.markdown(
    """
    Compara de forma directa varias oportunidades de inversión en CDAs.
    Esta página sirve para ver **qué opción destaca más**, **en qué dimensión lo hace**
    y **qué sacrificios implica elegir una frente a otra**.
    """
)
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
filtros = render_filtros_cda(df, key_prefix="comparator")
df_f = aplicar_filtros_cda(df, filtros)

if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# =========================
# EXPLICACIÓN
# =========================
st.subheader("Cómo interpretar esta página")

st.markdown(
    """
    Aquí no estás viendo un ranking global, sino una **comparación directa entre opciones concretas**.

    **Para usar bien esta vista:**
    - selecciona entre **2 y 4 CDAs**,
    - compara su **plazo en días**,
    - revisa su **tasa nominal**, **tasa real** y **riesgo**,
    - y observa qué opción sale mejor según perfil conservador, balanceado o agresivo.

    La mejor opción no siempre es la que más paga, sino la que ofrece el equilibrio que más te interesa.
    """
)

st.markdown("---")

# =========================
# IDENTIFICADOR DESCRIPTIVO
# =========================
df_f = df_f.copy()

df_f["opcion_comparacion"] = (
    df_f["entity_name"].fillna("Entidad")
    + " · "
    + df_f["instrument_name"].fillna("Instrumento")
    + " · "
    + df_f["term_days_floor"].fillna(0).astype(int).astype(str)
    + " días"
)

# =========================
# SELECTOR
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

if df_comp.empty:
    st.warning("No se pudieron recuperar las opciones seleccionadas.")
    st.stop()

st.markdown("---")

# =========================
# RESUMEN RÁPIDO
# =========================
st.subheader("Resumen rápido")

mejor_balanceado = df_comp.sort_values("final_score_balanced", ascending=False).iloc[0]
mayor_tasa = df_comp.sort_values("rate_nominal_pct", ascending=False).iloc[0]
menor_riesgo = df_comp.sort_values("risk_score", ascending=True).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Mejor equilibrio general")
    st.write(f"**Entidad:** {mejor_balanceado.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mejor_balanceado.get('term_days_floor', 0)) if pd.notna(mejor_balanceado.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Score balanceado:** {mejor_balanceado.get('final_score_balanced', float('nan')):.2f}")

with col2:
    st.markdown("### Mayor tasa nominal")
    st.write(f"**Entidad:** {mayor_tasa.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mayor_tasa.get('term_days_floor', 0)) if pd.notna(mayor_tasa.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Tasa nominal:** {mayor_tasa.get('rate_nominal_pct', float('nan')):.2f}%")

with col3:
    st.markdown("### Menor riesgo")
    st.write(f"**Entidad:** {menor_riesgo.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(menor_riesgo.get('term_days_floor', 0)) if pd.notna(menor_riesgo.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Riesgo:** {menor_riesgo.get('risk_score', float('nan')):.2f}")

st.info(generar_insight_comparator(df_comp))

st.markdown("---")

# =========================
# TABLA EJECUTIVA
# =========================
st.subheader("Comparación ejecutiva")

columnas_resumen = [
    "entity_name",
    "instrument_name",
    "term_days_floor",
    "term_profile",
    "entity_type",
    "min_amount",
    "rate_nominal_pct",
    "real_rate_pct",
    "risk_score",
    "liquidity_score",
    "solvency_score",
    "final_score_conservative",
    "final_score_balanced",
    "final_score_aggressive",
    "recommendation_tag",
]

columnas_resumen = [c for c in columnas_resumen if c in df_comp.columns]

tabla_resumen = df_comp[columnas_resumen].copy()
tabla_resumen = tabla_resumen.rename(columns={
    "entity_name": "Entidad",
    "instrument_name": "Instrumento",
    "term_days_floor": "Días",
    "term_profile": "Perfil de plazo",
    "entity_type": "Tipo de entidad",
    "min_amount": "Monto mínimo",
    "rate_nominal_pct": "Tasa nominal (%)",
    "real_rate_pct": "Tasa real (%)",
    "risk_score": "Riesgo",
    "liquidity_score": "Liquidez",
    "solvency_score": "Solvencia",
    "final_score_conservative": "Score conservador",
    "final_score_balanced": "Score balanceado",
    "final_score_aggressive": "Score agresivo",
    "recommendation_tag": "Etiqueta",
})

st.dataframe(tabla_resumen, use_container_width=True)

st.markdown("---")

# =========================
# GRÁFICOS COMPARATIVOS
# =========================
st.subheader("Comparación visual")

fig_scores = grafico_barras_scores_comparador(
    df_comp,
    nombre_col="entity_name",
    columnas=[
        "final_score_conservative",
        "final_score_balanced",
        "final_score_aggressive"
    ],
    titulo="Comparación de scores por perfil"
)
if fig_scores is not None:
    st.plotly_chart(fig_scores, use_container_width=True)

fig_radar = grafico_radar_comparador(
    df_comp,
    categorias=[
        "real_return_score_100",
        "safety_score_100",
        "flexibility_score_100",
        "accessibility_score_100",
        "market_timing_score_100"
    ],
    nombre_col="entity_name",
    titulo="Comparación multidimensional"
)
if fig_radar is not None:
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# =========================
# MEJOR OPCIÓN POR PERFIL
# =========================
st.subheader("Mejor opción según perfil de inversión")

mejor_conservador = df_comp.sort_values("final_score_conservative", ascending=False).iloc[0]
mejor_balanceado = df_comp.sort_values("final_score_balanced", ascending=False).iloc[0]
mejor_agresivo = df_comp.sort_values("final_score_aggressive", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Perfil conservador")
    st.write(f"**Entidad:** {mejor_conservador.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mejor_conservador.get('term_days_floor', 0)) if pd.notna(mejor_conservador.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Score:** {mejor_conservador.get('final_score_conservative', float('nan')):.2f}")
    st.write(f"**Tasa nominal:** {mejor_conservador.get('rate_nominal_pct', float('nan')):.2f}%")

with col2:
    st.markdown("### Perfil balanceado")
    st.write(f"**Entidad:** {mejor_balanceado.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mejor_balanceado.get('term_days_floor', 0)) if pd.notna(mejor_balanceado.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Score:** {mejor_balanceado.get('final_score_balanced', float('nan')):.2f}")
    st.write(f"**Tasa nominal:** {mejor_balanceado.get('rate_nominal_pct', float('nan')):.2f}%")

with col3:
    st.markdown("### Perfil agresivo")
    st.write(f"**Entidad:** {mejor_agresivo.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mejor_agresivo.get('term_days_floor', 0)) if pd.notna(mejor_agresivo.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Score:** {mejor_agresivo.get('final_score_aggressive', float('nan')):.2f}")
    st.write(f"**Tasa nominal:** {mejor_agresivo.get('rate_nominal_pct', float('nan')):.2f}%")

st.markdown("---")

# =========================
# LECTURA DETALLADA
# =========================
st.subheader("Lectura detallada por opción")

for _, row in df_comp.sort_values("final_score_balanced", ascending=False).iterrows():
    dias_txt = (
        str(int(row.get("term_days_floor", 0)))
        if pd.notna(row.get("term_days_floor"))
        else "N/D"
    )

    st.markdown(f"### {row.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{dias_txt} días**")
    st.write(f"**Instrumento:** {row.get('instrument_name', 'N/D')}")
    st.write(f"**Perfil de plazo:** {row.get('term_profile', 'N/D')}")
    st.write(f"**Tipo de entidad:** {row.get('entity_type', 'N/D')}")
    st.write(f"**Monto mínimo:** {row.get('min_amount', float('nan')):,.0f}")
    st.write(f"**Tasa nominal:** {row.get('rate_nominal_pct', float('nan')):.2f}%")
    st.write(f"**Tasa real:** {row.get('real_rate_pct', float('nan')):.2f}%")
    st.write(f"**Riesgo:** {row.get('risk_score', float('nan')):.2f}")
    st.write(f"**Liquidez:** {row.get('liquidity_score', float('nan')):.2f}")
    st.write(f"**Solvencia:** {row.get('solvency_score', float('nan')):.2f}")
    st.write(f"**Score conservador:** {row.get('final_score_conservative', float('nan')):.2f}")
    st.write(f"**Score balanceado:** {row.get('final_score_balanced', float('nan')):.2f}")
    st.write(f"**Score agresivo:** {row.get('final_score_aggressive', float('nan')):.2f}")
    st.write(f"**Etiqueta metodológica:** {row.get('recommendation_tag', 'N/D')}")
    st.markdown("---")
