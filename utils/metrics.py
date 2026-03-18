import pandas as pd
import numpy as np


def _safe_mean(df: pd.DataFrame, col: str):
    return df[col].mean() if col in df.columns and not df[col].dropna().empty else np.nan


def _safe_max(df: pd.DataFrame, col: str):
    return df[col].max() if col in df.columns and not df[col].dropna().empty else np.nan


def _safe_min(df: pd.DataFrame, col: str):
    return df[col].min() if col in df.columns and not df[col].dropna().empty else np.nan


def _safe_nunique(df: pd.DataFrame, col: str):
    return df[col].nunique() if col in df.columns else 0


def _safe_pct(mask):
    if len(mask) == 0:
        return 0.0
    return float(mask.mean() * 100)


def calcular_kpis_generales(df: pd.DataFrame):
    kpis = {
        "registros": len(df),
        "entidades": _safe_nunique(df, "entity_name"),
        "tipos_entidad": _safe_nunique(df, "entity_type"),
        "monedas": _safe_nunique(df, "currency_code"),
        "tasa_nominal_promedio": _safe_mean(df, "rate_nominal_pct"),
        "tasa_nominal_maxima": _safe_max(df, "rate_nominal_pct"),
        "tasa_real_promedio": _safe_mean(df, "real_rate_pct"),
        "score_balanceado_promedio": _safe_mean(df, "final_score_balanced"),
        "score_conservador_promedio": _safe_mean(df, "final_score_conservative"),
        "score_agresivo_promedio": _safe_mean(df, "final_score_aggressive"),
        "riesgo_promedio": _safe_mean(df, "risk_score"),
        "liquidez_promedio": _safe_mean(df, "liquidity_score"),
        "solvencia_promedio": _safe_mean(df, "solvency_score"),
        "monto_minimo_promedio": _safe_mean(df, "min_amount"),
    }

    if "real_rate_pct" in df.columns:
        kpis["pct_tasa_real_positiva"] = _safe_pct(df["real_rate_pct"].fillna(-999) > 0)

    if "guarantee" in df.columns:
        kpis["pct_garantizados"] = _safe_pct(df["guarantee"].fillna(0) == 1)

    if "withdrawal_allowed" in df.columns:
        kpis["pct_con_rescate"] = _safe_pct(df["withdrawal_allowed"].fillna(0) == 1)

    if "compound_interest" in df.columns:
        kpis["pct_con_interes_compuesto"] = _safe_pct(df["compound_interest"].fillna(0) == 1)

    if "final_score_balanced" in df.columns:
        kpis["spread_score_balanceado"] = _safe_max(df, "final_score_balanced") - _safe_min(df, "final_score_balanced")

    if "rate_nominal_pct" in df.columns:
        kpis["spread_tasa_nominal"] = _safe_max(df, "rate_nominal_pct") - _safe_min(df, "rate_nominal_pct")

    return kpis


def calcular_kpis_ranking(df: pd.DataFrame, score_col: str):
    out = {
        "registros": len(df),
        "entidades": _safe_nunique(df, "entity_name"),
        "score_promedio": _safe_mean(df, score_col),
        "score_maximo": _safe_max(df, score_col),
        "score_minimo": _safe_min(df, score_col),
        "tasa_real_promedio": _safe_mean(df, "real_rate_pct"),
        "riesgo_promedio": _safe_mean(df, "risk_score"),
    }

    if score_col in df.columns and not df[score_col].dropna().empty:
        out["percentil_top"] = float((df[score_col].rank(pct=True).max()) * 100)

    return out


def calcular_resumen_tipo(df: pd.DataFrame):
    if "entity_type" not in df.columns:
        return pd.DataFrame()

    agg = {
        "registros": ("entity_name", "count"),
        "entidades": ("entity_name", "nunique"),
    }

    columnas_map = {
        "rate_nominal_pct": "tasa_nominal_promedio",
        "real_rate_pct": "tasa_real_promedio",
        "risk_score": "riesgo_promedio",
        "liquidity_score": "liquidez_promedio",
        "solvency_score": "solvencia_promedio",
        "final_score_conservative": "score_conservador_promedio",
        "final_score_balanced": "score_balanceado_promedio",
        "final_score_aggressive": "score_agresivo_promedio",
        "min_amount": "monto_minimo_promedio",
    }

    for col, alias in columnas_map.items():
        if col in df.columns:
            agg[alias] = (col, "mean")

    resumen = df.groupby("entity_type", as_index=False).agg(**agg)

    if "score_balanceado_promedio" in resumen.columns:
        resumen = resumen.sort_values("score_balanceado_promedio", ascending=False)

    return resumen


def calcular_resumen_moneda(df: pd.DataFrame):
    if "currency_code" not in df.columns:
        return pd.DataFrame()

    agg = {
        "registros": ("entity_name", "count"),
        "entidades": ("entity_name", "nunique"),
    }

    columnas_map = {
        "rate_nominal_pct": "tasa_nominal_promedio",
        "real_rate_pct": "tasa_real_promedio",
        "risk_score": "riesgo_promedio",
        "final_score_balanced": "score_balanceado_promedio",
        "min_amount": "monto_minimo_promedio",
    }

    for col, alias in columnas_map.items():
        if col in df.columns:
            agg[alias] = (col, "mean")

    resumen = df.groupby("currency_code", as_index=False).agg(**agg)

    if "score_balanceado_promedio" in resumen.columns:
        resumen = resumen.sort_values("score_balanceado_promedio", ascending=False)

    return resumen


def calcular_resumen_plazo(df: pd.DataFrame):
    if "term_profile" not in df.columns:
        return pd.DataFrame()

    agg = {
        "registros": ("entity_name", "count"),
    }

    columnas_map = {
        "term_days_floor": "plazo_promedio_dias",
        "rate_nominal_pct": "tasa_nominal_promedio",
        "real_rate_pct": "tasa_real_promedio",
        "risk_score": "riesgo_promedio",
        "final_score_balanced": "score_balanceado_promedio",
        "min_amount": "monto_minimo_promedio",
    }

    for col, alias in columnas_map.items():
        if col in df.columns:
            agg[alias] = (col, "mean")

    resumen = df.groupby("term_profile", as_index=False).agg(**agg)

    if "score_balanceado_promedio" in resumen.columns:
        resumen = resumen.sort_values("score_balanceado_promedio", ascending=False)

    return resumen


def calcular_percentiles_mercado(df: pd.DataFrame, col: str):
    if col not in df.columns or df[col].dropna().empty:
        return {}

    serie = df[col].dropna()
    return {
        "min": float(serie.min()),
        "p25": float(serie.quantile(0.25)),
        "mediana": float(serie.quantile(0.50)),
        "p75": float(serie.quantile(0.75)),
        "max": float(serie.max()),
        "std": float(serie.std()) if len(serie) > 1 else 0.0
    }


def calcular_matriz_riesgo_atractivo(df: pd.DataFrame):
    if "categoria_riesgo" not in df.columns or "categoria_atractivo" not in df.columns:
        return pd.DataFrame()

    matriz = (
        df.groupby(["categoria_riesgo", "categoria_atractivo"], dropna=False)
        .size()
        .reset_index(name="registros")
    )
    return matriz


def obtener_top_oportunidad(df: pd.DataFrame, score_col: str = "final_score_balanced"):
    if df.empty or score_col not in df.columns:
        return pd.Series(dtype="object")
    return df.sort_values(score_col, ascending=False).iloc[0]


def obtener_mejores_por_dimension(df: pd.DataFrame):
    out = {}

    if df.empty:
        return out

    mappings = {
        "mejor_balanceado": ("final_score_balanced", False),
        "mejor_conservador": ("final_score_conservative", False),
        "mejor_agresivo": ("final_score_aggressive", False),
        "mayor_tasa_nominal": ("rate_nominal_pct", False),
        "mayor_tasa_real": ("real_rate_pct", False),
        "menor_riesgo": ("risk_score", True),
        "mayor_liquidez": ("liquidity_score", False),
        "mayor_solvencia": ("solvency_score", False),
        "mayor_accesibilidad": ("accessibility_score_100", False),
    }

    for nombre, (col, asc) in mappings.items():
        if col in df.columns and not df[col].dropna().empty:
            out[nombre] = df.sort_values(col, ascending=asc).iloc[0]

    return out


def calcular_resumen_macro(df_int: pd.DataFrame):
    if df_int.empty:
        return {}

    return {
        "paises": _safe_nunique(df_int, "country"),
        "regiones": _safe_nunique(df_int, "region"),
        "benchmark_promedio": _safe_mean(df_int, "benchmark_rate_pct"),
        "inflacion_promedio": _safe_mean(df_int, "inflation_yoy_pct"),
        "tasa_real_proxy_promedio": _safe_mean(df_int, "real_rate_proxy_pct"),
        "policy_rate_promedio": _safe_mean(df_int, "policy_rate_pct"),
        "pct_con_garantia": _safe_pct(df_int["guarantee_exists"].fillna(0) == 1) if "guarantee_exists" in df_int.columns else np.nan,
    }


def obtener_fila_paraguay(df_int: pd.DataFrame):
    if "country" not in df_int.columns:
        return pd.DataFrame()
    return df_int[df_int["country"].astype(str).str.upper() == "PARAGUAY"].copy()
