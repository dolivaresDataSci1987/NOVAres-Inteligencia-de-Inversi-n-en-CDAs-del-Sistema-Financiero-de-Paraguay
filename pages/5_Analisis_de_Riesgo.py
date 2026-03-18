import streamlit as st
import pandas as pd
import plotly.express as px

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda
from utils.metrics import (
    calcular_kpis_generales,
    calcular_resumen_tipo,
    calcular_resumen_plazo,
)
from utils.insights import generar_insight_riesgo
from utils.charts import (
    grafico_riesgo_retorno,
    grafico_boxplot_por_categoria,
)

st.set_page_config(page_title="Riesgo", layout="wide")

st.title("⚠️ Análisis de Riesgo")
st.markdown(
    """
    Esta página analiza el **universo filtrado de CDAs**, no una sola entidad aislada.
    El objetivo es entender cómo se distribuyen las oportunidades según su
    **riesgo**, **retorno real**, **plazo** y **atractivo general**.
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

df_f = df_f.copy()

# =========================
# TEXTO EXPLICATIVO
# =========================
st.subheader("Cómo interpretar esta página")

st.markdown(
    """
    Aquí no estamos evaluando solo cuánto paga un CDA, sino **qué tan razonable parece ese retorno**
    en relación con el riesgo asumido.

    **Qué conviene mirar:**
    - **Riesgo:** qué tan defensiva o exigente parece la oportunidad dentro de esta metodología.
    - **Tasa real:** cuánto rinde aproximadamente después de descontar inflación.
    - **Score balanceado:** qué tan atractiva parece la opción combinando retorno, seguridad, liquidez y contexto.
    - **Plazo en días:** cuánto tiempo queda inmovilizado el dinero.

    **Importante:**  
    Todos los gráficos y tablas de esta página resumen el **conjunto de CDAs filtrados**
    que tienes activo en pantalla.
    """
)

with st.expander("Qué significa riesgo bajo, medio o alto en esta página"):
    st.markdown(
        """
        Esta clasificación es **interna al dashboard** y sirve para ordenar el universo visible.

        - **Bajo:** opción relativamente más defensiva frente al resto.
        - **Medio:** zona intermedia.
        - **Alto:** opción relativamente más exigente o más expuesta.

        No es una calificación oficial externa. Es una forma de comparar mejor las alternativas.
        """
    )

st.markdown("---")

# =========================
# CLASIFICACIONES AUXILIARES
# =========================
def categorizar_por_terciles(serie: pd.Series, labels=("Bajo", "Medio", "Alto")):
    serie = pd.to_numeric(serie, errors="coerce")

    if serie.dropna().empty:
        return pd.Series(["No disponible"] * len(serie), index=serie.index)

    # Si hay muy pocos valores únicos, qcut puede fallar.
    # En ese caso usamos ranking porcentual.
    try:
        cat = pd.qcut(serie, q=3, labels=labels, duplicates="drop")
        cat = cat.astype("object")
        cat = cat.where(pd.notna(cat), "No disponible")
        return cat
    except Exception:
        ranks = serie.rank(pct=True, method="average")
        out = pd.Series(index=serie.index, dtype="object")

        out[ranks <= 1/3] = labels[0]
        out[(ranks > 1/3) & (ranks <= 2/3)] = labels[1]
        out[ranks > 2/3] = labels[2]
        out = out.where(pd.notna(serie), "No disponible")
        return out


if "risk_score" in df_f.columns:
    df_f["categoria_riesgo"] = categorizar_por_terciles(
        df_f["risk_score"],
        labels=("Bajo", "Medio", "Alto")
    )
else:
    df_f["categoria_riesgo"] = "No disponible"

if "final_score_balanced" in df_f.columns:
    df_f["categoria_atractivo"] = categorizar_por_terciles(
        df_f["final_score_balanced"],
        labels=("Bajo", "Medio", "Alto")
    )
else:
    df_f["categoria_atractivo"] = "No disponible"

df_f["opcion_label"] = (
    df_f["entity_name"].fillna("Entidad")
    + " · "
    + df_f["term_days_floor"].fillna(0).astype(int).astype(str)
    + " días"
)

# =========================
# KPIS
# =========================
kpis = calcular_kpis_generales(df_f)

st.subheader("KPIs clave de riesgo y retorno")

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

col1.metric("CDAs analizados", f"{kpis.get('registros', 0)}")
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
# DESTACADOS
# =========================
st.subheader("Oportunidades destacadas del universo filtrado")

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
# MAPA PRINCIPAL
# =========================
st.subheader("Mapa principal del universo filtrado")

fig_rr = grafico_riesgo_retorno(
    df_f,
    x_col="risk_score",
    y_col="real_rate_pct",
    color_col="entity_type",
    size_col="final_score_balanced",
    hover_name="opcion_label",
    titulo="Cada punto representa un CDA del universo filtrado"
)
if fig_rr is not None:
    st.plotly_chart(fig_rr, use_container_width=True)

st.caption(
    "Lectura: cada punto es un CDA concreto. Más arriba = mejor tasa real. "
    "Más a la derecha = mayor riesgo relativo. Punto más grande = mejor score balanceado."
)

st.markdown("---")

# =========================
# CRUCE RIESGO / ATRACTIVO
# =========================
st.subheader("Cruce entre riesgo y atractivo del universo filtrado")

cruce = (
    df_f.groupby(["categoria_riesgo", "categoria_atractivo"], dropna=False)
    .size()
    .reset_index(name="cdas")
)

if not cruce.empty:
    orden_riesgo = ["Bajo", "Medio", "Alto"]
    orden_atractivo = ["Bajo", "Medio", "Alto"]

    # Completar combinaciones faltantes para que el gráfico siempre salga consistente
    base = pd.MultiIndex.from_product(
        [orden_riesgo, orden_atractivo],
        names=["categoria_riesgo", "categoria_atractivo"]
    ).to_frame(index=False)

    cruce = base.merge(
        cruce,
        on=["categoria_riesgo", "categoria_atractivo"],
        how="left"
    )
    cruce["cdas"] = cruce["cdas"].fillna(0).astype(int)

    total_cdas = cruce["cdas"].sum()
    cruce["pct_universo"] = ((cruce["cdas"] / total_cdas) * 100).round(1) if total_cdas > 0 else 0

    fig_cruce = px.bar(
        cruce,
        x="categoria_riesgo",
        y="cdas",
        color="categoria_atractivo",
        barmode="stack",
        text_auto=True,
        category_orders={
            "categoria_riesgo": orden_riesgo,
            "categoria_atractivo": orden_atractivo
        },
        title="Número de CDAs por categoría de riesgo y atractivo"
    )

    fig_cruce.update_layout(
        xaxis_title="Categoría de riesgo",
        yaxis_title="Número de CDAs",
        legend_title="Atractivo"
    )
    st.plotly_chart(fig_cruce, use_container_width=True)

    st.caption(
        "Este gráfico resume cuántos CDAs del universo filtrado caen en cada combinación "
        "de riesgo y atractivo. No representa una sola entidad."
    )

    tabla_cruce = cruce.rename(columns={
        "categoria_riesgo": "Riesgo",
        "categoria_atractivo": "Atractivo",
        "cdas": "Número de CDAs",
        "pct_universo": "% del universo"
    })
    st.dataframe(tabla_cruce, use_container_width=True)

st.markdown("---")

# =========================
# SEGMENTACIÓN ÚTIL
# =========================
st.subheader("Segmentación útil del universo filtrado")

resumen_tipo = calcular_resumen_tipo(df_f)
resumen_plazo = calcular_resumen_plazo(df_f)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Resumen por tipo de entidad")
    if not resumen_tipo.empty:
        st.dataframe(resumen_tipo, use_container_width=True)

with col2:
    st.markdown("### Resumen por perfil de plazo")
    if not resumen_plazo.empty:
        st.dataframe(resumen_plazo, use_container_width=True)

st.markdown("---")

# =========================
# DISTRIBUCIONES CON SENTIDO
# =========================
st.subheader("Distribuciones con lectura más clara")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_boxplot_por_categoria(
        df_f,
        categoria_col="term_profile",
        valor_col="real_rate_pct",
        titulo="Distribución de tasa real por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_boxplot_por_categoria(
        df_f,
        categoria_col="term_profile",
        valor_col="final_score_balanced",
        titulo="Distribución de score balanceado por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

# =========================
# RANKINGS ESPECÍFICOS
# =========================
st.markdown("---")
st.subheader("Rankings específicos más legibles")

top_defensivo = (
    df_f.sort_values(["final_score_conservative", "real_rate_pct"], ascending=[False, False])
    [["opcion_label", "entity_type", "final_score_conservative"]]
    .head(8)
    .rename(columns={"final_score_conservative": "score"})
)

top_retorno = (
    df_f.sort_values(["real_rate_pct", "final_score_balanced"], ascending=[False, False])
    [["opcion_label", "entity_type", "real_rate_pct"]]
    .head(8)
    .rename(columns={"real_rate_pct": "score"})
)

col1, col2 = st.columns(2)

with col1:
    fig_top_def = px.bar(
        top_defensivo.sort_values("score", ascending=True),
        x="score",
        y="opcion_label",
        color="entity_type",
        orientation="h",
        text_auto=".2f",
        title="Top CDAs defensivos del universo filtrado"
    )
    fig_top_def.update_layout(
        xaxis_title="Score conservador",
        yaxis_title=""
    )
    st.plotly_chart(fig_top_def, use_container_width=True)

with col2:
    fig_top_ret = px.bar(
        top_retorno.sort_values("score", ascending=True),
        x="score",
        y="opcion_label",
        color="entity_type",
        orientation="h",
        text_auto=".2f",
        title="Top CDAs por retorno real del universo filtrado"
    )
    fig_top_ret.update_layout(
        xaxis_title="Tasa real (%)",
        yaxis_title=""
    )
    st.plotly_chart(fig_top_ret, use_container_width=True)

st.caption(
    "Aquí cada barra representa una oportunidad concreta: entidad + plazo en días."
)

st.markdown("---")

# =========================
# TABLA PRINCIPAL
# =========================
st.subheader("Tabla de análisis del universo filtrado")

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
