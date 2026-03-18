import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda
from utils.metrics import (
    calcular_kpis_generales,
    calcular_resumen_tipo,
    calcular_resumen_plazo,
    calcular_percentiles_mercado,
)
from utils.insights import generar_insight_overview
from utils.charts import (
    grafico_riesgo_retorno,
    grafico_plazo_vs_tasa,
    grafico_score_por_tipo,
    grafico_boxplot_por_categoria,
    grafico_heatmap_promedios,
    grafico_conteo_categoria,
    grafico_barras_por_categoria,
    grafico_tasa_nominal_por_plazo,
)

st.set_page_config(page_title="Visión General del Mercado de CDA en Paraguay", page_icon="📊", layout="wide")

st.title("Visión General del Mercado de CDA en Paraguay")
st.markdown(
    """
    Vista general analítica del mercado de CDAs en Paraguay.
    Aquí se explora la estructura de oferta, la dispersión de tasas,
    el trade-off riesgo-retorno y la segmentación por plazo, perfil de pago y tipo de entidad.
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
filtros = render_filtros_cda(df, key_prefix="VisiónGeneral")
df_f = aplicar_filtros_cda(df, filtros)

if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# =========================
# GUÍA DE LECTURA
# =========================
st.subheader("Guía rápida para interpretar esta página")

st.markdown(
    """
    Esta página está pensada para que cualquier persona pueda entender, de forma simple,
    cómo está compuesto el mercado de CDAs y qué oportunidades parecen más atractivas.

    **Qué conviene mirar primero:**
    - **Tasa nominal:** cuánto paga el instrumento.
    - **Tasa real:** cuánto rinde realmente después de descontar inflación.
    - **Riesgo:** qué tan sólida o incierta parece la oportunidad dentro de la metodología.
    - **Score balanceado:** una nota sintética que combina retorno, seguridad, liquidez y otros factores.
    - **Monto mínimo:** cuánto dinero necesitas para entrar.
    """
)

st.markdown("---")

# =========================
# DICCIONARIO BÁSICO
# =========================
st.subheader("Diccionario básico de términos")

diccionario_simple = pd.DataFrame([
    {
        "Término": "Tasa nominal",
        "Qué significa en lenguaje simple": "Es el porcentaje que paga el CDA. Es la rentabilidad anunciada, sin descontar inflación."
    },
    {
        "Término": "Tasa nominal promedio",
        "Qué significa en lenguaje simple": "Es el promedio de las tasas nominales del conjunto de CDAs que estás viendo con los filtros aplicados."
    },
    {
        "Término": "Tasa real",
        "Qué significa en lenguaje simple": "Es la rentabilidad aproximada una vez descontada la inflación. Ayuda a ver si el dinero realmente gana poder de compra."
    },
    {
        "Término": "Riesgo",
        "Qué significa en lenguaje simple": "Es una medida interna del dashboard para resumir qué tan defensiva o incierta parece una opción. En general, menor valor implica menor riesgo relativo."
    },
    {
        "Término": "Score balanceado",
        "Qué significa en lenguaje simple": "Es una puntuación compuesta que resume qué tan atractiva es una oportunidad considerando varias dimensiones a la vez: retorno, seguridad, liquidez, flexibilidad y contexto."
    },
    {
        "Término": "Score conservador",
        "Qué significa en lenguaje simple": "Da más peso a seguridad, liquidez y estabilidad. Sirve para perfiles que priorizan proteger el capital."
    },
    {
        "Término": "Score agresivo",
        "Qué significa en lenguaje simple": "Da más peso al retorno potencial. Sirve para perfiles que buscan más rentabilidad y toleran más riesgo."
    },
    {
        "Término": "Monto mínimo",
        "Qué significa en lenguaje simple": "Es la cantidad mínima de dinero que necesitas para invertir en ese CDA."
    },
    {
        "Término": "Monto mínimo promedio",
        "Qué significa en lenguaje simple": "Es el promedio de los montos mínimos exigidos por las opciones visibles en pantalla."
    },
    {
        "Término": "Perfil de plazo",
        "Qué significa en lenguaje simple": "Agrupa los instrumentos según la duración de la inversión."
    },
    {
        "Término": "Short term / Corto plazo",
        "Qué significa en lenguaje simple": "Instrumentos con duración más corta. Suelen dar más flexibilidad, aunque no siempre la mejor tasa."
    },
    {
        "Término": "Medium term / Plazo medio",
        "Qué significa en lenguaje simple": "Instrumentos de duración intermedia. Buscan un punto medio entre retorno y flexibilidad."
    },
    {
        "Término": "Long term / Largo plazo",
        "Qué significa en lenguaje simple": "Instrumentos pensados para dejar el dinero más tiempo invertido. A veces ofrecen mejores tasas, pero con menos flexibilidad."
    },
    {
        "Término": "Liquidez",
        "Qué significa en lenguaje simple": "Refleja qué tan fácil es recuperar o mover el dinero, o qué tan rígido es el producto."
    },
    {
        "Término": "Solvencia",
        "Qué significa en lenguaje simple": "Resume la fortaleza financiera relativa de la entidad dentro de la metodología del dashboard."
    },
    {
        "Término": "Perfil de pago de interés",
        "Qué significa en lenguaje simple": "Indica cada cuánto se pagan los intereses: por ejemplo, al vencimiento, mensualmente o con otra frecuencia."
    },
])

st.dataframe(diccionario_simple, use_container_width=True, hide_index=True)

with st.expander("Cómo interpretar el score del dashboard"):
    st.markdown(
        """
        El **score** no representa una garantía ni una recomendación financiera absoluta.

        Sirve como una **herramienta comparativa interna** para ordenar oportunidades
        dentro del universo analizado.

        **Lectura práctica del score:**
        - **Score alto:** la opción destaca relativamente frente a otras del mismo universo.
        - **Score medio:** la opción puede ser razonable, pero no sobresale claramente.
        - **Score bajo:** la opción parece menos atractiva frente a alternativas comparables.

        El score cambia según el perfil:
        - **Conservador:** prioriza seguridad y liquidez.
        - **Balanceado:** busca equilibrio entre retorno y estabilidad.
        - **Agresivo:** prioriza más la rentabilidad potencial.
        """
    )

st.markdown("---")

# =========================
# KPIS
# =========================
kpis = calcular_kpis_generales(df_f)

st.subheader("KPIs del mercado filtrado")

col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

col1.metric("Registros", f"{kpis.get('registros', 0)}")
col2.metric("Entidades", f"{kpis.get('entidades', 0)}")
col3.metric("Tipos de entidad", f"{kpis.get('tipos_entidad', 0)}")
col4.metric(
    "Tasa nominal promedio",
    f"{kpis.get('tasa_nominal_promedio', float('nan')):.2f}%"
    if pd.notna(kpis.get("tasa_nominal_promedio")) else "N/D"
)

col5.metric(
    "Tasa real promedio",
    f"{kpis.get('tasa_real_promedio', float('nan')):.2f}%"
    if pd.notna(kpis.get("tasa_real_promedio")) else "N/D"
)
col6.metric(
    "Riesgo promedio",
    f"{kpis.get('riesgo_promedio', float('nan')):.2f}"
    if pd.notna(kpis.get("riesgo_promedio")) else "N/D"
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
st.info(generar_insight_overview(df_f))

st.markdown("---")

# =========================
# ESTRUCTURA DEL MERCADO
# =========================
st.subheader("Estructura del mercado")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_tasa_nominal_por_plazo(
        df_f,
        plazo_col="term_profile",
        tasa_col="rate_nominal_pct",
        titulo="Distribución de tasa nominal por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_score_por_tipo(
        df_f,
        tipo_col="entity_type",
        score_col="final_score_balanced",
        titulo="Score balanceado promedio por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = grafico_conteo_categoria(
        df_f,
        categoria_col="interest_payment_frequency",
        titulo="Distribución por perfil de pago de interés"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col4:
    fig = grafico_barras_por_categoria(
        df_f,
        categoria_col="term_profile",
        valor_col="rate_nominal_pct",
        titulo="Tasa nominal promedio por perfil de plazo"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# MAPAS ANALÍTICOS
# =========================
st.subheader("Mapas analíticos")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_riesgo_retorno(
        df_f,
        x_col="risk_score",
        y_col="real_rate_pct",
        color_col="entity_type",
        size_col="final_score_balanced",
        hover_name="entity_name",
        titulo="Mapa riesgo vs retorno real"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_plazo_vs_tasa(
        df_f,
        x_col="term_days_floor",
        y_col="rate_nominal_pct",
        color_col="entity_type",
        hover_name="entity_name",
        titulo="Plazo vs tasa nominal"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# SEGMENTACIÓN
# =========================
st.subheader("Segmentación del mercado")

col1, col2 = st.columns(2)

with col1:
    fig = grafico_boxplot_por_categoria(
        df_f,
        categoria_col="entity_type",
        valor_col="rate_nominal_pct",
        titulo="Distribución de tasa nominal por tipo de entidad"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = grafico_boxplot_por_categoria(
        df_f,
        categoria_col="interest_payment_frequency",
        valor_col="real_rate_pct",
        titulo="Distribución de tasa real por perfil de pago"
    )
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

fig = grafico_heatmap_promedios(
    df_f,
    row_col="entity_type",
    col_col="term_profile",
    value_col="final_score_balanced",
    titulo="Heatmap · score balanceado promedio por tipo de entidad y plazo"
)
if fig is not None:
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================
# RESÚMENES TABULARES
# =========================
st.subheader("Resúmenes analíticos")

resumen_tipo = calcular_resumen_tipo(df_f)
resumen_plazo = calcular_resumen_plazo(df_f)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Por tipo de entidad")
    if not resumen_tipo.empty:
        st.dataframe(resumen_tipo, use_container_width=True)

with col2:
    st.markdown("### Por perfil de plazo")
    if not resumen_plazo.empty:
        st.dataframe(resumen_plazo, use_container_width=True)

st.markdown("---")

# =========================
# PERCENTILES
# =========================
st.subheader("Percentiles del mercado")

percentiles_tasa = calcular_percentiles_mercado(df_f, "rate_nominal_pct")
percentiles_real = calcular_percentiles_mercado(df_f, "real_rate_pct")
percentiles_score = calcular_percentiles_mercado(df_f, "final_score_balanced")

tabla_percentiles = pd.DataFrame(
    [
        {"variable": "Tasa nominal", **percentiles_tasa},
        {"variable": "Tasa real", **percentiles_real},
        {"variable": "Score balanceado", **percentiles_score},
    ]
)

st.dataframe(tabla_percentiles, use_container_width=True)

st.markdown("---")

# =========================
# TABLA DETALLADA
# =========================
st.subheader("Tabla detallada del mercado")

columnas_mostrar = [
    "entity_name",
    "entity_type",
    "instrument_name",
    "term_profile",
    "term_bucket",
    "size_bucket",
    "interest_payment_frequency",
    "term_days_floor",
    "min_amount",
    "rate_nominal_pct",
    "rate_effective_pct",
    "real_rate_pct",
    "risk_score",
    "liquidity_score",
    "solvency_score",
    "accessibility_score_100",
    "final_score_balanced",
    "recommendation_tag",
]

columnas_mostrar = [c for c in columnas_mostrar if c in df_f.columns]

tabla = (
    df_f[columnas_mostrar]
    .sort_values(["final_score_balanced", "real_rate_pct"], ascending=[False, False])
    .reset_index(drop=True)
)

st.dataframe(tabla, use_container_width=True)
