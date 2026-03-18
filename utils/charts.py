import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _validar_columnas(df, columnas):
    return all(col in df.columns for col in columnas)


def grafico_top_ranking(df, score_col, nombre_col="entity_name", top_n=10, titulo=None, color_col=None):
    if df.empty or score_col not in df.columns or nombre_col not in df.columns:
        return None

    cols = [nombre_col, score_col]
    if color_col and color_col in df.columns:
        cols.append(color_col)

    plot_df = (
        df[cols]
        .dropna(subset=[nombre_col, score_col])
        .sort_values(score_col, ascending=False)
        .head(top_n)
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


def grafico_distribucion_tasas(df, col="rate_nominal_pct", titulo="Distribución de tasas nominales", color_col=None):
    if col not in df.columns:
        return None

    cols = [col]
    if color_col and color_col in df.columns:
        cols.append(color_col)

    plot_df = df[cols].dropna(subset=[col]).copy()
    if plot_df.empty:
        return None

    fig = px.histogram(
        plot_df,
        x=col,
        color=color_col if color_col in plot_df.columns else None,
        nbins=20,
        marginal="box",
        title=titulo,
        barmode="overlay"
    )
    fig.update_layout(height=460, xaxis_title="Tasa (%)", yaxis_title="Frecuencia")
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


def grafico_tasa_promedio_por_tipo(df, tipo_col="entity_type", valor_col="rate_nominal_pct", titulo="Tasa nominal promedio por tipo"):
    if not _validar_columnas(df, [tipo_col, valor_col]):
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
    fig.update_layout(height=430, xaxis_title="", yaxis_title="Promedio")
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

    plot_cols = [x_col, y_col]
    for c in [color_col, size_col, hover_name, "instrument_name", "currency_code", "term_profile"]:
        if c in df.columns:
            plot_cols.append(c)

    plot_df = df[plot_cols].dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return None

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in plot_df.columns else None,
        size=size_col if size_col in plot_df.columns else None,
        hover_name=hover_name if hover_name in plot_df.columns else None,
        hover_data=[c for c in ["instrument_name", "currency_code", "term_profile"] if c in plot_df.columns],
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

    cols = [x_col, y_col]
    for c in [color_col, hover_name, "currency_code", "term_profile"]:
        if c in df.columns:
            cols.append(c)

    plot_df = df[cols].dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return None

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in plot_df.columns else None,
        hover_name=hover_name if hover_name in plot_df.columns else None,
        hover_data=[c for c in ["currency_code", "term_profile"] if c in plot_df.columns],
        trendline="ols",
        title=titulo
    )
    fig.update_layout(height=500, xaxis_title="Plazo mínimo (días)", yaxis_title="Tasa nominal (%)")
    return fig


def grafico_boxplot_por_categoria(
    df,
    categoria_col,
    valor_col,
    titulo=None
):
    if not _validar_columnas(df, [categoria_col, valor_col]):
        return None

    plot_df = df[[categoria_col, valor_col]].dropna()
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


def grafico_matriz_riesgo_atractivo(df, risk_col="categoria_riesgo", atr_col="categoria_atractivo", titulo="Matriz riesgo vs atractivo"):
    if not _validar_columnas(df, [risk_col, atr_col]):
        return None

    pivot = (
        df.groupby([risk_col, atr_col])
        .size()
        .reset_index(name="registros")
        .pivot(index=risk_col, columns=atr_col, values="registros")
        .fillna(0)
    )

    if pivot.empty:
        return None

    orden_riesgo = [x for x in ["Bajo", "Medio", "Alto", "No disponible"] if x in pivot.index]
    orden_atr = [x for x in ["Bajo", "Medio", "Alto", "No disponible"] if x in pivot.columns]

    pivot = pivot.reindex(index=orden_riesgo, columns=orden_atr)

    fig = px.imshow(
        pivot,
        text_auto=True,
        aspect="auto",
        title=titulo
    )
    fig.update_layout(height=420)
    return fig


def grafico_tasa_real_por_pais(df, country_col="country", valor_col="real_rate_proxy_pct", top_n=15, titulo="Comparativa internacional por tasa real proxy"):
    if not _validar_columnas(df, [country_col, valor_col]):
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
    fig.update_layout(height=500, xaxis_title="Tasa real proxy (%)", yaxis_title="")
    return fig


def grafico_resumen_regional(df, region_col="region", valor_col="real_rate_proxy_pct", titulo="Promedio regional de tasa real proxy"):
    if not _validar_columnas(df, [region_col, valor_col]):
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
    fig.update_layout(height=430, xaxis_title="", yaxis_title="Promedio")
    return fig


def grafico_benchmark_vs_inflacion(df, x_col="inflation_yoy_pct", y_col="benchmark_rate_pct", hover_name="country", color_col="region", titulo="Benchmark vs inflación"):
    if not _validar_columnas(df, [x_col, y_col]):
        return None

    cols = [x_col, y_col]
    for c in [hover_name, color_col, "real_rate_proxy_pct"]:
        if c in df.columns:
            cols.append(c)

    plot_df = df[cols].dropna(subset=[x_col, y_col]).copy()
    if plot_df.empty:
        return None

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_col if color_col in plot_df.columns else None,
        hover_name=hover_name if hover_name in plot_df.columns else None,
        size="real_rate_proxy_pct" if "real_rate_proxy_pct" in plot_df.columns else None,
        title=titulo
    )
    fig.add_shape(
        type="line",
        x0=plot_df[x_col].min(),
        y0=plot_df[x_col].min(),
        x1=plot_df[x_col].max(),
        y1=plot_df[x_col].max(),
        line=dict(dash="dash")
    )
    fig.update_layout(height=500, xaxis_title="Inflación (%)", yaxis_title="Benchmark (%)")
    return fig


def grafico_radar_comparador(df_comp, categorias=None, nombre_col="entity_name", titulo="Comparación multidimensional"):
    if df_comp.empty or nombre_col not in df_comp.columns:
        return None

    categorias = categorias or [
        "real_return_score_100",
        "safety_score_100",
        "flexibility_score_100",
        "accessibility_score_100",
        "market_timing_score_100"
    ]
    categorias = [c for c in categorias if c in df_comp.columns]

    if not categorias:
        return None

    fig = go.Figure()

    for _, row in df_comp.iterrows():
        valores = [row[c] if pd.notna(row[c]) else 0 for c in categorias]
        fig.add_trace(
            go.Scatterpolar(
                r=valores + [valores[0]],
                theta=categorias + [categorias[0]],
                fill="toself",
                name=row[nombre_col]
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=titulo,
        height=520
    )
    return fig


def grafico_barras_scores_comparador(df_comp, nombre_col="entity_name", columnas=None, titulo="Scores comparados"):
    if df_comp.empty or nombre_col not in df_comp.columns:
        return None

    columnas = columnas or [
        "final_score_conservative",
        "final_score_balanced",
        "final_score_aggressive"
    ]
    columnas = [c for c in columnas if c in df_comp.columns]
    if not columnas:
        return None

    plot_df = df_comp[[nombre_col] + columnas].copy()
    plot_df = plot_df.melt(id_vars=nombre_col, var_name="score_tipo", value_name="score")
    plot_df = plot_df.dropna(subset=["score"])

    if plot_df.empty:
        return None

    fig = px.bar(
        plot_df,
        x=nombre_col,
        y="score",
        color="score_tipo",
        barmode="group",
        title=titulo,
        text_auto=".2f"
    )
    fig.update_layout(height=480, xaxis_title="", yaxis_title="Score")
    return fig
