# NOVAres · Inteligencia de Inversión en CDAs del Sistema Financiero de Paraguay

## 📊 Descripción

Este proyecto desarrolla una plataforma analítica orientada al pequeño inversor para identificar las mejores oportunidades de inversión en Certificados de Depósito de Ahorro (CDAs) en Paraguay.

A diferencia de los enfoques tradicionales centrados únicamente en la tasa de interés, esta herramienta integra múltiples dimensiones clave para la toma de decisiones:

* Rentabilidad (tasas nominales y reales ajustadas por inflación)
* Riesgo del emisor (liquidez, solvencia, morosidad y perfil institucional)
* Condiciones contractuales (flexibilidad, penalizaciones y accesibilidad)
* Contexto macroeconómico (inflación, política monetaria y condiciones del sistema financiero)

El resultado es un sistema de evaluación que permite comparar CDAs de distintas entidades bajo un enfoque de **rentabilidad ajustada a riesgo**, proporcionando recomendaciones adaptadas a diferentes perfiles de inversor.

---

## 🎯 Objetivo

Proporcionar una herramienta clara, estructurada y basada en datos que permita responder:

1. ¿Qué CDA ofrece la mejor rentabilidad real?
2. ¿Qué entidad presenta menor riesgo relativo?
3. ¿Es un buen momento para invertir en CDAs?

---

## 🧠 Enfoque metodológico

El proyecto combina múltiples datasets:

* Datos de tasas de CDAs (bancos y financieras)
* Perfil de riesgo de entidades (modelo proxy)
* Condiciones contractuales de los productos (modelo proxy)
* Indicadores macroeconómicos del sistema financiero

A partir de estos datos se construyen:

* Scores de rentabilidad
* Scores de riesgo
* Scores de flexibilidad
* Indicadores de timing de mercado

Finalmente, se generan:

* Score conservador
* Score balanceado
* Score agresivo

---

## 📂 Estructura del proyecto

```bash
cda-paraguay-dashboard/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── cda_master_dashboard.csv
│   ├── cda_master_dashboard_dictionary.csv
│   └── comparativa_cda_internacional_v2.csv
│
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Ranking.py
│   ├── 3_Comparator.py
│   ├── 4_Risk_Analysis.py
│   └── 5_Macro_Context.py
│
└── utils/
    ├── load_data.py
    ├── scoring.py
    └── charts.py
```

---

## 🚀 Aplicación

El repositorio alimenta un dashboard interactivo desarrollado en **Streamlit**, que permite:

* Explorar el mercado de CDAs
* Comparar productos entre entidades
* Filtrar por plazo, riesgo y perfil de inversor
* Identificar las mejores oportunidades de inversión
* Analizar el contexto macroeconómico

---

## ⚠️ Nota metodológica

Algunos componentes del modelo (riesgo del emisor y condiciones contractuales) se basan en aproximaciones y proxies debido a la limitada disponibilidad de datos públicos estructurados a nivel de entidad.

---

## 🔒 Aviso legal

Este proyecto es propiedad intelectual de NOVAres.

Todo el código, datasets, metodologías de scoring y modelos analíticos contenidos en este repositorio son de carácter propietario.

Queda estrictamente prohibido el uso, reproducción o distribución total o parcial sin autorización expresa.

---

## 🧾 Licencia

All rights reserved © 2026 NOVAres

