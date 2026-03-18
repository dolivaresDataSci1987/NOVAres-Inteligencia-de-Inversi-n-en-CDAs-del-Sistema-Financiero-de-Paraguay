import pandas as pd
import numpy as np


def _fmt_pct(x):
    if pd.isna(x):
        return "N/D"
    return f"{x:.2f}%"


def _fmt_num(x):
    if pd.isna(x):
        return "N/D"
    return f"{x:.2f}"


def generar_insight_overview(df: pd.DataFrame):
    if df.empty:
        return "No hay datos suficientes para generar una lectura ejecutiva."

    partes = []

    if "real_rate_pct" in df.columns:
        pct_real_positiva = (df["real_rate_pct"].fillna(-999) > 0).mean() * 100
        partes.append(
            f"El **{pct_real_positiva:.1f}%** del universo filtrado presenta **tasa real positiva**."
        )

    if "final_score_balanced" in df.columns and "entity_type" in df.columns:
        resumen = (
            df.groupby("entity_type", as_index=False)["final_score_balanced"]
            .mean()
            .sort_values("final_score_balanced", ascending=False)
        )
        if not resumen.empty:
            top_tipo = resumen.iloc[0]
            partes.append(
                f"El tipo de entidad con mejor **score balanceado promedio** es "
                f"**{top_tipo['entity_type']}** ({top_tipo['final_score_balanced']:.2f})."
            )

    if "term_profile" in df.columns and "rate_nominal_pct" in df.columns:
        resumen_plazo = (
            df.groupby("term_profile", as_index=False)["rate_nominal_pct"]
            .mean()
            .sort_values("rate_nominal_pct", ascending=False)
        )
        if not resumen_plazo.empty:
            top_plazo = resumen_plazo.iloc[0]
            partes.append(
                f"El perfil de plazo con mayor **tasa nominal promedio** es "
                f"**{top_plazo['term_profile']}** ({top_plazo['rate_nominal_pct']:.2f}%)."
            )

    if "min_amount" in df.columns and "final_score_balanced" in df.columns:
        corr = df[["min_amount", "final_score_balanced"]].dropna().corr().iloc[0, 1]
        if pd.notna(corr):
            if corr > 0.20:
                partes.append(
                    "Se observa una relación positiva moderada entre **monto mínimo** y **score balanceado**, "
                    "lo que sugiere que parte de las mejores oportunidades exigen mayor barrera de entrada."
                )
            elif corr < -0.20:
                partes.append(
                    "El universo no sugiere que exigir mayor monto mínimo mejore el score; "
                    "hay señales de oportunidades competitivas también en tramos más accesibles."
                )

    return " ".join(partes) if partes else "El mercado muestra señales mixtas y conviene leerlo por segmentos."


def generar_insight_ranking(df: pd.DataFrame, perfil: str, score_col: str):
    if df.empty or score_col not in df.columns:
        return "No hay datos suficientes para generar insight del ranking."

    top = df.sort_values(score_col, ascending=False).iloc[0]
    media = df[score_col].mean()

    partes = [
        f"La mejor oportunidad para perfil **{perfil.lower()}** es **{top.get('entity_name', 'N/D')}** "
        f"con un score de **{top.get(score_col, np.nan):.2f}**, frente a una media filtrada de **{media:.2f}**."
    ]

    if "real_rate_pct" in top.index:
        partes.append(
            f"Su **tasa real** es **{top.get('real_rate_pct', np.nan):.2f}%**"
        )

    if "risk_score" in top.index:
        partes.append(
            f"y su **riesgo** se sitúa en **{top.get('risk_score', np.nan):.2f}**."
        )

    if "recommendation_tag" in top.index and pd.notna(top.get("recommendation_tag")):
        partes.append(
            f"La etiqueta metodológica asignada es **{top.get('recommendation_tag')}**."
        )

    return " ".join(partes)


def generar_insight_comparator(df_comp: pd.DataFrame):
    if df_comp.empty:
        return "No hay suficientes opciones seleccionadas para generar una conclusión comparativa."

    partes = []

    if "final_score_balanced" in df_comp.columns:
        top_bal = df_comp.sort_values("final_score_balanced", ascending=False).iloc[0]
        partes.append(
            f"**{top_bal.get('entity_name', 'N/D')}** lidera en **equilibrio general** "
            f"con un score balanceado de **{top_bal.get('final_score_balanced', np.nan):.2f}**."
        )

    if "rate_nominal_pct" in df_comp.columns:
        top_nom = df_comp.sort_values("rate_nominal_pct", ascending=False).iloc[0]
        partes.append(
            f"**{top_nom.get('entity_name', 'N/D')}** domina en **rentabilidad nominal** "
            f"({top_nom.get('rate_nominal_pct', np.nan):.2f}%)."
        )

    if "risk_score" in df_comp.columns:
        low_risk = df_comp.sort_values("risk_score", ascending=True).iloc[0]
        partes.append(
            f"**{low_risk.get('entity_name', 'N/D')}** aparece como la opción más **defensiva** "
            f"por menor riesgo ({low_risk.get('risk_score', np.nan):.2f})."
        )

    return " ".join(partes)


def generar_insight_riesgo(df: pd.DataFrame):
    if df.empty:
        return "No hay datos suficientes para generar insight de riesgo."

    partes = []

    if {"risk_score", "real_rate_pct"}.issubset(df.columns):
        corr = df[["risk_score", "real_rate_pct"]].dropna().corr().iloc[0, 1]
        if pd.notna(corr):
            if corr > 0.25:
                partes.append(
                    "El universo sugiere un patrón donde **más riesgo tiende a asociarse con mayor retorno real**."
                )
            elif corr < -0.25:
                partes.append(
                    "El universo muestra una relación inversa: **más riesgo no está siendo compensado por mayor retorno real**."
                )
            else:
                partes.append(
                    "La relación entre **riesgo y retorno real** es débil, lo que sugiere ineficiencias y oportunidades selectivas."
                )

    if {"categoria_riesgo", "categoria_atractivo"}.issubset(df.columns):
        elite = df[
            (df["categoria_riesgo"] == "Bajo") &
            (df["categoria_atractivo"] == "Alto")
        ]
        partes.append(
            f"Se identifican **{len(elite)}** oportunidades en el cuadrante más atractivo: "
            f"**bajo riesgo + alto atractivo**."
        )

    return " ".join(partes)


def generar_insight_macro(df_int: pd.DataFrame):
    if df_int.empty:
        return "No hay datos suficientes para generar insight macro."

    partes = []

    if "real_rate_proxy_pct" in df_int.columns and "country" in df_int.columns:
        top = df_int.sort_values("real_rate_proxy_pct", ascending=False).iloc[0]
        bottom = df_int.sort_values("real_rate_proxy_pct", ascending=True).iloc[0]
        partes.append(
            f"En la comparativa internacional, **{top.get('country', 'N/D')}** lidera en tasa real proxy "
            f"({_fmt_pct(top.get('real_rate_proxy_pct'))}), mientras que **{bottom.get('country', 'N/D')}** "
            f"ocupa la peor posición relativa ({_fmt_pct(bottom.get('real_rate_proxy_pct'))})."
        )

    py = pd.DataFrame()
    if "country" in df_int.columns:
        py = df_int[df_int["country"].astype(str).str.upper() == "PARAGUAY"].copy()

    if not py.empty and "real_rate_proxy_pct" in df_int.columns:
        py_row = py.iloc[0]
        media = df_int["real_rate_proxy_pct"].mean()
        partes.append(
            f"Paraguay presenta una tasa real proxy de **{_fmt_pct(py_row.get('real_rate_proxy_pct'))}**, "
            f"frente a una media del universo comparado de **{_fmt_pct(media)}**."
        )

    return " ".join(partes)
