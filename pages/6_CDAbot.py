import streamlit as st
import pandas as pd
import plotly.express as px

from utils.load_data import cargar_datos_cda
from utils.filters import render_filtros_cda, aplicar_filtros_cda

st.set_page_config(page_title="CDAbot", page_icon="🤖", layout="wide")

# =========================================================
# CONFIG / HELPERS
# =========================================================
PROFILE_TO_SCORE = {
    "Conservador": "final_score_conservative",
    "Balanceado": "final_score_balanced",
    "Agresivo": "final_score_aggressive",
}

PROFILE_TO_RANK = {
    "Conservador": "rank_conservative",
    "Balanceado": "rank_balanced",
    "Agresivo": "rank_aggressive",
}

TERM_LABELS = {
    "short_term": "Corto plazo",
    "medium_term": "Plazo medio",
    "long_term": "Largo plazo",
}

ENTITY_LABELS = {
    "bank": "Banco",
    "finance_company": "Financiera",
    "cooperative": "Cooperativa",
}


def safe_float(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def safe_int(x, default=0):
    try:
        if pd.isna(x):
            return default
        return int(float(x))
    except Exception:
        return default


def format_pyg(x):
    if pd.isna(x):
        return "N/D"
    return f"{x:,.0f} PYG".replace(",", ".")


def format_pct(x):
    if pd.isna(x):
        return "N/D"
    return f"{x:.2f}%"


def label_term_profile(value):
    if pd.isna(value):
        return "N/D"
    return TERM_LABELS.get(str(value), str(value))


def label_entity_type(value):
    if pd.isna(value):
        return "N/D"
    return ENTITY_LABELS.get(str(value), str(value))


def build_option_label(row):
    entidad = row.get("entity_name", "Entidad")
    instrumento = row.get("instrument_name", "Instrumento")
    dias = safe_int(row.get("term_days_floor", 0))
    return f"{entidad} · {instrumento} · {dias} días"


def infer_profile(priority, risk_tolerance, liquidity_need, horizon_days):
    """
    Inferencia simple y coherente con el dashboard actual:
    no crea métricas nuevas, solo decide qué score usar.
    """
    conservative_points = 0
    aggressive_points = 0

    if priority == "Seguridad / proteger capital":
        conservative_points += 3
    elif priority == "Equilibrio":
        conservative_points += 1
        aggressive_points += 1
    elif priority == "Rentabilidad":
        aggressive_points += 3
    elif priority == "Liquidez / flexibilidad":
        conservative_points += 2

    if risk_tolerance == "Baja":
        conservative_points += 3
    elif risk_tolerance == "Media":
        conservative_points += 1
        aggressive_points += 1
    elif risk_tolerance == "Alta":
        aggressive_points += 3

    if liquidity_need == "Alta":
        conservative_points += 2
    elif liquidity_need == "Media":
        conservative_points += 1
    elif liquidity_need == "Baja":
        aggressive_points += 1

    if horizon_days <= 180:
        conservative_points += 2
    elif horizon_days <= 365:
        conservative_points += 1
        aggressive_points += 1
    else:
        aggressive_points += 2

    if conservative_points >= aggressive_points + 2:
        return "Conservador"
    elif aggressive_points >= conservative_points + 2:
        return "Agresivo"
    return "Balanceado"


def filter_by_user_profile(df, amount, horizon_days, currency, strict_horizon=True):
    out = df.copy()

    if "currency_code" in out.columns and currency != "Todas":
        out = out[out["currency_code"] == currency].copy()

    if "min_amount" in out.columns:
        out = out[out["min_amount"].fillna(0) <= amount].copy()

    if "term_days_floor" in out.columns:
        if strict_horizon:
            out = out[out["term_days_floor"].fillna(999999) <= horizon_days].copy()
        else:
            out = out[out["term_days_floor"].fillna(999999) <= int(horizon_days * 1.35)].copy()

    return out


def add_soft_fit_scores(df, liquidity_need, target_return_pct):
    """
    Ajustes suaves para ordenar mejor SIN reemplazar los scores existentes.
    Solo añade un pequeño bonus/penalización interpretativa.
    """
    out = df.copy()

    out["soft_fit_bonus"] = 0.0

    if "liquidity_score" in out.columns:
        if liquidity_need == "Alta":
            out["soft_fit_bonus"] += out["liquidity_score"].fillna(0) * 0.08
        elif liquidity_need == "Media":
            out["soft_fit_bonus"] += out["liquidity_score"].fillna(0) * 0.04
        else:
            out["soft_fit_bonus"] += 0

    if target_return_pct is not None and "real_rate_pct" in out.columns:
        diff = (out["real_rate_pct"].fillna(0) - target_return_pct).abs()
        out["target_fit_bonus"] = (10 - diff).clip(lower=-10, upper=10)
        out["soft_fit_bonus"] += out["target_fit_bonus"] * 0.6
    else:
        out["target_fit_bonus"] = 0.0

    return out


def rank_recommendations(df, inferred_profile):
    score_col = PROFILE_TO_SCORE[inferred_profile]

    out = df.copy()
    if score_col not in out.columns:
        return out, score_col

    out["cdabot_score"] = out[score_col].fillna(0) + out["soft_fit_bonus"].fillna(0)

    sort_cols = ["cdabot_score"]
    ascending = [False]

    if "real_rate_pct" in out.columns:
        sort_cols.append("real_rate_pct")
        ascending.append(False)

    out = out.sort_values(sort_cols, ascending=ascending).reset_index(drop=True)
    return out, score_col


def compute_estimated_interest(amount, annual_rate_pct, term_days):
    if pd.isna(annual_rate_pct) or pd.isna(term_days):
        return None
    return amount * (annual_rate_pct / 100) * (term_days / 365)


def build_profile_summary(amount, horizon_days, priority, liquidity_need, risk_tolerance, target_return_pct, inferred_profile):
    horizon_txt = (
        "corto plazo" if horizon_days <= 180
        else "plazo medio" if horizon_days <= 365
        else "largo plazo"
    )

    txt = (
        f"Has indicado una inversión de **{format_pyg(amount)}**, "
        f"con un horizonte máximo de **{horizon_days} días** "
        f"({horizon_txt}). Tu prioridad principal es **{priority.lower()}**, "
        f"tu necesidad de liquidez es **{liquidity_need.lower()}** "
        f"y tu tolerancia al riesgo es **{risk_tolerance.lower()}**."
    )

    if target_return_pct is not None:
        txt += f" Además, te gustaría acercarte a una rentabilidad objetivo de **{target_return_pct:.2f}%**."

    txt += f"\n\nCon estas respuestas, CDAbot interpreta que tu perfil encaja mejor con un enfoque **{inferred_profile.lower()}**."
    return txt


def build_strategy_text(inferred_profile, horizon_days, liquidity_need):
    if inferred_profile == "Conservador":
        return (
            "La estrategia sugerida es priorizar opciones con mejor equilibrio defensivo, "
            "poniendo más peso en seguridad, liquidez relativa y accesibilidad de entrada."
        )
    elif inferred_profile == "Agresivo":
        return (
            "La estrategia sugerida es priorizar opciones con mayor potencial de retorno, "
            "aceptando más plazo o menos flexibilidad si eso mejora la rentabilidad esperada."
        )
    else:
        base = (
            "La estrategia sugerida es buscar un punto medio entre retorno, seguridad y liquidez, "
            "sin perseguir únicamente la tasa más alta."
        )
        if horizon_days <= 365 and liquidity_need == "Alta":
            base += " En tu caso, conviene evitar que una tasa atractiva te obligue a inmovilizar demasiado el capital."
        return base


def build_reason_row(row, inferred_profile, amount):
    rate_nominal = safe_float(row.get("rate_nominal_pct"))
    real_rate = safe_float(row.get("real_rate_pct"))
    risk_score = safe_float(row.get("risk_score"))
    liquidity_score = safe_float(row.get("liquidity_score"))
    solvency_score = safe_float(row.get("solvency_score"))
    dias = safe_int(row.get("term_days_floor"))
    monto_min = safe_float(row.get("min_amount"))
    etiqueta = row.get("recommendation_tag", "N/D")

    razones = []

    if inferred_profile == "Conservador":
        if solvency_score >= 75:
            razones.append("muestra una solvencia relativa favorable")
        if liquidity_score >= 75:
            razones.append("mantiene una flexibilidad relativamente buena")
        if risk_score <= 40:
            razones.append("presenta un riesgo relativamente bajo")
    elif inferred_profile == "Agresivo":
        if real_rate >= 5:
            razones.append("ofrece una tasa real alta")
        if rate_nominal >= 8:
            razones.append("tiene una tasa nominal competitiva")
        if dias >= 365:
            razones.append("acepta más plazo a cambio de más retorno potencial")
    else:
        if real_rate >= 4:
            razones.append("combina una tasa real atractiva")
        if liquidity_score >= 70:
            razones.append("sin perder del todo la flexibilidad")
        if solvency_score >= 70:
            razones.append("y mantiene una base razonable de solvencia relativa")

    if monto_min <= amount:
        razones.append("entra dentro de tu monto disponible")

    if not razones:
        razones.append("encaja razonablemente con tus restricciones principales")

    texto = ", ".join(razones)
    return (
        f"**{row.get('entity_name', 'Entidad')}** encaja porque {texto}. "
        f"Su etiqueta metodológica actual es **{etiqueta}**."
    )


def build_tradeoff_text(top_df, target_return_pct, horizon_days, liquidity_need):
    if top_df.empty:
        return "No fue posible calcular trade-offs con el filtro actual."

    top = top_df.iloc[0]
    dias = safe_int(top.get("term_days_floor"))
    real_rate = safe_float(top.get("real_rate_pct"))
    risk = safe_float(top.get("risk_score"))

    msgs = []

    if target_return_pct is not None and real_rate < target_return_pct:
        msgs.append(
            "Tu objetivo de rentabilidad parece más exigente que lo que ofrecen las mejores opciones compatibles con tus filtros actuales."
        )

    if liquidity_need == "Alta" and dias > 365:
        msgs.append(
            "Para acercarte a más rentabilidad, probablemente tendrás que aceptar menos liquidez o un plazo más largo."
        )

    if horizon_days <= 180 and real_rate < 4:
        msgs.append(
            "Con horizontes cortos, el mercado suele limitar parte del retorno potencial."
        )

    if risk > 70:
        msgs.append(
            "La opción líder aparece bien posicionada por retorno, pero no es la más defensiva del universo filtrado."
        )

    if not msgs:
        msgs.append(
            "En tus condiciones actuales, el principal compromiso está entre mejorar retorno y mantener flexibilidad."
        )

    return " ".join(msgs)


def make_download_table(df_show):
    cols = [
        "entity_name",
        "entity_type",
        "instrument_name",
        "term_days_floor",
        "term_profile",
        "min_amount",
        "rate_nominal_pct",
        "real_rate_pct",
        "risk_score",
        "liquidity_score",
        "solvency_score",
        "final_score_conservative",
        "final_score_balanced",
        "final_score_aggressive",
        "cdabot_score",
        "recommendation_tag",
    ]
    cols = [c for c in cols if c in df_show.columns]
    return df_show[cols].copy()


def reset_cdabot():
    st.session_state.cdabot_step = 0
    st.session_state.cdabot_answers = {}
    st.session_state.cdabot_ready = False


# =========================================================
# SESSION STATE
# =========================================================
if "cdabot_step" not in st.session_state:
    st.session_state.cdabot_step = 0

if "cdabot_answers" not in st.session_state:
    st.session_state.cdabot_answers = {}

if "cdabot_ready" not in st.session_state:
    st.session_state.cdabot_ready = False


# =========================================================
# CARGA
# =========================================================
df = cargar_datos_cda()

if df.empty:
    st.warning("No se pudo cargar la base de CDAs.")
    st.stop()

# =========================================================
# FILTROS GENERALES DEL DASHBOARD
# =========================================================
filtros = render_filtros_cda(df, key_prefix="cdabot")
df_f = aplicar_filtros_cda(df, filtros)

if df_f.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()

df_f = df_f.copy()
df_f["opcion_label"] = df_f.apply(build_option_label, axis=1)

# =========================================================
# HEADER
# =========================================================
st.title("🤖 CDAbot")
st.markdown(
    """
    CDAbot te ayuda a traducir tus preferencias de inversión en una **selección práctica de CDAs**
    usando la misma lógica metodológica del dashboard.
    """
)
st.warning(
    """
    **AVISO:** Este dashboard tiene fines exclusivamente **informativos, analíticos y educativos**. **No constituye asesoramiento financiero, recomendación de inversión ni sustituye la evaluación profesional personalizada.**
Los datos mostrados se basan en información recopilada y procesada bajo una metodología propia de análisis. Algunas variables —como la **tasa nominal, tasa efectiva, plazo, monto mínimo u otras condiciones comerciales**—
    pueden **variar ligeramente** respecto a la oferta final vigente de cada entidad financiera en el momento de la contratación.
 Esto se debe a que las condiciones de los CDAs pueden ser **dinámicas**, estar sujetas a **actualizaciones comerciales**,
    cambios de mercado y, en algunos casos, a **negociación según el perfil del cliente, el monto invertido o el plazo pactado**.
 Antes de tomar una decisión de inversión, conviene **confirmar directamente con la entidad** las condiciones finales aplicables.
    """
)
st.info(
    "Consejo práctico: primero aplica los filtros generales del dashboard si quieres acotar el universo, "
    "y luego deja que CDAbot te ayude a priorizar."
)

st.markdown("---")

# =========================================================
# LAYOUT
# =========================================================
col_chat, col_side = st.columns([1.55, 1], gap="large")

with col_side:
    st.subheader("Resumen del perfil")
    ans = st.session_state.cdabot_answers

    if ans:
        st.write(f"**Monto objetivo:** {format_pyg(ans.get('amount'))}" if ans.get("amount") is not None else "**Monto objetivo:** N/D")
        st.write(f"**Horizonte máximo:** {ans.get('horizon_days', 'N/D')} días")
        st.write(f"**Prioridad:** {ans.get('priority', 'N/D')}")
        st.write(f"**Liquidez:** {ans.get('liquidity_need', 'N/D')}")
        st.write(f"**Riesgo:** {ans.get('risk_tolerance', 'N/D')}")
        if ans.get("target_return_pct") is not None:
            st.write(f"**Objetivo rentabilidad:** {ans.get('target_return_pct'):.2f}%")
        else:
            st.write("**Objetivo rentabilidad:** No especificado")
        st.write(f"**Perfil inferido:** {ans.get('inferred_profile', 'Aún no calculado')}")
    else:
        st.caption("Aún no has completado el diagnóstico inicial.")

    st.markdown("### Qué tiene en cuenta CDAbot")
    st.markdown(
        """
        - monto mínimo de entrada  
        - plazo máximo aceptable  
        - score por perfil  
        - liquidez relativa  
        - tasa real  
        - solvencia relativa  
        """
    )

    st.markdown("### Acciones")
    if st.button("🔄 Reiniciar diagnóstico", use_container_width=True):
        reset_cdabot()
        st.rerun()

with col_chat:
    st.subheader("Diagnóstico conversacional")

    # ---------------------------------------------
    # HISTORIAL SIMULADO
    # ---------------------------------------------
    if st.session_state.cdabot_step == 0:
        with st.chat_message("assistant"):
            st.markdown(
                "Hola, soy **CDAbot**. Voy a ayudarte a encontrar CDAs que encajen con tu estrategia. "
                "Empecemos por lo básico."
            )

    if st.session_state.cdabot_step >= 1:
        with st.chat_message("assistant"):
            st.markdown("**1.** ¿Cuánto dinero quieres invertir?")
        with st.chat_message("user"):
            st.markdown(format_pyg(st.session_state.cdabot_answers.get("amount")))

    if st.session_state.cdabot_step >= 2:
        with st.chat_message("assistant"):
            st.markdown("**2.** ¿Cuál es el plazo máximo que te sientes cómodo dejando inmovilizado el dinero?")
        with st.chat_message("user"):
            st.markdown(f"{st.session_state.cdabot_answers.get('horizon_days')} días")

    if st.session_state.cdabot_step >= 3:
        with st.chat_message("assistant"):
            st.markdown("**3.** ¿Qué priorizas más en esta inversión?")
        with st.chat_message("user"):
            st.markdown(st.session_state.cdabot_answers.get("priority"))

    if st.session_state.cdabot_step >= 4:
        with st.chat_message("assistant"):
            st.markdown("**4.** ¿Qué necesidad de liquidez tienes?")
        with st.chat_message("user"):
            st.markdown(st.session_state.cdabot_answers.get("liquidity_need"))

    if st.session_state.cdabot_step >= 5:
        with st.chat_message("assistant"):
            st.markdown("**5.** ¿Cuál es tu tolerancia al riesgo?")
        with st.chat_message("user"):
            st.markdown(st.session_state.cdabot_answers.get("risk_tolerance"))

    if st.session_state.cdabot_step >= 6:
        with st.chat_message("assistant"):
            st.markdown("**6.** ¿Tienes una rentabilidad objetivo aproximada? (opcional)")
        with st.chat_message("user"):
            val = st.session_state.cdabot_answers.get("target_return_pct")
            st.markdown(format_pct(val) if val is not None else "No tengo una concreta")

    # ---------------------------------------------
    # STEP FORMS
    # ---------------------------------------------
    if st.session_state.cdabot_step == 0:
        with st.form("cdabot_step_0"):
            amount = st.number_input(
                "Monto a invertir (PYG)",
                min_value=100000,
                value=5000000,
                step=100000,
                format="%d"
            )
            submitted = st.form_submit_button("Continuar")
            if submitted:
                st.session_state.cdabot_answers["amount"] = amount
                st.session_state.cdabot_step = 1
                st.rerun()

    elif st.session_state.cdabot_step == 1:
        with st.form("cdabot_step_1"):
            horizon_days = st.selectbox(
                "Horizonte máximo",
                options=[90, 180, 365, 540, 730, 1095],
                format_func=lambda x: f"{x} días"
            )
            submitted = st.form_submit_button("Continuar")
            if submitted:
                st.session_state.cdabot_answers["horizon_days"] = horizon_days
                st.session_state.cdabot_step = 2
                st.rerun()

    elif st.session_state.cdabot_step == 2:
        with st.form("cdabot_step_2"):
            priority = st.radio(
                "Qué priorizas más",
                options=[
                    "Seguridad / proteger capital",
                    "Equilibrio",
                    "Rentabilidad",
                    "Liquidez / flexibilidad",
                ],
                horizontal=False
            )
            submitted = st.form_submit_button("Continuar")
            if submitted:
                st.session_state.cdabot_answers["priority"] = priority
                st.session_state.cdabot_step = 3
                st.rerun()

    elif st.session_state.cdabot_step == 3:
        with st.form("cdabot_step_3"):
            liquidity_need = st.radio(
                "Necesidad de liquidez",
                options=["Alta", "Media", "Baja"],
                horizontal=True
            )
            submitted = st.form_submit_button("Continuar")
            if submitted:
                st.session_state.cdabot_answers["liquidity_need"] = liquidity_need
                st.session_state.cdabot_step = 4
                st.rerun()

    elif st.session_state.cdabot_step == 4:
        with st.form("cdabot_step_4"):
            risk_tolerance = st.radio(
                "Tolerancia al riesgo",
                options=["Baja", "Media", "Alta"],
                horizontal=True
            )
            submitted = st.form_submit_button("Continuar")
            if submitted:
                st.session_state.cdabot_answers["risk_tolerance"] = risk_tolerance
                st.session_state.cdabot_step = 5
                st.rerun()

    elif st.session_state.cdabot_step == 5:
        with st.form("cdabot_step_5"):
            wants_target = st.checkbox("Quiero indicar una rentabilidad objetivo")
            target_return_pct = None

            if wants_target:
                target_return_pct = st.number_input(
                    "Rentabilidad objetivo (%)",
                    min_value=0.0,
                    max_value=30.0,
                    value=6.0,
                    step=0.25
                )

            submitted = st.form_submit_button("Generar recomendación")
            if submitted:
                st.session_state.cdabot_answers["target_return_pct"] = target_return_pct

                inferred_profile = infer_profile(
                    priority=st.session_state.cdabot_answers["priority"],
                    risk_tolerance=st.session_state.cdabot_answers["risk_tolerance"],
                    liquidity_need=st.session_state.cdabot_answers["liquidity_need"],
                    horizon_days=st.session_state.cdabot_answers["horizon_days"],
                )
                st.session_state.cdabot_answers["inferred_profile"] = inferred_profile
                st.session_state.cdabot_step = 6
                st.session_state.cdabot_ready = True
                st.rerun()

    # ---------------------------------------------
    # OUTPUT FINAL
    # ---------------------------------------------
    if st.session_state.cdabot_ready:
        answers = st.session_state.cdabot_answers

        amount = answers["amount"]
        horizon_days = answers["horizon_days"]
        priority = answers["priority"]
        liquidity_need = answers["liquidity_need"]
        risk_tolerance = answers["risk_tolerance"]
        target_return_pct = answers.get("target_return_pct", None)
        inferred_profile = answers["inferred_profile"]

        # Intento estricto por plazo
        df_user = filter_by_user_profile(
            df=df_f,
            amount=amount,
            horizon_days=horizon_days,
            currency="Todas",
            strict_horizon=True
        )

        # Si queda vacío, relajamos un poco el plazo para no romper la experiencia
        used_relaxed_horizon = False
        if df_user.empty:
            df_user = filter_by_user_profile(
                df=df_f,
                amount=amount,
                horizon_days=horizon_days,
                currency="Todas",
                strict_horizon=False
            )
            used_relaxed_horizon = True

        # Ajustes suaves
        df_user = add_soft_fit_scores(
            df_user,
            liquidity_need=liquidity_need,
            target_return_pct=target_return_pct
        )

        # Ranking final
        df_ranked, score_col = rank_recommendations(df_user, inferred_profile)

        with st.chat_message("assistant"):
            st.markdown("Ya tengo tu diagnóstico. Aquí va la lectura estratégica:")

        st.markdown("## Tu lectura personalizada")

        st.info(
            build_profile_summary(
                amount=amount,
                horizon_days=horizon_days,
                priority=priority,
                liquidity_need=liquidity_need,
                risk_tolerance=risk_tolerance,
                target_return_pct=target_return_pct,
                inferred_profile=inferred_profile,
            )
        )

        st.success(build_strategy_text(inferred_profile, horizon_days, liquidity_need))

        if df_ranked.empty:
            st.warning(
                "No encontré opciones que encajen con tus restricciones actuales. "
                "Prueba a ampliar el horizonte, subir el monto o relajar filtros generales del dashboard."
            )
            st.stop()

        if used_relaxed_horizon:
            st.caption(
                "Nota: no había opciones dentro de tu plazo máximo exacto, así que CDAbot amplió ligeramente "
                "el rango de plazo para no dejarte sin alternativas."
            )

        # TOPS
        st.markdown("## Recomendaciones concretas")

        top_n = min(5, len(df_ranked))
        top = df_ranked.head(top_n).copy()

        cols = st.columns(top_n if top_n <= 4 else 5)

        for i, (_, row) in enumerate(top.iterrows()):
            with cols[i]:
                st.markdown(f"### #{i+1}")
                st.write(f"**Entidad:** {row.get('entity_name', 'N/D')}")
                st.write(f"**Instrumento:** {row.get('instrument_name', 'N/D')}")
                st.write(f"**Plazo:** {safe_int(row.get('term_days_floor'))} días")
                st.write(f"**Perfil de plazo:** {label_term_profile(row.get('term_profile'))}")
                st.write(f"**Tipo de entidad:** {label_entity_type(row.get('entity_type'))}")
                st.write(f"**Monto mínimo:** {format_pyg(row.get('min_amount'))}")
                st.write(f"**Tasa nominal:** {format_pct(row.get('rate_nominal_pct'))}")
                st.write(f"**Tasa real:** {format_pct(row.get('real_rate_pct'))}")
                st.write(f"**Riesgo:** {safe_float(row.get('risk_score')):.2f}")
                st.write(f"**Liquidez:** {safe_float(row.get('liquidity_score')):.2f}")
                st.write(f"**Solvencia:** {safe_float(row.get('solvency_score')):.2f}")
                st.write(f"**Score CDAbot:** {safe_float(row.get('cdabot_score')):.2f}")

        st.markdown("---")

        # RECOMENDACIÓN PRINCIPAL
        leader = df_ranked.iloc[0]
        estimated_interest = compute_estimated_interest(
            amount=amount,
            annual_rate_pct=safe_float(leader.get("rate_nominal_pct")),
            term_days=safe_int(leader.get("term_days_floor"))
        )

        st.subheader("Mejor ajuste para ti")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Entidad", leader.get("entity_name", "N/D"))
        col2.metric("Plazo", f"{safe_int(leader.get('term_days_floor'))} días")
        col3.metric("Tasa nominal", format_pct(leader.get("rate_nominal_pct")))
        col4.metric("Perfil detectado", inferred_profile)

        st.markdown(build_reason_row(leader, inferred_profile, amount))

        if estimated_interest is not None:
            st.markdown(
                f"""
                **Simulación orientativa:** si invirtieras **{format_pyg(amount)}** en esta opción y se mantuviera la
                tasa nominal de **{format_pct(leader.get('rate_nominal_pct'))}** durante
                **{safe_int(leader.get('term_days_floor'))} días**, el interés estimado sería de aproximadamente
                **{format_pyg(estimated_interest)}**.

                *Esta simulación es orientativa y simplificada; no sustituye las condiciones reales del producto.*
                """
            )

        st.markdown("---")

        # TRADE-OFFS
        st.subheader("Trade-offs que deberías tener presentes")
        st.warning(
            build_tradeoff_text(
                top_df=df_ranked.head(3),
                target_return_pct=target_return_pct,
                horizon_days=horizon_days,
                liquidity_need=liquidity_need,
            )
        )

        # ALTERNATIVAS TEMÁTICAS
        st.subheader("Alternativas útiles")

        col_a, col_b, col_c = st.columns(3)

        # más rentable compatible
        if "real_rate_pct" in df_ranked.columns:
            alt_return = df_ranked.sort_values(
                ["real_rate_pct", "cdabot_score"], ascending=[False, False]
            ).iloc[0]
            with col_a:
                st.markdown("### Alternativa más rentable")
                st.write(f"**Entidad:** {alt_return.get('entity_name', 'N/D')}")
                st.write(f"**Plazo:** {safe_int(alt_return.get('term_days_floor'))} días")
                st.write(f"**Tasa real:** {format_pct(alt_return.get('real_rate_pct'))}")
                st.write(f"**Score CDAbot:** {safe_float(alt_return.get('cdabot_score')):.2f}")

        # más líquida compatible
        if "liquidity_score" in df_ranked.columns:
            alt_liq = df_ranked.sort_values(
                ["liquidity_score", "cdabot_score"], ascending=[False, False]
            ).iloc[0]
            with col_b:
                st.markdown("### Alternativa más flexible")
                st.write(f"**Entidad:** {alt_liq.get('entity_name', 'N/D')}")
                st.write(f"**Plazo:** {safe_int(alt_liq.get('term_days_floor'))} días")
                st.write(f"**Liquidez:** {safe_float(alt_liq.get('liquidity_score')):.2f}")
                st.write(f"**Tasa nominal:** {format_pct(alt_liq.get('rate_nominal_pct'))}")

        # más defensiva compatible
        if "final_score_conservative" in df_ranked.columns:
            alt_def = df_ranked.sort_values(
                ["final_score_conservative", "cdabot_score"], ascending=[False, False]
            ).iloc[0]
            with col_c:
                st.markdown("### Alternativa más defensiva")
                st.write(f"**Entidad:** {alt_def.get('entity_name', 'N/D')}")
                st.write(f"**Plazo:** {safe_int(alt_def.get('term_days_floor'))} días")
                st.write(f"**Score conservador:** {safe_float(alt_def.get('final_score_conservative')):.2f}")
                st.write(f"**Riesgo:** {safe_float(alt_def.get('risk_score')):.2f}")

        st.markdown("---")

        # GRÁFICO
        st.subheader("Mapa visual de tus opciones compatibles")

        fig_df = df_ranked.head(20).copy()

        if {"risk_score", "real_rate_pct", "entity_type", "cdabot_score", "opcion_label"}.issubset(fig_df.columns):
            fig = px.scatter(
                fig_df,
                x="risk_score",
                y="real_rate_pct",
                color="entity_type",
                size="cdabot_score",
                hover_name="opcion_label",
                title="Tus mejores opciones compatibles según CDAbot"
            )
            fig.update_layout(
                xaxis_title="Riesgo",
                yaxis_title="Tasa real (%)",
                legend_title="Tipo de entidad"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Más arriba suele implicar mejor tasa real. El tamaño del punto resume la prioridad final de CDAbot "
            "para tu caso concreto."
        )

        st.markdown("---")

        # TABLA FINAL
        st.subheader("Tabla ejecutiva para decidir")
        tabla = make_download_table(df_ranked.head(15)).rename(columns={
            "entity_name": "Entidad",
            "entity_type": "Tipo de entidad",
            "instrument_name": "Instrumento",
            "term_days_floor": "Días",
            "term_profile": "Perfil de plazo",
            "min_amount": "Monto mínimo",
            "rate_nominal_pct": "Tasa nominal (%)",
            "real_rate_pct": "Tasa real (%)",
            "risk_score": "Riesgo",
            "liquidity_score": "Liquidez",
            "solvency_score": "Solvencia",
            "final_score_conservative": "Score conservador",
            "final_score_balanced": "Score balanceado",
            "final_score_aggressive": "Score agresivo",
            "cdabot_score": "Score CDAbot",
            "recommendation_tag": "Etiqueta",
        })

        st.dataframe(tabla, use_container_width=True)

        csv = tabla.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar tabla de recomendaciones",
            data=csv,
            file_name="cdabot_recomendaciones.csv",
            mime="text/csv",
            use_container_width=False,
        )

        st.markdown("---")

        st.subheader("Cómo leer bien esta recomendación")
        st.markdown(
            """
            - **CDAbot no sustituye una recomendación financiera profesional**: ordena y explica las mejores opciones visibles según tu perfil y tus restricciones.
            - **La mejor opción no siempre es la que más paga**, sino la que mejor encaja con tu equilibrio entre plazo, liquidez, seguridad y retorno.
            - Si cambias el monto, el plazo o la prioridad, la recomendación puede cambiar bastante.
            """
        )
