import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda
from utils.metrics import (
    calcular_kpis_ranking,
    calcular_resumen_tipo,
    calcular_resumen_plazo,
)
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
    Esta página ordena las oportunidades de inversión en CDAs según el perfil de inversión seleccionado.
    El objetivo no es solo mostrar qué opción sale primera, sino ayudarte a entender
    **por qué destaca**, **qué tipo de inversor encaja mejor con ella** y **qué alternativas similares**
    también merecen atención.
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
st.subheader("Selecciona el perfil de inversión")

perfil = st.radio(
    "Perfil",
    options=["Conservador", "Balanceado", "Agresivo"],
    horizontal=True
)

if perfil == "Conservador":
    score_col = "final_score_conservative"
    rank_col = "rank_conservative"
    titulo_score = "Score conservador"
    explicacion_perfil = (
        "Este perfil prioriza **proteger el capital**, reducir la exposición al riesgo "
        "y dar más peso a seguridad, liquidez y estabilidad."
    )
elif perfil == "Balanceado":
    score_col = "final_score_balanced"
    rank_col = "rank_balanced"
    titulo_score = "Score balanceado"
    explicacion_perfil = (
        "Este perfil busca un **equilibrio entre rentabilidad y prudencia**. "
        "No mira solo cuánto paga el CDA, sino también su riesgo, liquidez y solidez relativa."
    )
else:
    score_col = "final_score_aggressive"
    rank_col = "rank_aggressive"
    titulo_score = "Score agresivo"
    explicacion_perfil = (
        "Este perfil da más peso a la **rentabilidad potencial**. "
        "Acepta más volatilidad o menor componente defensivo a cambio de buscar retornos más altos."
    )

if score_col not in df_f.columns:
    st.warning(f"No existe la columna {score_col} en la base.")
    st.stop()

df_rank = df_f.sort_values(score_col, ascending=False).reset_index(drop=True)

# =========================
# GUÍA DE LECTURA
# =========================
st.subheader("Cómo interpretar esta página")

st.markdown(
    f"""
    En esta vista estás viendo el mercado filtrado ordenado según el criterio de un perfil
    **{perfil.lower()}**.

    **Qué significa esto en la práctica:**
    - La opción que aparece arriba **no es solo la que más paga**, sino la que mejor encaja con la lógica del perfil elegido.
    - Un CDA puede tener una tasa alta, pero no necesariamente quedar arriba si su riesgo, liquidez o accesibilidad son peores.
    - Aquí conviene fijarse en cuatro cosas a la vez:
      - **score del perfil elegido**,
      - **tasa nominal**,
      - **tasa real**,
      - **plazo en días**.

    **Lectura del perfil {perfil.lower()}:**  
    {explicacion_perfil}
    """
)

with st.expander("Qué estás viendo exactamente en el ranking"):
    st.markdown(
        """
        Este ranking compara oportunidades dentro del universo filtrado y las ordena de mejor a peor
        según el perfil seleccionado.

        **Cómo leer las posiciones altas:**
        - Una opción alta en el ranking suele combinar una buena rentabilidad con una estructura más favorable
          para ese perfil.
        - No siempre significa que sea la mejor para todo el mundo, sino que destaca **relativamente**
          frente a las otras opciones visibles.

        **Cómo usar esta página bien:**
        - Mira primero el **top 1** y el **top 3**.
        - Después compara el plazo en días, la tasa real y el riesgo.
        - Finalmente revisa si el tipo de entidad o el plazo cambian mucho la calidad promedio del ranking.
        """
    )

st.markdown("---")

# =========================
# KPIs
# =========================
kpis = calcular_kpis_ranking(df_rank, score_col=score_col)

st.subheader("KPIs del ranking filtrado")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros analizados", f"{kpis.get('registros', 0)}")
col2.metric("Entidades analizadas", f"{kpis.get('entidades', 0)}")
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

st.subheader(f"Mejor oportunidad para perfil {perfil.lower()}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Entidad", top.get("entity_name", "N/D"))
col2.metric("Plazo", f"{int(top.get('term_days_floor', 0))} días" if pd.notna(top.get("term_days_floor")) else "N/D")
col3.metric("Tasa nominal", f"{top.get('rate_nominal_pct', float('nan')):.2f}%")
col4.metric(titulo_score, f"{top.get(score_col, float('nan')):.2f}")

st.markdown(
    f"""
    **Instrumento:** {top.get('instrument_name', 'N/D')}  
    **Lectura rápida:** Este es un **CDA de {int(top.get('term_days_floor', 0)) if pd.notna(top.get('term_days_floor')) else 'N/D'} días**
    con perfil de plazo **{top.get('term_profile', 'N/D')}** y categoría **{top.get('term_bucket', 'N/D')}**.  
    **Tipo de entidad:** {top.get('entity_type', 'N/D')}  
    **Tasa real:** {top.get('real_rate_pct', float('nan')):.2f}%  
    **Riesgo:** {top.get('risk_score', float('nan')):.2f}  
    **Liquidez:** {top.get('liquidity_score', float('nan')):.2f}  
    **Solvencia:** {top.get('solvency_score', float('nan')):.2f}  
    **Monto mínimo:** {top.get('min_amount', float('nan')):,.0f}  
    **Etiqueta metodológica:** {top.get('recommendation_tag', 'N/D')}
    """
)

st.info(generar_insight_ranking(df_rank, perfil=perfil, score_col=score_col))

st.markdown("---")

# =========================
# TOP 3 DESTACADO
# =========================
st.subheader("Top 3 oportunidades más interesantes")

top3 = df_rank.head(3).copy()

cols = st.columns(3)

for i, (_, row) in enumerate(top3.iterrows()):
    with cols[i]:
        st.markdown(f"### #{i+1} · {row.get('entity_name', 'N/D')}")
        st.write(f"**Instrumento:** {row.get('instrument_name', 'N/D')}")
        st.write(
            f"**Qué es:** CDA de **{int(row.get('term_days_floor', 0)) if pd.notna(row.get('term_days_floor')) else 'N/D'} días**"
        )
        st.write(f"**Perfil de plazo:** {row.get('term_profile', 'N/D')}")
        st.write(f"**Tasa nominal:** {row.get('rate_nominal_pct', float('nan')):.2f}%")
        st.write(f"**Tasa real:** {row.get('real_rate_pct', float('nan')):.2f}%")
        st.write(f"**{titulo_score}:** {row.get(score_col, float('nan')):.2f}")
        st.write(f"**Riesgo:** {row.get('risk_score', float('nan')):.2f}")
        st.write(f"**Monto mínimo:** {row.get('min_amount', float('nan')):,.0f}")

st.markdown("---")

# =========================
# TOP 10 VISUAL
# =========================
st.subheader(f"Top 10 visual · Perfil {perfil.lower()}")

df_rank = df_rank.copy()
df_rank["ranking_label"] = (
    df_rank["entity_name"].fillna("Entidad")
    + " · "
    + df_rank["term_days_floor"].fillna(0).astype(int).astype(str)
    + " días"
)

fig = grafico_top_ranking(
    df_rank,
    score_col=score_col,
    nombre_col="ranking_label",
    top_n=10,
    titulo=f"Top 10 por {titulo_score.lower()}",
    color_col="entity_type"
)
if fig is not None:
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    **Cómo leer este gráfico:**  
    Cada barra representa una oportunidad concreta. Cuanto más larga es la barra,
    mejor posicionada está esa opción para el perfil seleccionado.
    """
)

columnas_top = [
    rank_col,
    "entity_name",
    "instrument_name",
    "term_days_floor",
    "term_profile",
    "term_bucket",
    "entity_type",
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

tabla_top = df_rank[columnas_top].head(10).copy()
tabla_top = tabla_top.rename(columns={
    rank_col: "Posición",
    "entity_name": "Entidad",
    "instrument_name": "Instrumento",
    "term_days_floor": "Días",
    "term_profile": "Perfil de plazo",
    "term_bucket": "Bucket plazo",
    "entity_type": "Tipo de entidad",
    "min_amount": "Monto mínimo",
    "rate_nominal_pct": "Tasa nominal (%)",
    "real_rate_pct": "Tasa real (%)",
    "risk_score": "Riesgo",
    "liquidity_score": "Liquidez",
    "solvency_score": "Solvencia",
    score_col: titulo_score,
    "recommendation_tag": "Etiqueta",
})

st.dataframe(tabla_top, use_container_width=True)

st.markdown("---")

# =========================
# DESCOMPOSICIÓN DEL LÍDER
# =========================
st.subheader("Por qué sale primero esta opción")

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
        "Componente": [
            "Retorno nominal",
            "Retorno real",
            "Seguridad",
            "Flexibilidad",
            "Accesibilidad",
            "Timing de mercado",
        ][:len(componentes)],
        "Score": [top.get(c, float("nan")) for c in componentes]
    }).sort_values("Score", ascending=False)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.bar_chart(df_componentes.set_index("Componente"))

    with col2:
        st.dataframe(df_componentes, use_container_width=True)

st.markdown("---")

# =========================
# LECTURA POR SEGMENTOS
# =========================
st.subheader("Cómo cambia el ranking según el tipo de oportunidad")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_barras_por_categoria(
        df_rank,
        categoria_col="term_profile",
        valor_col=score_col,
        titulo=f"{titulo_score} promedio por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_barras_por_categoria(
        df_rank,
        categoria_col="entity_type",
        valor_col=score_col,
        titulo=f"{titulo_score} promedio por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

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
# MEJORES POR PLAZO
# =========================
st.subheader("Mejores oportunidades por perfil de plazo")

if "term_profile" in df_rank.columns:
    mejores_por_plazo = (
        df_rank.sort_values(score_col, ascending=False)
        .groupby("term_profile", as_index=False)
        .first()
    )

    columnas_plazo = [
        "term_profile",
        "entity_name",
        "instrument_name",
        "term_days_floor",
        "entity_type",
        "rate_nominal_pct",
        "real_rate_pct",
        "risk_score",
        score_col,
        "recommendation_tag",
    ]
    columnas_plazo = [c for c in columnas_plazo if c in mejores_por_plazo.columns]

    tabla_plazo = mejores_por_plazo[columnas_plazo].copy()
    tabla_plazo = tabla_plazo.rename(columns={
        "term_profile": "Perfil de plazo",
        "entity_name": "Entidad",
        "instrument_name": "Instrumento",
        "term_days_floor": "Días",
        "entity_type": "Tipo de entidad",
        "rate_nominal_pct": "Tasa nominal (%)",
        "real_rate_pct": "Tasa real (%)",
        "risk_score": "Riesgo",
        score_col: titulo_score,
        "recommendation_tag": "Etiqueta",
    })

    st.dataframe(tabla_plazo, use_container_width=True)

st.markdown("---")

# =========================
# RESÚMENES
# =========================
st.subheader("Resúmenes del ranking")

resumen_tipo = calcular_resumen_tipo(df_rank)
resumen_plazo = calcular_resumen_plazo(df_rank)

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
# TABLA COMPLETA
# =========================
st.subheader("Tabla completa del ranking")

columnas_tabla = [
    rank_col,
    "entity_name",
    "entity_type",
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

tabla_completa = df_rank[columnas_tabla].copy()
tabla_completa = tabla_completa.rename(columns={
    rank_col: "Posición",
    "entity_name": "Entidad",
    "entity_type": "Tipo de entidad",
    "instrument_name": "Instrumento",
    "term_profile": "Perfil de plazo",
    "term_bucket": "Bucket plazo",
    "term_days_floor": "Días",
    "size_bucket": "Tamaño entidad",
    "interest_payment_frequency": "Pago de interés",
    "min_amount": "Monto mínimo",
    "rate_nominal_pct": "Tasa nominal (%)",
    "rate_effective_pct": "Tasa efectiva (%)",
    "real_rate_pct": "Tasa real (%)",
    "risk_score": "Riesgo",
    "risk_proxy": "Proxy de riesgo",
    "liquidity_score": "Liquidez",
    "solvency_score": "Solvencia",
    "profitability_score": "Rentabilidad",
    "accessibility_score_100": "Accesibilidad",
    "nominal_return_score_100": "Score retorno nominal",
    "real_return_score_100": "Score retorno real",
    "safety_score_100": "Score seguridad",
    "flexibility_score_100": "Score flexibilidad",
    "market_timing_score_100": "Score timing",
    score_col: titulo_score,
    "recommendation_tag": "Etiqueta",
})

st.dataframe(tabla_completa, use_container_width=True)
