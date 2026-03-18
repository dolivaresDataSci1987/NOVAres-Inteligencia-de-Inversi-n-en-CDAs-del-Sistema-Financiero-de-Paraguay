import streamlit as st
import pandas as pd


def _safe_sorted_unique(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return []
    vals = df[col].dropna().astype(str).unique().tolist()
    return sorted(vals)


def render_filtros_cda(df: pd.DataFrame, sidebar: bool = True, key_prefix: str = "cda"):
    """
    Renderiza filtros comunes del universo CDA y devuelve un diccionario.
    """
    container = st.sidebar if sidebar else st

    container.header("Filtros")

    monedas_disponibles = _safe_sorted_unique(df, "currency_code")
    tipos_disponibles = _safe_sorted_unique(df, "entity_type")
    plazo_disponibles = _safe_sorted_unique(df, "term_profile")
    bucket_plazo_disponibles = _safe_sorted_unique(df, "term_bucket")
    size_disponibles = _safe_sorted_unique(df, "size_bucket")
    frecuencia_disponible = _safe_sorted_unique(df, "interest_payment_frequency")

    monedas = container.multiselect(
        "Moneda",
        options=monedas_disponibles,
        default=monedas_disponibles,
        key=f"{key_prefix}_monedas"
    )

    tipos_entidad = container.multiselect(
        "Tipo de entidad",
        options=tipos_disponibles,
        default=tipos_disponibles,
        key=f"{key_prefix}_tipos_entidad"
    )

    perfiles_plazo = container.multiselect(
        "Perfil de plazo",
        options=plazo_disponibles,
        default=plazo_disponibles,
        key=f"{key_prefix}_perfiles_plazo"
    )

    term_buckets = container.multiselect(
        "Bucket de plazo",
        options=bucket_plazo_disponibles,
        default=bucket_plazo_disponibles,
        key=f"{key_prefix}_term_bucket"
    )

    size_buckets = container.multiselect(
        "Tamaño de entidad",
        options=size_disponibles,
        default=size_disponibles,
        key=f"{key_prefix}_size_bucket"
    )

    interest_payment_frequency = container.multiselect(
        "Frecuencia de pago de interés",
        options=frecuencia_disponible,
        default=frecuencia_disponible,
        key=f"{key_prefix}_interest_payment_frequency"
    )

    rango_plazo = (
        int(df["term_days_floor"].min()) if "term_days_floor" in df.columns and not df["term_days_floor"].dropna().empty else 0,
        int(df["term_days_floor"].max()) if "term_days_floor" in df.columns and not df["term_days_floor"].dropna().empty else 365
    )

    plazo_dias = container.slider(
        "Rango de plazo (días)",
        min_value=rango_plazo[0],
        max_value=rango_plazo[1],
        value=rango_plazo,
        key=f"{key_prefix}_plazo_dias"
    )

    if "rate_nominal_pct" in df.columns and not df["rate_nominal_pct"].dropna().empty:
        tasa_min = float(df["rate_nominal_pct"].min())
        tasa_max = float(df["rate_nominal_pct"].max())
    else:
        tasa_min, tasa_max = 0.0, 20.0

    rango_tasa = container.slider(
        "Rango de tasa nominal (%)",
        min_value=float(round(tasa_min, 2)),
        max_value=float(round(tasa_max, 2)),
        value=(float(round(tasa_min, 2)), float(round(tasa_max, 2))),
        key=f"{key_prefix}_rango_tasa"
    )

    if "min_amount" in df.columns and not df["min_amount"].dropna().empty:
        monto_min = int(df["min_amount"].min())
        monto_max = int(df["min_amount"].max())
    else:
        monto_min, monto_max = 0, 100000000

    rango_monto = container.slider(
        "Monto mínimo requerido",
        min_value=monto_min,
        max_value=monto_max,
        value=(monto_min, monto_max),
        key=f"{key_prefix}_rango_monto"
    )

    solo_garantizados = container.checkbox(
        "Solo instrumentos con garantía",
        value=False,
        key=f"{key_prefix}_solo_garantizados"
    )

    solo_con_rescate = container.checkbox(
        "Solo instrumentos con retiro anticipado",
        value=False,
        key=f"{key_prefix}_solo_rescate"
    )

    solo_autorenovable = container.checkbox(
        "Solo instrumentos con auto renovación",
        value=False,
        key=f"{key_prefix}_solo_autorenovable"
    )

    solo_interes_compuesto = container.checkbox(
        "Solo instrumentos con interés compuesto",
        value=False,
        key=f"{key_prefix}_solo_compuesto"
    )

    return {
        "monedas": monedas,
        "tipos_entidad": tipos_entidad,
        "perfiles_plazo": perfiles_plazo,
        "term_buckets": term_buckets,
        "size_buckets": size_buckets,
        "interest_payment_frequency": interest_payment_frequency,
        "plazo_dias": plazo_dias,
        "rango_tasa": rango_tasa,
        "rango_monto": rango_monto,
        "solo_garantizados": solo_garantizados,
        "solo_con_rescate": solo_con_rescate,
        "solo_autorenovable": solo_autorenovable,
        "solo_interes_compuesto": solo_interes_compuesto,
    }


def aplicar_filtros_cda(df: pd.DataFrame, filtros: dict):
    """
    Aplica los filtros comunes del universo CDA.
    """
    df_f = df.copy()

    if filtros.get("monedas") and "currency_code" in df_f.columns:
        df_f = df_f[df_f["currency_code"].isin(filtros["monedas"])]

    if filtros.get("tipos_entidad") and "entity_type" in df_f.columns:
        df_f = df_f[df_f["entity_type"].isin(filtros["tipos_entidad"])]

    if filtros.get("perfiles_plazo") and "term_profile" in df_f.columns:
        df_f = df_f[df_f["term_profile"].isin(filtros["perfiles_plazo"])]

    if filtros.get("term_buckets") and "term_bucket" in df_f.columns:
        df_f = df_f[df_f["term_bucket"].isin(filtros["term_buckets"])]

    if filtros.get("size_buckets") and "size_bucket" in df_f.columns:
        df_f = df_f[df_f["size_bucket"].isin(filtros["size_buckets"])]

    if filtros.get("interest_payment_frequency") and "interest_payment_frequency" in df_f.columns:
        df_f = df_f[df_f["interest_payment_frequency"].isin(filtros["interest_payment_frequency"])]

    if "term_days_floor" in df_f.columns and filtros.get("plazo_dias"):
        min_d, max_d = filtros["plazo_dias"]
        df_f = df_f[df_f["term_days_floor"].between(min_d, max_d, inclusive="both")]

    if "rate_nominal_pct" in df_f.columns and filtros.get("rango_tasa"):
        min_t, max_t = filtros["rango_tasa"]
        df_f = df_f[df_f["rate_nominal_pct"].between(min_t, max_t, inclusive="both")]

    if "min_amount" in df_f.columns and filtros.get("rango_monto"):
        min_m, max_m = filtros["rango_monto"]
        df_f = df_f[df_f["min_amount"].between(min_m, max_m, inclusive="both")]

    if filtros.get("solo_garantizados") and "guarantee" in df_f.columns:
        df_f = df_f[df_f["guarantee"] == 1]

    if filtros.get("solo_con_rescate") and "withdrawal_allowed" in df_f.columns:
        df_f = df_f[df_f["withdrawal_allowed"] == 1]

    if filtros.get("solo_autorenovable") and "auto_renewal" in df_f.columns:
        df_f = df_f[df_f["auto_renewal"] == 1]

    if filtros.get("solo_interes_compuesto") and "compound_interest" in df_f.columns:
        df_f = df_f[df_f["compound_interest"] == 1]

    return df_f


def render_filtros_macro(df_int: pd.DataFrame, sidebar: bool = True, key_prefix: str = "macro"):
    container = st.sidebar if sidebar else st
    container.header("Filtros")

    regiones = sorted(df_int["region"].dropna().astype(str).unique()) if "region" in df_int.columns else []
    riesgos = sorted(df_int["market_risk_tier"].dropna().astype(str).unique()) if "market_risk_tier" in df_int.columns else []

    regiones_sel = container.multiselect(
        "Región",
        options=regiones,
        default=regiones,
        key=f"{key_prefix}_regiones"
    )

    riesgos_sel = container.multiselect(
        "Tier de riesgo",
        options=riesgos,
        default=riesgos,
        key=f"{key_prefix}_riesgos"
    )

    solo_con_garantia = container.checkbox(
        "Solo países con garantía de depósitos",
        value=False,
        key=f"{key_prefix}_solo_garantia"
    )

    return {
        "regiones": regiones_sel,
        "riesgos": riesgos_sel,
        "solo_con_garantia": solo_con_garantia
    }


def aplicar_filtros_macro(df_int: pd.DataFrame, filtros: dict):
    df_f = df_int.copy()

    if filtros.get("regiones") and "region" in df_f.columns:
        df_f = df_f[df_f["region"].isin(filtros["regiones"])]

    if filtros.get("riesgos") and "market_risk_tier" in df_f.columns:
        df_f = df_f[df_f["market_risk_tier"].isin(filtros["riesgos"])]

    if filtros.get("solo_con_garantia") and "guarantee_exists" in df_f.columns:
        df_f = df_f[df_f["guarantee_exists"] == 1]

    return df_f
