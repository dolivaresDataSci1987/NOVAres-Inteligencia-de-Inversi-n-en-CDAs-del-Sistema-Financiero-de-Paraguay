import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda
from utils.metrics import (
    calcular_kpis_generales,
    calcular_resumen_tipo,
)
from utils.insights import generar_insight_riesgo
from utils.charts import (
    grafico_riesgo_retorno,
    grafico_boxplot_por_categoria,
    grafico_barras_por_categoria,
    grafico_matriz_riesgo_atractivo,
    grafico_top_ranking,
)

st.set_page_config(page_title="Análisis de Riesgo", page_icon="🛡️", layout="wide")

st.title("Análisis de riesgo y retorno")
st.markdown(
    """
    Esta página ayuda a interpretar el mercado de CDAs desde una lógica de
    **riesgo, retorno real, liquidez y equilibrio general**.

    La idea no es mirar solo cuánto paga una opción, sino entender
    **si ese retorno compensa el riesgo asumido** y qué oportunidades aparecen
    como más defensivas o más agresivas dentro del universo filtrado.
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
filtros = render_filtros_cda(df, key_prefix="risk")
df_f = aplicar_filtros_cda(df, filtros)

if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# =========================
# GUÍA DE LECTURA
# =========================
st.subheader("Cómo interpretar esta página")

st.markdown(
    """
    Aquí conviene leer cada oportunidad con cuatro preguntas simples:

    - **¿Cuánto paga?** → tasa nominal y tasa real.
    - **¿Qué tan defensiva parece?** → riesgo y seguridad relativa.
    - **¿Qué tan flexible es?** → liquidez y condiciones del producto.
    - **¿Compensa lo que ofrece?** → score balanceado y posicionamiento frente al resto.

    **Lectura práctica:**
    - una opción atractiva no siempre es la de mayor tasa,
    - una opción de menor riesgo no siempre es la mejor si el retorno real es muy pobre,
    - el punto interesante suele estar en el equilibrio entre retorno y protección.
    """
)

with st.expander("Qué significa riesgo alto, medio o bajo en esta página"):
    st.markdown(
        """
        La categoría de riesgo es una **clasificación interna del dashboard** para ordenar oportunidades
        dentro del universo disponible.

        - **Bajo:** opción relativamente más defensiva frente al resto.
        - **Medio:** zona intermedia, con compensaciones entre protección y retorno.
        - **Alto:** opción relativamente más exigente en términos de riesgo.

        Esto no equivale a una garantía ni a una calificación oficial externa.
        Sirve para comparar mejor las alternativas visibles.
        """
    )

st.markdown("---")

# =========================
# CLASIFICACIONES AUXILIARES
# =========================
df_f = df_f.copy()

if "risk_score" in df_f.columns:
    df_f["categoria_riesgo"] = pd.cut(
        df_f["risk_score"],
        bins=[-float("inf"), 33, 66, float("inf")],
        labels=["Bajo", "Medio", "Alto"]
    )
else:
    df_f["categoria_riesgo"] = "No disponible"

if "final_score_balanced" in df_f.columns:
    df_f["categoria_atractivo"] = pd.cut(
        df_f["final_score_balanced"],
        bins=[-float("inf"), 40, 70, float("inf")],
        labels=["Bajo", "Medio", "Alto"]
    )
else:
    df_f["categoria_atractivo"] = "No disponible"

# =========================
# KPIS
# =========================
kpis = calcular_kpis_generales(df_f)

st.subheader("KPIs clave de riesgo y retorno")

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

col1.metric("Registros", f"{kpis.get('registros', 0)}")
col2.metric("Entidades", f"{kpis.get('entidades', 0)}")
col3.metric(
    "Riesgo promedio",
    f"{kpis.get('riesgo_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("riesgo_promedio")) else "N/D"
)
col4.metric(
    "Tasa real promedio",
    f"{kpis.get('tasa_real_promedio', float('nan')):.2f}%"
    if pd.notna(kpis.get("tasa_real_promedio")) else "N/D"
)

col5.metric(
    "Liquidez promedio",
    f"{kpis.get('liquidez_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("liquidez_promedio")) else "N/D"
)
col6.metric(
    "Solvencia promedio",
    f"{kpis.get('solvencia_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("solvencia_promedio")) else "N/D"
)
col7.metric(
    "Score balanceado promedio",
    f"{kpis.get('score_balanceado_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("score_balanceado_promedio")) else "N/D"
)
col8.metric(
    "% con tasa real positiva",
    f"{kpis.get('pct_tasa_real_positiva', float('nan')):.1f}%"
    if pd.notna(kpis.get("pct_tasa_real_positiva")) else "N/D"
)

st.markdown("---")

# =========================
# INSIGHT
# =========================
st.subheader("Lectura ejecutiva")
st.info(generar_insight_riesgo(df_f))

st.markdown("---")

# =========================
# OPORTUNIDADES DESTACADAS
# =========================
st.subheader("Oportunidades destacadas según enfoque")

menor_riesgo = df_f.sort_values("risk_score", ascending=True).iloc[0]
mayor_tasa_real = df_f.sort_values("real_rate_pct", ascending=False).iloc[0]
mejor_balanceado = df_f.sort_values("final_score_balanced", ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Opción más defensiva")
    st.write(f"**Entidad:** {menor_riesgo.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(menor_riesgo.get('term_days_floor', 0)) if pd.notna(menor_riesgo.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Riesgo:** {menor_riesgo.get('risk_score', float('nan')):.2f}")
    st.write(f"**Tasa real:** {menor_riesgo.get('real_rate_pct', float('nan')):.2f}%")

with col2:
    st.markdown("### Mayor retorno real")
    st.write(f"**Entidad:** {mayor_tasa_real.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mayor_tasa_real.get('term_days_floor', 0)) if pd.notna(mayor_tasa_real.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Tasa real:** {mayor_tasa_real.get('real_rate_pct', float('nan')):.2f}%")
    st.write(f"**Riesgo:** {mayor_tasa_real.get('risk_score', float('nan')):.2f}")

with col3:
    st.markdown("### Mejor equilibrio general")
    st.write(f"**Entidad:** {mejor_balanceado.get('entity_name', 'N/D')}")
    st.write(f"**Qué es:** CDA de **{int(mejor_balanceado.get('term_days_floor', 0)) if pd.notna(mejor_balanceado.get('term_days_floor')) else 'N/D'} días**")
    st.write(f"**Score balanceado:** {mejor_balanceado.get('final_score_balanced', float('nan')):.2f}")
    st.write(f"**Tasa real:** {mejor_balanceado.get('real_rate_pct', float('nan')):.2f}%")

st.markdown("---")

# =========================
# MAPA RIESGO-RETORNO
# =========================
st.subheader("Mapa principal de riesgo vs retorno real")

fig_rr = grafico_riesgo_retorno(
    df_f,
    x_col="risk_score",
    y_col="real_rate_pct",
    color_col="entity_type",
    size_col="final_score_balanced",
    hover_name="entity_name",
    titulo="Riesgo vs retorno real"
)
if fig_rr is not None:
    st.plotly_chart(fig_rr, use_container_width=True)

st.markdown(
    """
    **Cómo leer este mapa:**  
    - más a la derecha = mayor riesgo relativo,  
    - más arriba = mejor retorno real,  
    - puntos más grandes = mejor score balanceado general.  

    Las oportunidades más interesantes suelen estar en la zona donde el retorno real es alto
    sin que el riesgo se dispare demasiado.
    """
)

st.markdown("---")

# =========================
# MATRIZ RIESGO / ATRACTIVO
# =========================
st.subheader("Matriz de riesgo vs atractivo")

fig_matriz = grafico_matriz_riesgo_atractivo(
    df_f,
    risk_col="categoria_riesgo",
    atr_col="categoria_atractivo",
    titulo="Cruce entre categoría de riesgo y atractivo balanceado"
)
if fig_matriz is not None:
    st.plotly_chart(fig_matriz, use_container_width=True)

st.markdown(
    """
    Esta matriz ayuda a separar rápidamente:
    - oportunidades con **bajo riesgo y alto atractivo**,
    - opciones intermedias,
    - y productos que quedan peor posicionados en el equilibrio general.
    """
)

st.markdown("---")

# =========================
# DISTRIBUCIONES
# =========================
st.subheader("Distribuciones y segmentación")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_boxplot_por_categoria(
        df_f,
        categoria_col="entity_type",
        valor_col="risk_score",
        titulo="Distribución de riesgo por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_boxplot_por_categoria(
        df_f,
        categoria_col="term_profile",
        valor_col="real_rate_pct",
        titulo="Distribución de tasa real por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = grafico_barras_por_categoria(
        df_f,
        categoria_col="entity_type",
        valor_col="final_score_balanced",
        titulo="Score balanceado promedio por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = grafico_barras_por_categoria(
        df_f,
        categoria_col="term_profile",
        valor_col="risk_score",
        titulo="Riesgo promedio por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# TOP DEFENSIVO / TOP RETORNO
# =========================
st.subheader("Rankings específicos")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_top_ranking(
        df_f.sort_values("final_score_conservative", ascending=False),
        score_col="final_score_conservative",
        nombre_col="entity_name",
        top_n=8,
        titulo="Top oportunidades defensivas",
        color_col="entity_type"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_top_ranking(
        df_f.sort_values("real_rate_pct", ascending=False),
        score_col="real_rate_pct",
        nombre_col="entity_name",
        top_n=8,
        titulo="Top oportunidades por retorno real",
        color_col="entity_type"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# RESÚMENES TABULARES
# =========================
st.subheader("Resúmenes analíticos")

resumen_tipo = calcular_resumen_tipo(df_f)

if not resumen_tipo.empty:
    st.markdown("### Resumen por tipo de entidad")
    st.dataframe(resumen_tipo, use_container_width=True)

st.markdown("---")

# =========================
# TABLA PRINCIPAL
# =========================
st.subheader("Tabla de análisis de riesgo")

columnas_riesgo = [
    "entity_name",
    "entity_type",
    "instrument_name",
    "term_profile",
    "term_bucket",
    "term_days_floor",
    "min_amount",
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
).copy()

tabla_riesgo = tabla_riesgo.rename(columns={
    "entity_name": "Entidad",
    "entity_type": "Tipo de entidad",
    "instrument_name": "Instrumento",
    "term_profile": "Perfil de plazo",
    "term_bucket": "Bucket plazo",
    "term_days_floor": "Días",
    "min_amount": "Monto mínimo",
    "rate_nominal_pct": "Tasa nominal (%)",
    "real_rate_pct": "Tasa real (%)",
    "risk_score": "Riesgo",
    "risk_proxy": "Proxy de riesgo",
    "liquidity_score": "Liquidez",
    "solvency_score": "Solvencia",
    "npl_score": "NPL",
    "profitability_score": "Rentabilidad",
    "safety_score_100": "Seguridad",
    "flexibility_score_100": "Flexibilidad",
    "market_timing_score_100": "Timing mercado",
    "final_score_conservative": "Score conservador",
    "final_score_balanced": "Score balanceado",
    "final_score_aggressive": "Score agresivo",
    "categoria_riesgo": "Categoría riesgo",
    "categoria_atractivo": "Categoría atractivo",
    "recommendation_tag": "Etiqueta",
})

st.dataframe(tabla_riesgo, use_container_width=True)
