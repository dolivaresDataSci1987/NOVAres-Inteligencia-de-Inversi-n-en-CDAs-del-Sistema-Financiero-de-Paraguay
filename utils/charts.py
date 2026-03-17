import plotly.express as px


def grafico_top_ranking(df, score_col, nombre_col="entity_name", top_n=10, titulo=None):
    if df.empty or score_col not in df.columns or nombre_col not in df.columns:
        return None

    plot_df = (
        df[[nombre_col, score_col]]
        .dropna()
        .sort_values(score_col, ascending=False)
        .head(top_n)
    )

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df.sort_values(score_col, ascending=True),
        x=score_col,
        y=nombre_col,
        orientation="h",
        title=titulo or f"Top {top_n} por {score_col}",
        text_auto=".2f"
    )

    fig.update_layout(
        xaxis_title="Score",
        yaxis_title="Entidad",
        height=450
    )
    return fig


def grafico_riesgo_retorno(
    df,
    x_col="risk_score",
    y_col="real_rate_pct",
    color_col="entity_type",
    hover_name="entity_name",
    titulo="Riesgo vs retorno real"
):
    for col in [x_col, y_col]:
        if col not in df.columns:
            return None

    plot_cols = [x_col, y_col]
    if color_col in df.columns:
        plot_cols.append(color_col)
    if hover_name in df.columns:
        plot_cols.append(hover_name)

    plot_df = df[plot_cols].dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return None

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in plot_df.columns else None,
        hover_name=hover_name if hover_name in plot_df.columns else None,
        title=titulo
    )

    fig.update_layout(
        xaxis_title="Riesgo",
        yaxis_title="Tasa real (%)",
        height=500
    )
    return fig


def grafico_tasa_promedio_por_tipo(
    df,
    tipo_col="entity_type",
    valor_col="rate_nominal_pct",
    titulo="Tasa nominal promedio por tipo de entidad"
):
    if tipo_col not in df.columns or valor_col not in df.columns:
        return None

    plot_df = (
        df[[tipo_col, valor_col]]
        .dropna()
        .groupby(tipo_col, as_index=False)
        .mean()
        .sort_values(valor_col, ascending=False)
    )

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df,
        x=tipo_col,
        y=valor_col,
        title=titulo,
        text_auto=".2f"
    )

    fig.update_layout(
        xaxis_title="Tipo de entidad",
        yaxis_title="Valor promedio",
        height=450
    )
    return fig


def grafico_score_por_tipo(
    df,
    tipo_col="entity_type",
    score_col="final_score_balanced",
    titulo="Score promedio por tipo de entidad"
):
    if tipo_col not in df.columns or score_col not in df.columns:
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

    fig.update_layout(
        xaxis_title="Tipo de entidad",
        yaxis_title="Score promedio",
        height=450
    )
    return fig


def grafico_tasa_real_por_pais(
    df,
    country_col="country",
    valor_col="real_rate_proxy_pct",
    top_n=15,
    titulo="Comparativa internacional por tasa real proxy"
):
    if country_col not in df.columns or valor_col not in df.columns:
        return None

    plot_df = (
        df[[country_col, valor_col]]
        .dropna()
        .sort_values(valor_col, ascending=False)
        .head(top_n)
    )

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df.sort_values(valor_col, ascending=True),
        x=valor_col,
        y=country_col,
        orientation="h",
        title=titulo,
        text_auto=".2f"
    )

    fig.update_layout(
        xaxis_title="Tasa real proxy (%)",
        yaxis_title="País",
        height=550
    )
    return fig


def grafico_resumen_regional(
    df,
    region_col="region",
    valor_col="real_rate_proxy_pct",
    titulo="Promedio regional de tasa real proxy"
):
    if region_col not in df.columns or valor_col not in df.columns:
        return None

    plot_df = (
        df[[region_col, valor_col]]
        .dropna()
        .groupby(region_col, as_index=False)
        .mean()
        .sort_values(valor_col, ascending=False)
    )

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df,
        x=region_col,
        y=valor_col,
        title=titulo,
        text_auto=".2f"
    )

    fig.update_layout(
        xaxis_title="Región",
        yaxis_title="Promedio",
        height=450
    )
    return fig


def grafico_distribucion_tasas(
    df,
    col="rate_nominal_pct",
    titulo="Distribución de tasas nominales"
):
    if col not in df.columns:
        return None

    plot_df = df[[col]].dropna().copy()
    if plot_df.empty:
        return None

    fig = px.histogram(
        plot_df,
        x=col,
        nbins=20,
        title=titulo
    )

    fig.update_layout(
        xaxis_title="Tasa (%)",
        yaxis_title="Frecuencia",
        height=450
    )
    return fig
