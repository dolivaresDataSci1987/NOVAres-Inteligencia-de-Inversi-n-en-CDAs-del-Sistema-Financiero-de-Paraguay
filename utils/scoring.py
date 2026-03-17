import pandas as pd
import numpy as np


# =========================
# FUNCIONES AUXILIARES
# =========================
def limitar_0_100(serie):
    """
    Limita una serie al rango 0-100.
    """
    return serie.clip(lower=0, upper=100)


def normalizar_minmax_0_100(serie):
    """
    Normaliza una serie al rango 0-100.
    Si todos los valores son iguales, devuelve 50.
    """
    serie = pd.to_numeric(serie, errors="coerce")

    if serie.dropna().empty:
        return pd.Series(np.nan, index=serie.index)

    minimo = serie.min()
    maximo = serie.max()

    if pd.isna(minimo) or pd.isna(maximo):
        return pd.Series(np.nan, index=serie.index)

    if maximo == minimo:
        return pd.Series(50, index=serie.index)

    return ((serie - minimo) / (maximo - minimo)) * 100


def normalizar_inversa_0_100(serie):
    """
    Normalización inversa 0-100.
    Útil para variables donde un valor menor es mejor, como riesgo.
    """
    base = normalizar_minmax_0_100(serie)
    return 100 - base


# =========================
# CATEGORIZACIONES
# =========================
def categorizar_riesgo(risk_score):
    """
    Clasificación simple del riesgo.
    """
    if pd.isna(risk_score):
        return "No disponible"
    if risk_score <= 33:
        return "Bajo"
    if risk_score <= 66:
        return "Medio"
    return "Alto"


def categorizar_atractivo(score):
    """
    Clasificación simple del atractivo.
    """
    if pd.isna(score):
        return "No disponible"
    if score <= 40:
        return "Bajo"
    if score <= 70:
        return "Medio"
    return "Alto"


def categorizar_plazo(dias):
    """
    Categorización simple por plazo.
    """
    if pd.isna(dias):
        return "No disponible"
    if dias <= 180:
        return "Corto"
    if dias <= 365:
        return "Medio"
    return "Largo"


# =========================
# SCORING REUTILIZABLE
# =========================
def calcular_score_conservador(df):
    """
    Cálculo aproximado de score conservador
    si necesitas recalcularlo desde columnas base.
    """
    df = df.copy()

    safety = pd.to_numeric(df.get("safety_score_100"), errors="coerce")
    liquidity = pd.to_numeric(df.get("liquidity_score"), errors="coerce")
    accessibility = pd.to_numeric(df.get("accessibility_score_100"), errors="coerce")
    real_return = pd.to_numeric(df.get("real_return_score_100"), errors="coerce")

    score = (
        0.40 * safety +
        0.25 * liquidity +
        0.20 * accessibility +
        0.15 * real_return
    )

    return limitar_0_100(score)


def calcular_score_balanceado(df):
    """
    Cálculo aproximado de score balanceado.
    """
    df = df.copy()

    safety = pd.to_numeric(df.get("safety_score_100"), errors="coerce")
    real_return = pd.to_numeric(df.get("real_return_score_100"), errors="coerce")
    liquidity = pd.to_numeric(df.get("liquidity_score"), errors="coerce")
    flexibility = pd.to_numeric(df.get("flexibility_score_100"), errors="coerce")
    timing = pd.to_numeric(df.get("market_timing_score_100"), errors="coerce")

    score = (
        0.25 * safety +
        0.30 * real_return +
        0.20 * liquidity +
        0.10 * flexibility +
        0.15 * timing
    )

    return limitar_0_100(score)


def calcular_score_agresivo(df):
    """
    Cálculo aproximado de score agresivo.
    """
    df = df.copy()

    nominal_return = pd.to_numeric(df.get("nominal_return_score_100"), errors="coerce")
    real_return = pd.to_numeric(df.get("real_return_score_100"), errors="coerce")
    timing = pd.to_numeric(df.get("market_timing_score_100"), errors="coerce")
    safety = pd.to_numeric(df.get("safety_score_100"), errors="coerce")

    score = (
        0.35 * nominal_return +
        0.35 * real_return +
        0.20 * timing +
        0.10 * safety
    )

    return limitar_0_100(score)


def enriquecer_scoring(df):
    """
    Añade columnas auxiliares de categorización y,
    si faltan, intenta generar scores básicos.
    """
    df = df.copy()

    if "risk_score" in df.columns:
        df["categoria_riesgo"] = df["risk_score"].apply(categorizar_riesgo)

    if "term_days_floor" in df.columns:
        df["categoria_plazo"] = df["term_days_floor"].apply(categorizar_plazo)

    if "final_score_balanced" in df.columns:
        df["categoria_atractivo"] = df["final_score_balanced"].apply(categorizar_atractivo)

    if "final_score_conservative" not in df.columns:
        df["final_score_conservative"] = calcular_score_conservador(df)

    if "final_score_balanced" not in df.columns:
        df["final_score_balanced"] = calcular_score_balanceado(df)

    if "final_score_aggressive" not in df.columns:
        df["final_score_aggressive"] = calcular_score_agresivo(df)

    return df
