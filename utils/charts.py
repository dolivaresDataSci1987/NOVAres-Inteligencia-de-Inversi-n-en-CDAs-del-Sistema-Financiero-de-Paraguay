import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _validar_columnas(df, columnas):
    return all(col in df.columns for col in columnas)


def _columnas_unicas(columnas):
    seen = set()
    out = []
    for col in columnas:
        if col and col not in seen:
            out.append(col)
            seen.add(col)
    return out


def grafico_top_ranking(df, score_col, nombre_col="entity_name", top_n=10, titulo=None, color_col=None):
    if df.empty or score_col not in df.columns or nombre_col not in df.columns:
        return None

    cols = _columnas_unicas([nombre_col, score_col, color_col if color_col in df.columns else None])

    plot_df = (
        df[cols]
        .dropna(subset=[nombre_col, score_col])
        .sort_values(score_col, ascending=False)
        .head(top_n)
        .copy()
    )

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df.sort_values(score_col, ascending=True),
        x=score_col,
        y=nombre_col,
        color=color_col if color_col in plot_df.columns else None,
        orientation="h",
        title=titulo or f"Top {top_n} por {score_col}",
        text_auto=".2f"
    )
    fig.update_layout(height=480, xaxis_title="Score", yaxis_title="")
    return fig


def grafico_score_por_tipo(df, tipo_col="entity_type", score_col="final_score_balanced", titulo="Score promedio por tipo"):
    if not _validar_columnas(df, [tipo_col, score_col]):
        return None

    plot_df = (
        df[[tipo_col, score_col]]
        .dropna()
        .groupby(tipo_col, as_index=False)
        .mean()
        .sort_values(score_col, ascending=False)
    )

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df,
        x=tipo_col,
        y=score_col,
        title=titulo,
        text_auto=".2f"
    )
    fig.update_layout(height=430, xaxis_title="", yaxis_title="Score promedio")
    return fig


def grafico_riesgo_retorno(
    df,
    x_col="risk_score",
    y_col="real_rate_pct",
    color_col="entity_type",
    size_col="final_score_balanced",
    hover_name="entity_name",
    titulo="Mapa riesgo vs retorno real"
):
    required = [x_col, y_col]
    if not _validar_columnas(df, required):
        return None

    plot_cols = _columnas_unicas([
        x_col,
        y_col,
        color_col if color_col in df.columns else None,
        size_col if size_col in df.columns else None,
        hover_name if hover_name in df.columns else None,
        "instrument_name" if "instrument_name" in df.columns else None,
        "term_profile" if "term_profile" in df.columns else None,
        "interest_payment_frequency" if "interest_payment_frequency" in df.columns else None,
    ])

    plot_df = df[plot_cols].dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return None

    hover_data_cols = [
        c for c in ["instrument_name", "term_profile", "interest_payment_frequency"]
        if c in plot_df.columns and c != hover_name
    ]

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in plot_df.columns else None,
        size=size_col if size_col in plot_df.columns else None,
        hover_name=hover_name if hover_name in plot_df.columns else None,
        hover_data=hover_data_cols,
        title=titulo
    )

    fig.add_vline(x=plot_df[x_col].median(), line_dash="dash")
    fig.add_hline(y=plot_df[y_col].median(), line_dash="dash")
    fig.update_layout(height=520, xaxis_title="Riesgo", yaxis_title="Tasa real (%)")
    return fig


def grafico_plazo_vs_tasa(
    df,
    x_col="term_days_floor",
    y_col="rate_nominal_pct",
    color_col="entity_type",
    hover_name="entity_name",
    titulo="Plazo vs tasa nominal"
):
    if not _validar_columnas(df, [x_col, y_col]):
        return None

    cols = _columnas_unicas([
        x_col,
        y_col,
        color_col if color_col in df.columns else None,
        hover_name if hover_name in df.columns else None,
        "term_profile" if "term_profile" in df.columns else None,
        "interest_payment_frequency" if "interest_payment_frequency" in df.columns else None,
    ])

    plot_df = df[cols].dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return None

    hover_data_cols = [
        c for c in ["term_profile", "interest_payment_frequency"]
        if c in plot_df.columns and c != hover_name
    ]

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in plot_df.columns else None,
        hover_name=hover_name if hover_name in plot_df.columns else None,
        hover_data=hover_data_cols,
        title=titulo
    )

    fig.update_layout(height=500, xaxis_title="Plazo mínimo (días)", yaxis_title="Tasa nominal (%)")
    return fig


def grafico_boxplot_por_categoria(df, categoria_col, valor_col, titulo=None):
    if not _validar_columnas(df, [categoria_col, valor_col]):
        return None

    plot_df = df[[categoria_col, valor_col]].dropna().copy()
    if plot_df.empty:
        return None

    fig = px.box(
        plot_df,
        x=categoria_col,
        y=valor_col,
        points="all",
        title=titulo or f"{valor_col} por {categoria_col}"
    )
    fig.update_layout(height=470, xaxis_title="", yaxis_title=valor_col)
    return fig


def grafico_barras_por_categoria(df, categoria_col, valor_col, titulo=None):
    if not _validar_columnas(df, [categoria_col, valor_col]):
        return None

    plot_df = (
        df[[categoria_col, valor_col]]
        .dropna()
        .groupby(categoria_col, as_index=False)
        .mean()
        .sort_values(valor_col, ascending=False)
    )
    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df,
        x=categoria_col,
        y=valor_col,
        title=titulo or f"{valor_col} promedio por {categoria_col}",
        text_auto=".2f"
    )
    fig.update_layout(height=430, xaxis_title="", yaxis_title=valor_col)
    return fig


def grafico_conteo_categoria(df, categoria_col, titulo=None):
    if categoria_col not in df.columns:
        return None

    plot_df = (
        df[categoria_col]
        .dropna()
        .value_counts()
        .rename_axis(categoria_col)
        .reset_index(name="registros")
    )
    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df,
        x=categoria_col,
        y="registros",
        title=titulo or f"Distribución por {categoria_col}",
        text_auto=True
    )
    fig.update_layout(height=430, xaxis_title="", yaxis_title="Registros")
    return fig


def grafico_heatmap_promedios(df, row_col, col_col, value_col, titulo=None):
    if not _validar_columnas(df, [row_col, col_col, value_col]):
        return None

    pivot = (
        df[[row_col, col_col, value_col]]
        .dropna()
        .pivot_table(index=row_col, columns=col_col, values=value_col, aggfunc="mean")
    )

    if pivot.empty:
        return None

    fig = px.imshow(
        pivot,
        text_auto=".2f",
        aspect="auto",
        title=titulo or f"Heatmap de {value_col}"
    )
    fig.update_layout(height=480)
    return fig


def grafico_tasa_nominal_por_plazo(df, plazo_col="term_profile", tasa_col="rate_nominal_pct", titulo="Tasa nominal por perfil de plazo"):
    if not _validar_columnas(df, [plazo_col, tasa_col]):
        return None

    plot_df = df[[plazo_col, tasa_col]].dropna().copy()
    if plot_df.empty:
        return None

    fig = px.box(
        plot_df,
        x=plazo_col,
        y=tasa_col,
        points="all",
        title=titulo
    )
    fig.update_layout(height=470, xaxis_title="", yaxis_title="Tasa nominal (%)")
    return fig
