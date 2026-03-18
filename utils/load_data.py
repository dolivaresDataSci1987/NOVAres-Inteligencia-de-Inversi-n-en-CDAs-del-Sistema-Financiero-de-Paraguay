from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _convertir_columnas_a_numerico(df, columnas):
    for col in columnas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _convertir_columnas_binarias(df, columnas):
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    return df


def _limpiar_columnas_texto(df, columnas):
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df.loc[df[col].isin(["nan", "None", ""]), col] = pd.NA
    return df


@st.cache_data
def cargar_datos_cda():
    path = DATA_DIR / "cda_master_dashboard.csv"
    df = pd.read_csv(path)

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

    columnas_binarias = [
        "withdrawal_allowed",
        "compound_interest",
        "guarantee",
        "auto_renewal",
    ]

    columnas_texto = [
        "entity_name",
        "entity_type",
        "instrument_name",
        "currency_code",
        "term_profile",
        "term_bucket",
        "size_bucket",
        "interest_payment_frequency",
        "recommendation_tag",
        "rate_source",
        "source_url",
        "data_note",
        "date_reference",
    ]

    df = _convertir_columnas_a_numerico(df, columnas_numericas)
    df = _convertir_columnas_binarias(df, columnas_binarias)
    df = _limpiar_columnas_texto(df, columnas_texto)

    return df


@st.cache_data
def cargar_comparativa_internacional():
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

    columnas_texto = [
        "country",
        "region",
        "market_risk_tier",
        "deposit_protection_scheme",
        "deposit_guarantee_limit",
        "relative_attractiveness_note",
    ]

    df = _convertir_columnas_a_numerico(df, columnas_numericas)
    df = _limpiar_columnas_texto(df, columnas_texto)

    return df


@st.cache_data
def cargar_diccionario():
    path = DATA_DIR / "cda_master_dashboard_dictionary.csv"
    return pd.read_csv(path)


def obtener_columnas(df):
    return df.columns.tolist()
