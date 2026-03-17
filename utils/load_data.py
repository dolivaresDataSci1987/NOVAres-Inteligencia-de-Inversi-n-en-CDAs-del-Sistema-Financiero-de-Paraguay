from pathlib import Path
import pandas as pd
import streamlit as st

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@st.cache_data
def cargar_datos_cda():
    """
    Carga el dataset maestro del dashboard.
    """
    path = DATA_DIR / "cda_master_dashboard.csv"
    df = pd.read_csv(path)

    # Limpieza ligera
    columnas_numericas = [
        "term_days_floor",
        "rate_nominal_pct",
        "rate_effective_pct",
        "inflation_yoy_pct",
        "real_rate_pct",
        "policy_rate_pct",
        "system_passive_rate_pct",
        "real_policy_rate",
        "cda_attractiveness_score",
        "risk_score",
        "risk_proxy",
        "liquidity_score",
        "solvency_score",
        "npl_score",
        "profitability_score",
        "early_withdrawal_penalty",
        "min_amount",
        "nominal_return_score_100",
        "real_return_score_100",
        "safety_score_100",
        "flexibility_score_100",
        "accessibility_score_100",
        "market_timing_score_100",
        "final_score_conservative",
        "final_score_balanced",
        "final_score_aggressive",
        "rank_conservative",
        "rank_balanced",
        "rank_aggressive",
    ]

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    columnas_binarias = [
        "withdrawal_allowed",
        "compound_interest",
        "guarantee",
        "auto_renewal",
    ]

    for col in columnas_binarias:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    return df


@st.cache_data
def cargar_comparativa_internacional():
    """
    Carga la base comparativa internacional.
    """
    path = DATA_DIR / "comparativa_cda_internacional_v2.csv"
    df = pd.read_csv(path)

    columnas_numericas = [
        "benchmark_rate_pct",
        "inflation_yoy_pct",
        "real_rate_proxy_pct",
        "policy_rate_pct",
        "rank_by_real_rate_proxy",
        "deposit_guarantee_usd",
        "guarantee_exists",
    ]

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


@st.cache_data
def cargar_diccionario():
    """
    Carga el diccionario de variables del dataset principal.
    """
    path = DATA_DIR / "cda_master_dashboard_dictionary.csv"
    df = pd.read_csv(path)
    return df


def filtrar_datos(
    df,
    monedas=None,
    tipos_entidad=None,
    perfiles_plazo=None
):
    """
    Aplica filtros simples al dataset principal.
    """
    df_filtrado = df.copy()

    if monedas:
        df_filtrado = df_filtrado[df_filtrado["currency_code"].isin(monedas)]

    if tipos_entidad:
        df_filtrado = df_filtrado[df_filtrado["entity_type"].isin(tipos_entidad)]

    if perfiles_plazo:
        df_filtrado = df_filtrado[df_filtrado["term_profile"].isin(perfiles_plazo)]

    return df_filtrado
