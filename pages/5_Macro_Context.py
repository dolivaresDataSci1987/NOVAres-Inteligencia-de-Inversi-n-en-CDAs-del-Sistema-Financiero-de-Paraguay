import streamlit as st
import pandas as pd

from utils.load_data import cargar_datos_cda, cargar_comparativa_internacional

st.set_page_config(page_title="Contexto Macro", page_icon="🌎", layout="wide")

st.title("Contexto macro y comparativa internacional")
st.markdown(
    """
    Analiza el posicionamiento de Paraguay frente a otros mercados a partir de
    variables macrofinancieras relevantes para la evaluación de CDAs.
    """
)

# =========================
# CARGA DE DATOS
# =========================
df_cda = cargar_datos_cda()
df_int = cargar_comparativa_internacional()

if df_int.empty:
    st.warning("No hay datos disponibles en la base de comparativa internacional.")
    st.stop()

df_int = df_int.copy()

# =========================
# FILTROS
# =========================
st.sidebar.header("Filtros")

if "region" in df_int.columns:
    regiones_disponibles = sorted(df_int["region"].dropna().unique())
else:
    regiones_disponibles = []

regiones = st.sidebar.multiselect(
    "Región",
    options=regiones_disponibles,
    default=regiones_disponibles
)

if regiones:
    df_int_f = df_int[df_int["region"].isin(regiones)].copy()
else:
    df_int_f = df_int.copy()

if df_int_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

# =========================
# LOCALIZAR PARAGUAY
# =========================
paraguay_row = pd.DataFrame()

if "country" in df_int_f.columns:
    paraguay_row = df_int_f[df_int_f["country"].astype(str).str.upper() == "PARAGUAY"].copy()

if paraguay_row.empty and "country" in df_int.columns:
    paraguay_row = df_int[df_int["country"].astype(str).str.upper() == "PARAGUAY"].copy()

# =========================
# KPIs GLOBALES
# =========================
st.subheader("KPIs macrofinancieros del universo comparado")

benchmark_promedio = (
    df_int_f["benchmark_rate_pct"].mean()
    if "benchmark_rate_pct" in df_int_f.columns else float("nan")
)
inflacion_promedio = (
    df_int_f["inflation_yoy_pct"].mean()
    if "inflation_yoy_pct" in df_int_f.columns else float("nan")
)
tasa_real_proxy_promedio = (
    df_int_f["real_rate_proxy_pct"].mean()
    if "real_rate_proxy_pct" in df_int_f.columns else float("nan")
)
policy_rate_promedio = (
    df_int_f["policy_rate_pct"].mean()
    if "policy_rate_pct" in df_int_f.columns else float("nan")
)
paises = df_int_f["country"].nunique() if "country" in df_int_f.columns else 0
regiones_n = df_int_f["region"].nunique() if "region" in df_int_f.columns else 0

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("Países comparados", f"{paises}")
col2.metric("Regiones representadas", f"{regiones_n}")
col3.metric("Benchmark promedio", f"{benchmark_promedio:.2f}%")

col4.metric("Inflación promedio", f"{inflacion_promedio:.2f}%")
col5.metric("Tasa real proxy promedio", f"{tasa_real_proxy_promedio:.2f}%")
col6.metric("Policy rate promedio", f"{policy_rate_promedio:.2f}%")

st.markdown("---")

# =========================
# PARAGUAY EN CONTEXTO
# =========================
st.subheader("Paraguay en contexto")

if not paraguay_row.empty:
    py = paraguay_row.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Paraguay · benchmark",
        f"{py['benchmark_rate_pct']:.2f}%"
        if "benchmark_rate_pct" in paraguay_row.columns and pd.notna(py["benchmark_rate_pct"])
        else "N/D"
    )
    col2.metric(
        "Paraguay · inflación",
        f"{py['inflation_yoy_pct']:.2f}%"
        if "inflation_yoy_pct" in paraguay_row.columns and pd.notna(py["inflation_yoy_pct"])
        else "N/D"
    )
    col3.metric(
        "Paraguay · tasa real proxy",
        f"{py['real_rate_proxy_pct']:.2f}%"
        if "real_rate_proxy_pct" in paraguay_row.columns and pd.notna(py["real_rate_proxy_pct"])
        else "N/D"
        )

    st.markdown("### Lectura estratégica de Paraguay")

    if "region" in paraguay_row.columns:
        st.write(f"**Región:** {py.get('region', 'N/D')}")
    if "market_risk_tier" in paraguay_row.columns:
        st.write(f"**Perfil de riesgo de mercado:** {py.get('market_risk_tier', 'N/D')}")
    if "deposit_protection_scheme" in paraguay_row.columns:
        st.write(f"**Esquema de protección de depósitos:** {py.get('deposit_protection_scheme', 'N/D')}")
    if "deposit_guarantee_limit" in paraguay_row.columns:
        st.write(f"**Límite de garantía:** {py.get('deposit_guarantee_limit', 'N/D')}")
    if "rank_by_real_rate_proxy" in paraguay_row.columns and pd.notna(py.get("rank_by_real_rate_proxy")):
        st.write(f"**Posición por tasa real proxy:** {int(py['rank_by_real_rate_proxy'])}")
    if "relative_attractiveness_note" in paraguay_row.columns:
        st.write(f"**Nota metodológica / atractividad relativa:** {py.get('relative_attractiveness_note', 'N/D')}")

else:
    st.info("No se encontró la fila de Paraguay en la comparativa internacional filtrada.")

st.markdown("---")

# =========================
# TABLA COMPARATIVA INTERNACIONAL
# =========================
st.subheader("Tabla comparativa internacional")

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

columnas_comp = [c for c in columnas_comp if c in df_int_f.columns]

if "rank_by_real_rate_proxy" in df_int_f.columns:
    tabla_comp = df_int_f[columnas_comp].sort_values("rank_by_real_rate_proxy", ascending=True)
else:
    tabla_comp = df_int_f[columnas_comp].copy()

st.dataframe(tabla_comp, use_container_width=True)

st.markdown("---")

# =========================
# RESUMEN POR REGIÓN
# =========================
st.subheader("Resumen por región")

if "region" in df_int_f.columns:
    agregaciones = {}

    if "country" in df_int_f.columns:
        agregaciones["paises"] = ("country", "nunique")
    if "benchmark_rate_pct" in df_int_f.columns:
        agregaciones["benchmark_promedio"] = ("benchmark_rate_pct", "mean")
    if "inflation_yoy_pct" in df_int_f.columns:
        agregaciones["inflacion_promedio"] = ("inflation_yoy_pct", "mean")
    if "real_rate_proxy_pct" in df_int_f.columns:
        agregaciones["tasa_real_proxy_promedio"] = ("real_rate_proxy_pct", "mean")
    if "policy_rate_pct" in df_int_f.columns:
        agregaciones["policy_rate_promedio"] = ("policy_rate_pct", "mean")

    resumen_region = (
        df_int_f.groupby("region", as_index=False)
        .agg(**agregaciones)
    )

    if "tasa_real_proxy_promedio" in resumen_region.columns:
        resumen_region = resumen_region.sort_values("tasa_real_proxy_promedio", ascending=False)

    st.dataframe(resumen_region, use_container_width=True)

st.markdown("---")

# =========================
# TOPS INTERNACIONALES
# =========================
st.subheader("Mercados destacados")

col1, col2, col3 = st.columns(3)

if "real_rate_proxy_pct" in df_int_f.columns:
    top_real = df_int_f.sort_values("real_rate_proxy_pct", ascending=False).iloc[0]
    with col1:
        st.markdown("### Mayor tasa real proxy")
        st.write(f"**País:** {top_real.get('country', 'N/D')}")
        st.write(f"**Región:** {top_real.get('region', 'N/D')}")
        st.write(f"**Tasa real proxy:** {top_real.get('real_rate_proxy_pct', float('nan')):.2f}%")
        st.write(f"**Benchmark:** {top_real.get('benchmark_rate_pct', float('nan')):.2f}%")

if "inflation_yoy_pct" in df_int_f.columns:
    top_inflacion = df_int_f.sort_values("inflation_yoy_pct", ascending=False).iloc[0]
    with col2:
        st.markdown("### Mayor inflación")
        st.write(f"**País:** {top_inflacion.get('country', 'N/D')}")
        st.write(f"**Región:** {top_inflacion.get('region', 'N/D')}")
        st.write(f"**Inflación:** {top_inflacion.get('inflation_yoy_pct', float('nan')):.2f}%")
        st.write(f"**Tasa real proxy:** {top_inflacion.get('real_rate_proxy_pct', float('nan')):.2f}%")

if "benchmark_rate_pct" in df_int_f.columns:
    top_benchmark = df_int_f.sort_values("benchmark_rate_pct", ascending=False).iloc[0]
    with col3:
        st.markdown("### Mayor benchmark")
        st.write(f"**País:** {top_benchmark.get('country', 'N/D')}")
        st.write(f"**Región:** {top_benchmark.get('region', 'N/D')}")
        st.write(f"**Benchmark:** {top_benchmark.get('benchmark_rate_pct', float('nan')):.2f}%")
        st.write(f"**Tasa real proxy:** {top_benchmark.get('real_rate_proxy_pct', float('nan')):.2f}%")

st.markdown("---")

# =========================
# VÍNCULO CON EL MERCADO PARAGUAYO DE CDAs
# =========================
st.subheader("Conexión con el mercado paraguayo de CDAs")

kpi_cda = {}

if "rate_nominal_pct" in df_cda.columns:
    kpi_cda["tasa_nominal_promedio_cda"] = df_cda["rate_nominal_pct"].mean()
if "real_rate_pct" in df_cda.columns:
    kpi_cda["tasa_real_promedio_cda"] = df_cda["real_rate_pct"].mean()
if "final_score_balanced" in df_cda.columns:
    kpi_cda["score_balanceado_promedio"] = df_cda["final_score_balanced"].mean()
if "entity_name" in df_cda.columns:
    kpi_cda["entidades"] = df_cda["entity_name"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Tasa nominal promedio CDA",
    f"{kpi_cda['tasa_nominal_promedio_cda']:.2f}%"
    if "tasa_nominal_promedio_cda" in kpi_cda else "N/D"
)
col2.metric(
    "Tasa real promedio CDA",
    f"{kpi_cda['tasa_real_promedio_cda']:.2f}%"
    if "tasa_real_promedio_cda" in kpi_cda else "N/D"
)
col3.metric(
    "Score balanceado promedio",
    f"{kpi_cda['score_balanceado_promedio']:.2f}"
    if "score_balanceado_promedio" in kpi_cda else "N/D"
)
col4.metric(
    "Entidades en la base local",
    f"{kpi_cda['entidades']}"
    if "entidades" in kpi_cda else "N/D"
)

st.markdown(
    """
    Esta lectura conjunta permite interpretar el atractivo de los CDAs paraguayos no solo
    en términos absolutos, sino también relativos: frente al entorno macro, frente a la inflación
    y frente al posicionamiento internacional de Paraguay dentro del conjunto comparado.
    """
)

st.markdown("---")

# =========================
# LECTURA INTERPRETATIVA FINAL
# =========================
st.subheader("Lectura interpretativa final")

if not paraguay_row.empty:
    py = paraguay_row.iloc[0]

    benchmark_txt = (
        f"{py['benchmark_rate_pct']:.2f}%"
        if "benchmark_rate_pct" in paraguay_row.columns and pd.notna(py["benchmark_rate_pct"])
        else "N/D"
    )
    inflacion_txt = (
        f"{py['inflation_yoy_pct']:.2f}%"
        if "inflation_yoy_pct" in paraguay_row.columns and pd.notna(py["inflation_yoy_pct"])
        else "N/D"
    )
    real_txt = (
        f"{py['real_rate_proxy_pct']:.2f}%"
        if "real_rate_proxy_pct" in paraguay_row.columns and pd.notna(py["real_rate_proxy_pct"])
        else "N/D"
    )
    riesgo_txt = py.get("market_risk_tier", "N/D")

    st.write(
        f"Paraguay presenta un benchmark de **{benchmark_txt}**, una inflación de "
        f"**{inflacion_txt}** y una tasa real proxy de **{real_txt}**. "
        f"En la comparativa internacional filtrada, esto sitúa al país dentro de un entorno "
        f"de riesgo de mercado **{riesgo_txt}**."
    )

    if "relative_attractiveness_note" in paraguay_row.columns:
        st.write(
            f"Desde una lectura estratégica, la base internacional sugiere que Paraguay: "
            f"**{py.get('relative_attractiveness_note', 'N/D')}**"
        )

st.write(
    "Para la evaluación de CDAs, este contexto importa porque determina cuánto valor real "
    "puede capturar el inversor una vez descontada la inflación y cómo se posiciona el mercado local "
    "frente a otras alternativas regionales e internacionales."
)
